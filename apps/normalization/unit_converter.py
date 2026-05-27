class UnitConversionError(Exception):
    pass


def to_litres(value: float, unit: str) -> float:
    unit = unit.upper()
    conversions = {
        'L': 1, 'LTR': 1, 'LITRE': 1, 'LITRES': 1,
        'ML': 0.001,
        'M3': 1000,
        'GAL': 3.78541,
        'BBL': 158.987,
    }
    if unit not in conversions:
        raise UnitConversionError(f"Cannot convert '{unit}' to litres.")
    return value * conversions[unit]


def to_kwh(value: float, unit: str) -> float:
    unit = unit.upper()
    conversions = {
        'KWH': 1,
        'MWH': 1000,
        'GWH': 1000000,
        'J': 2.77778e-7,
        'MJ': 0.277778,
        'GJ': 277.778,
    }
    if unit not in conversions:
        raise UnitConversionError(f"Cannot convert '{unit}' to kWh.")
    return value * conversions[unit]


def to_kg(value: float, unit: str) -> float:
    unit = unit.upper()
    conversions = {
        'KG': 1,
        'G': 0.001,
        'T': 1000, 'MT': 1000, 'TONNE': 1000,
        'LB': 0.453592, 'LBS': 0.453592,
    }
    if unit not in conversions:
        raise UnitConversionError(f"Cannot convert '{unit}' to kg.")
    return value * conversions[unit]


def to_km(value: float, unit: str) -> float:
    unit = unit.upper()
    conversions = {
        'KM': 1,
        'M': 0.001,
        'MI': 1.60934,
        'MILES': 1.60934,
        'NM': 1.852,
    }
    if unit not in conversions:
        raise UnitConversionError(f"Cannot convert '{unit}' to km.")
    return value * conversions[unit]