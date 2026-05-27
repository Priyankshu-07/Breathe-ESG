from datetime import date, datetime
from calendar import monthrange


class DateParseError(Exception):
    pass


def parse_date(raw: str) -> date:
    if not raw:
        raise DateParseError(f"Empty date string.")
    
    formats = [
        '%Y%m%d',      # SAP: 20231231
        '%d.%m.%Y',    # SAP German: 31.12.2023
        '%Y-%m-%d',    # ISO: 2023-12-31
        '%d/%m/%Y',    # UK: 31/12/2023
        '%m/%d/%Y',    # US: 12/31/2023
        '%d-%m-%Y',    # 31-12-2023
        '%b %Y',       # Jan 2023
        '%B %Y',       # January 2023
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(raw.strip(), fmt).date()
        except ValueError:
            continue
    
    raise DateParseError(f"Cannot parse date '{raw}'.")


def billing_period_to_range(raw: str) -> tuple[date, date]:
    # Handles "Jan 2023", "January 2023", "2023-01"
    formats = [
        ('%b %Y', '%b %Y'),
        ('%B %Y', '%B %Y'),
        ('%Y-%m', '%Y-%m'),
    ]
    
    for fmt, _ in formats:
        try:
            d = datetime.strptime(raw.strip(), fmt).date()
            last_day = monthrange(d.year, d.month)[1]
            return date(d.year, d.month, 1), date(d.year, d.month, last_day)
        except ValueError:
            continue
    
    raise DateParseError(f"Cannot parse billing period '{raw}'.")