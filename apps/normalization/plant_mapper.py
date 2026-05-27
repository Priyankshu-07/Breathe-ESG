class UnknownPlantCode(Exception):
    pass


PLANT_MAP = {
    'P001': 'Mumbai Plant',
    'P002': 'Delhi Plant',
    'P003': 'Bangalore Plant',
    'W001': 'Warehouse Mumbai',
    'W002': 'Warehouse Delhi',
}


def lookup_plant(code: str) -> str:
    if not code:
        raise UnknownPlantCode("Empty plant code.")
    if code not in PLANT_MAP:
        raise UnknownPlantCode(f"Unknown plant code '{code}'.")
    return PLANT_MAP[code]