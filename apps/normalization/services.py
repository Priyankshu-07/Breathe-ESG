from decimal import Decimal, InvalidOperation
from datetime import date
from apps.ingestion.models import IngestionRow
from apps.emissions.models import NormalizedEmission
from apps.normalization.unit_converter import to_kwh, to_litres, to_kg, to_km, UnitConversionError
from apps.normalization.date_normalizer import parse_date, billing_period_to_range, DateParseError
from apps.normalization.plant_mapper import lookup_plant, UnknownPlantCode
from apps.normalization.emission_scope import resolve_scope
from apps.normalization.rules import check_activity_value, check_period
FLIGHT_EF = {
    'economy':  0.255,
    'business': 0.573,
    'first':    1.020,
    'unknown':  0.255,
}
HOTEL_EF = 0.0713
GROUND_EF = {
    'taxi':       0.14921,
    'car_rental': 0.16844,
    'train':      0.03549,
    'bus':        0.10471,
    'unknown':    0.14921,
}
AIRPORT_DISTANCES_KM: dict[frozenset, float] = {
    frozenset({'DEL', 'BOM'}): 1148.0,
    frozenset({'DEL', 'BLR'}): 1740.0,
    frozenset({'LHR', 'JFK'}): 5539.0,
    frozenset({'LHR', 'DEL'}): 6700.0,
    frozenset({'JFK', 'LAX'}): 3983.0,
    frozenset({'DXB', 'DEL'}): 2194.0,
}
def _to_decimal(value) -> Decimal | None:
    if value is None:
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None
def _resolve_period(data: dict, source_type: str) -> tuple[date, date]:
    if source_type == 'utility':
        if data.get('period_start_raw') and data.get('period_end_raw'):
            return parse_date(data['period_start_raw']), parse_date(data['period_end_raw'])
        elif data.get('billing_period'):
            return billing_period_to_range(data['billing_period'])

    if source_type == 'sap':
        d = data.get('posting_date')
        if d:
            return date(d.year, d.month, 1), d

    if source_type == 'travel':
        d = parse_date(data['travel_date_raw'])
        return d, d

    raise ValueError("Cannot resolve period from parsed data.")
def _normalize_sap(data: dict, warnings: list) -> tuple[float | None, str]:
    qty = data.get('quantity')
    unit = data.get('unit', '')

    if qty is None:
        warnings.append("SAP quantity is None, cannot normalize.")
        return None, unit

    VOLUME = {'L', 'LTR', 'LITRE', 'LITRES', 'ML', 'M3', 'GAL', 'BBL'}
    MASS = {'KG', 'G', 'T', 'MT', 'TONNE', 'LB', 'LBS'}

    try:
        if unit in VOLUME:
            return to_litres(qty, unit), 'litres'
        elif unit in MASS:
            return to_kg(qty, unit), 'kg'
        else:
            warnings.append(f"Unknown SAP unit '{unit}', keeping as-is.")
            return qty, unit
    except UnitConversionError as e:
        warnings.append(str(e))
        return qty, unit


def _normalize_utility(data: dict, warnings: list) -> tuple[float | None, str]:
    consumption = data.get('consumption')
    unit = data.get('unit', 'kWh')

    if consumption is None:
        warnings.append("Utility consumption is None, cannot normalize.")
        return None, unit

    try:
        return to_kwh(consumption, unit), 'kWh'
    except UnitConversionError as e:
        warnings.append(str(e))
        return consumption, unit


