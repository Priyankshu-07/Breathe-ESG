SCOPE_MAP = {
    'fuel_combustion':        'scope1',
    'electricity':            'scope2',
    
}

def resolve_scope(source_type, category):
    return SCOPE_MAP[category]