import csv
import io
from typing import Any
from apps.normalization.date_normalizer import parse_date, DateParseError
COLUMN_MAP = {
    # German
    'buchungsdatum':        'posting_date',
    'belegdatum':           'document_date',
    'menge':                'quantity',
    'mengeneinheit':        'unit',
    'werk':                 'plant_code',
    'material':             'material_code',
    'materialbezeichnung':  'material_description',
    'kostenstelle':         'cost_center',
    'bewegungsart':         'movement_type',
    'posting date':         'posting_date',
    'document date':        'document_date',
    'quantity':             'quantity',
    'unit':                 'unit',
    'plant':                'plant_code',
    'material description': 'material_description',
    'cost center':          'cost_center',
    'movement type':        'movement_type',
}
FUEL_MOVEMENT_TYPES = {'201', '261', '262', 'GI'}
FUEL_MATERIAL_PREFIXES = ('FUEL', 'DSL', 'PETROL', 'CNG', 'LPG', 'HSD')
def _normalize_header(raw: str) -> str:
    return raw.strip().lower().replace('-', ' ').replace('_', ' ')
def _map_headers(headers: list[str]) -> dict[int, str]:
    mapping = {}
    for i, h in enumerate(headers):
        normalized = _normalize_header(h)
        if normalized in COLUMN_MAP:
            mapping[i] = COLUMN_MAP[normalized]
    return mapping
def _detect_category(row: dict) -> str:
    material = row.get('material_code', '').upper()
    movement = row.get('movement_type', '').upper()
    if movement in FUEL_MOVEMENT_TYPES:
        return 'fuel_combustion'
    if any(material.startswith(p) for p in FUEL_MATERIAL_PREFIXES):
        return 'fuel_combustion'
    return 'procurement'
def parse(file_content: bytes) -> list[dict[str, Any]]:
    try:
        text = file_content.decode('utf-8')
    except UnicodeDecodeError:
        text = file_content.decode('latin-1')

    reader = csv.reader(io.StringIO(text), delimiter=';')
    rows = list(reader)

    if not rows:
        return []
    headers = rows[0]
    col_map = _map_headers(headers)
    results = []
    for i, raw_row in enumerate(rows[1:], start=1):
        warnings = []
        parse_status = 'ok'
        row = {}
        for col_idx, internal_key in col_map.items():
            if col_idx < len(raw_row):
                row[internal_key] = raw_row[col_idx].strip()
        if not any(row.values()):
            continue
        raw_date = row.get('posting_date') or row.get('document_date', '')
        try:
            posting_date = parse_date(raw_date)
        except DateParseError as e:
            warnings.append(str(e))
            posting_date = None
            parse_status = 'warning'
        try:
            quantity = float(row.get('quantity', '0').replace(',', '.'))
        except ValueError:
            warnings.append(f"Row {i}: could not parse quantity '{row.get('quantity')}'")
            quantity = None
            parse_status = 'failed'
        results.append({
            'parse_status':         parse_status,
            'parse_warnings':       warnings,
            'quantity':             quantity,
            'unit':                 row.get('unit', '').upper(),
            'posting_date':         posting_date,
            'plant_code':           row.get('plant_code', ''),
            'material_code':        row.get('material_code', ''),
            'material_description': row.get('material_description', ''),
            'movement_type':        row.get('movement_type', ''),
            'category':             _detect_category(row),
            'cost_center':          row.get('cost_center', ''),
        })
    return results