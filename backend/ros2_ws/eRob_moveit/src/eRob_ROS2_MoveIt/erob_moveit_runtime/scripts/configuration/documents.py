"""Pure document operations shared by configuration use cases and adapters."""
from copy import deepcopy
import hashlib
import json

# TODO - WOULD BE NICE TO HAVE TYPE HINTS AND DOCSTRINGS FOR THESE FUNCTIONS

def merge(base, override):
    result = deepcopy(base)
    for key, value in override.items():
        result[key] = merge(result[key], value) if isinstance(value, dict) and isinstance(result.get(key), dict) else deepcopy(value)
    return result


def differences(value, inherited):
    result = {}
    for key, item in value.items():
        if key not in inherited:
            result[key] = deepcopy(item)
        elif isinstance(item, dict) and isinstance(inherited[key], dict):
            nested = differences(item, inherited[key])
            if nested:
                result[key] = nested
        elif item != inherited[key]:
            result[key] = deepcopy(item)
    return result


def revision(data):
    # YAML integer map keys and JSON string map keys have the same wire representation.
    normalized = json.loads(json.dumps(data, allow_nan=False))
    return hashlib.sha256(json.dumps(normalized, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
