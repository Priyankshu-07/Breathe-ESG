import csv
import io
from typing import Any
from apps.normalization.date_normalizer import parse_date, DateParseError
COLUMN_MAP = {
    'meter id':             'meter_id',
    'meterid':              'meter_id',
    'meter number':         'meter_id',
    'account number':       'account_number',
    'site':                 'site_name',
    'location':             'site_name',
    'facility':             'site_name',
    'billing period start': 'period_start_raw',
    'period start':         'period_start_raw',
    'from':                 'period_start_raw',
    'billing period end':   'period_end_raw',
    'period end':           'period_end_raw',
    'to':                   'period_end_raw',
    'billing period':       'billing_period',
    'period':               'billing_period',
    'consumption':          'consumption',
    'usage':                'consumption',
    'kwh':                  'consumption',
    'units consumed':       'consumption',
    'unit':                 'unit',
    'units':                'unit',
    'uom':                  'unit',
    'tariff':               'tariff',
    'rate':                 'tariff',
    'total cost':           'total_cost',
    'amount':               'total_cost',
    'currency':             'currency',
}
def _map_headers(headers: list[str]) -> dict[int, str]:
    mapping = {}
    for i, h in enumerate(headers):
        if h.strip().lower() in COLUMN_MAP:
            mapping[i] = COLUMN_MAP[h.strip().lower()]
    return mapping
def parse(file_content: bytes) -> list[dict[str, Any]]:
    try:
        text = file_content.decode('utf-8-sig')
    except UnicodeDecodeError:
        text = file_content.decode('latin-1')
    reader = csv.reader(io.StringIO(text))
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
        try:
            consumption = float(row.get('consumption', '0').replace(',', ''))
        except ValueError:
            warnings.append(f"Row {i}: could not parse consumption '{row.get('consumption')}'")
            consumption = None
            parse_status = 'failed'
        if not row.get('period_start_raw') and not row.get('billing_period'):
            warnings.append(f"Row {i}: no billing period found.")
            parse_status = 'warning'
        results.append({
            'parse_status':     parse_status,
            'parse_warnings':   warnings,
            'consumption':      consumption,
            'unit':             row.get('unit', 'kWh'),
            'period_start_raw': row.get('period_start_raw', ''),
            'period_end_raw':   row.get('period_end_raw', ''),
            'billing_period':   row.get('billing_period', ''),
            'meter_id':         row.get('meter_id', ''),
            'site_name':        row.get('site_name', ''),
            'tariff':           row.get('tariff', ''),
            'total_cost':       row.get('total_cost', ''),
            'currency':         row.get('currency', ''),
            'category':         'electricity',
        })
    return results