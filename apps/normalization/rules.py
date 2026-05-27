from dataclasses import dataclass
from datetime import date


@dataclass
class Violation:
    severity: str   # 'warning' or 'error'
    message: str


def check_activity_value(value: float, unit: str, category: str) -> list[Violation]:
    violations = []
    
    if value < 0:
        violations.append(Violation('error', f"Negative activity value {value}."))
    
    if value == 0:
        violations.append(Violation('warning', f"Activity value is zero."))
    
    if category == 'electricity' and value > 10_000_000:
        violations.append(Violation('warning', f"Unusually high electricity consumption: {value} kWh."))
    
    return violations


def check_period(start: date, end: date) -> list[Violation]:
    violations = []
    
    if end < start:
        violations.append(Violation('error', f"Period end {end} is before start {start}."))
    
    if (end - start).days > 366:
        violations.append(Violation('warning', f"Period spans more than a year."))
    
    return violations