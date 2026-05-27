import json
from typing import Any
from apps.normalization.date_normalizer import parse_date, DateParseError
def _parse_flight(segment: dict, warnings: list) -> dict:
    return {
        'segment_type':     'flight',
        'category':         'business_travel_flight',
        'origin':           segment.get('origin_airport', segment.get('from', '')).upper().strip(),
        'destination':      segment.get('destination_airport', segment.get('to', '')).upper().strip(),
        'cabin_class':      segment.get('cabin_class', segment.get('class', 'unknown')).lower(),
        'distance':         segment.get('distance', None),
        'distance_unit':    segment.get('distance_unit', 'km'),
    }
def _parse_hotel(segment: dict, warnings: list) -> dict:
    try:
        nights = float(segment.get('nights', segment.get('duration', 1)))
    except (ValueError, TypeError):
        nights = None
        warnings.append("Could not parse hotel nights.")

    return {
        'segment_type': 'hotel',
        'category':     'business_travel_hotel',
        'nights':       nights,
        'hotel_name':   segment.get('hotel_name', segment.get('property', '')),
        'city':         segment.get('city', ''),
    }
def _parse_ground(segment: dict, warnings: list) -> dict:
    raw_distance = segment.get('distance', segment.get('distance_km', None))
    try:
        distance = float(raw_distance) if raw_distance is not None else None
    except (ValueError, TypeError):
        distance = None
        warnings.append(f"Could not parse ground distance '{raw_distance}'.")

    return {
        'segment_type':   'ground',
        'category':       'business_travel_ground',
        'transport_type': segment.get('transport_type', segment.get('type', 'unknown')).lower(),
        'distance':       distance,
        'distance_unit':  segment.get('distance_unit', 'km'),
    }
def parse(file_content: bytes) -> list[dict[str, Any]]:
    try:
        data = json.loads(file_content.decode('utf-8'))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        raise ValueError(f"Could not parse travel JSON: {e}")
    trips = data.get('trips', [])
    results = []
    for trip in trips:
        trip_id = trip.get('trip_id', '')
        traveller = trip.get('traveller', trip.get('employee', ''))
        travel_date_raw = trip.get('travel_date', trip.get('date', ''))
        for segment in trip.get('segments', []):
            warnings = []
            parse_status = 'ok'
            seg_type = segment.get('type', '').lower()
            if seg_type == 'flight':
                parsed = _parse_flight(segment, warnings)
            elif seg_type == 'hotel':
                parsed = _parse_hotel(segment, warnings)
            elif seg_type in ('ground', 'car', 'taxi', 'train', 'bus'):
                parsed = _parse_ground(segment, warnings)
            else:
                warnings.append(f"Unknown segment type '{seg_type}', skipped.")
                continue
            if warnings:
                parse_status = 'warning'
            parsed.update({
                'parse_status':    parse_status,
                'parse_warnings':  warnings,
                'trip_id':         trip_id,
                'traveller':       traveller,
                'travel_date_raw': travel_date_raw,  # raw string, normalization parses it
            })
            results.append(parsed)
    return results