def _normalize_travel(data: dict, warnings: list) -> tuple[float | None, str, float | None, str]:
    category = data['category']

    if category == 'business_travel_flight':
        origin = data.get('origin', '')
        dest = data.get('destination', '')
        key = frozenset({origin, dest})
        distance = AIRPORT_DISTANCES_KM.get(key)
        if not distance:
            warnings.append(f"Unknown route {origin}→{dest}, distance set to 0.")
            distance = 0.0
        cabin = data.get('cabin_class', 'unknown')
        ef = FLIGHT_EF.get(cabin, FLIGHT_EF['unknown'])
        return distance, 'km', ef, 'DEFRA 2023'

    elif category == 'business_travel_hotel':
        nights = data.get('nights')
        if nights is None:
            warnings.append("Hotel nights is None, defaulting to 0.")
            nights = 0.0
        return float(nights), 'nights', HOTEL_EF, 'DEFRA 2023'

    elif category == 'business_travel_ground':
        raw_dist = data.get('distance')
        unit = data.get('distance_unit', 'km')

        if raw_dist is None:
            warnings.append("Ground transport distance is None, defaulting to 0.")
            distance = 0.0
        else:
            try:
                distance = to_km(float(raw_dist), unit)
            except (UnitConversionError, ValueError) as e:
                warnings.append(str(e))
                distance = 0.0

        TYPE_MAP = {
            'taxi': 'taxi', 'cab': 'taxi', 'uber': 'taxi',
            'car': 'car_rental', 'rental': 'car_rental',
            'train': 'train', 'rail': 'train',
            'bus': 'bus', 'coach': 'bus',
        }
        mapped = TYPE_MAP.get(data.get('transport_type', 'unknown'), 'unknown')
        ef = GROUND_EF.get(mapped, GROUND_EF['unknown'])
        return distance, 'km', ef, 'DEFRA 2023'

    raise ValueError(f"Unknown travel category '{category}'")
def normalize_row(row: IngestionRow) -> NormalizedEmission | None:
    data = row.parsed_data
    source_type = row.job.source_type
    warnings = []
    if source_type == 'sap':
        activity_value, activity_unit = _normalize_sap(data, warnings)
        original_value = data.get('quantity')
        original_unit = data.get('unit', '')
        ef = None
        ef_source = ''
        try:
            lookup_plant(data.get('plant_code', ''))
        except UnknownPlantCode as e:
            warnings.append(str(e))
    elif source_type == 'utility':
        activity_value, activity_unit = _normalize_utility(data, warnings)
        original_value = data.get('consumption')
        original_unit = data.get('unit', '')
        ef = None
        ef_source = ''
    elif source_type == 'travel':
        activity_value, activity_unit, ef, ef_source = _normalize_travel(data, warnings)
        original_value = activity_value
        original_unit = activity_unit
    else:
        raise ValueError(f"Unknown source_type '{source_type}'")
    period_start = period_end = None
    try:
        period_start, period_end = _resolve_period(data, source_type)
    except (DateParseError, ValueError) as e:
        warnings.append(str(e))
    try:
        scope = resolve_scope(source_type, data['category'])
    except Exception as e:
        warnings.append(str(e))
        scope = None
    violations = []
    if activity_value is not None:
        violations += check_activity_value(activity_value, activity_unit, data['category'])
    if period_start and period_end:
        violations += check_period(period_start, period_end)
    has_error = (
        any(v.severity == 'error' for v in violations)
        or activity_value is None
        or period_start is None
        or scope is None
    )
    all_warnings = warnings + [v.message for v in violations]
    if all_warnings:
        row.status = 'error' if has_error else 'warning'
        row.error_message = '; '.join(all_warnings)
        row.save()
    if has_error:
        return None
    activity_decimal = _to_decimal(activity_value)
    original_decimal = _to_decimal(original_value)
    ef_decimal = _to_decimal(ef)
    co2e_kg = (activity_decimal * ef_decimal) if (activity_decimal and ef_decimal) else None
    emission = NormalizedEmission(
        organisation=row.job.organisation,
        source_row=row,
        scope=scope,
        category=data['category'],
        activity_value=activity_decimal,
        activity_unit=activity_unit,
        co2e_kg=co2e_kg,
        period_start=period_start,
        period_end=period_end,
        original_value=original_decimal,
        original_unit=original_unit,
        emission_factor_used=ef_decimal,
        emission_factor_source=ef_source,
        status='pending_review',
    )
    emission.save()
    return emission