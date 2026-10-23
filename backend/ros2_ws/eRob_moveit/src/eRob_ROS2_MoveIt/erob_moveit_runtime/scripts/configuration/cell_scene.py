"""Profile-owned cell collision definitions, independent of ROS and storage."""
from copy import deepcopy
import math
import re
from .domain import ConfigurationError, transform


def _box(part, identifier):
    if not isinstance(part, dict) or set(part) != {'size_mm', 'pose'}:
        raise ConfigurationError(f'{identifier}: box parts require size_mm and pose')
    size = part['size_mm']
    if (not isinstance(size, list) or len(size) != 3 or any(
            isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(x) or x <= 0 for x in size)):
        raise ConfigurationError(f'{identifier}: size_mm must contain three positive finite numbers')
    transform(part['pose'])


def validate_cell_scene(document):
    if not isinstance(document, dict) or set(document) != {'CELL_COLLISION_OBJECTS'}:
        raise ConfigurationError('Cell scene requires only CELL_COLLISION_OBJECTS')
    objects = document['CELL_COLLISION_OBJECTS']
    if not isinstance(objects, dict):
        raise ConfigurationError('Cell collision objects must be a mapping')
    for identifier, item in objects.items():
        if not isinstance(identifier, str) or not re.fullmatch(r'cell_fixture_[A-Za-z0-9_]+', identifier):
            raise ConfigurationError('Cell collision IDs must start with cell_fixture_')
        if not isinstance(item, dict):
            raise ConfigurationError(f'{identifier}: expected a collision definition')
        geometry = {'parts'} if 'parts' in item else {'size_mm', 'pose'}
        fields = {'enabled', 'frame'} | geometry | ({'merged_into'} if 'merged_into' in item else set())
        if set(item) != fields:
            raise ConfigurationError(f'{identifier}: expected enabled, frame and box geometry')
        if type(item['enabled']) is not bool:
            raise ConfigurationError(f'{identifier}: enabled must be boolean')
        if not isinstance(item['frame'], str) or not re.fullmatch(r'[A-Za-z0-9_][A-Za-z0-9_/]*', item['frame']):
            raise ConfigurationError(f'{identifier}: invalid reference frame')
        if 'parts' in item:
            if not isinstance(item['parts'], list) or not item['parts']:
                raise ConfigurationError(f'{identifier}: parts must be a nonempty box list')
            for part in item['parts']:
                _box(part, identifier)
        else:
            _box({key:item[key] for key in ('size_mm','pose')}, identifier)
        if 'merged_into' in item:
            target = item['merged_into']
            if (not isinstance(target,str) or target == identifier or target not in objects
                    or item['enabled'] or not isinstance(objects[target],dict) or 'parts' not in objects[target]):
                raise ConfigurationError(f'{identifier}: merged members must be disabled and reference a compound object')
    for identifier in objects:
        seen = set()
        current = identifier
        while 'merged_into' in objects[current]:
            if current in seen:
                raise ConfigurationError('Merged collision object cycle')
            seen.add(current)
            current = objects[current]['merged_into']
    return document


def merge_cell_scene(document, command):
    validate_cell_scene(document)
    if not isinstance(command,dict) or set(command) != {'ids','name'}:
        raise ConfigurationError('Merge requires ids and name')
    ids, name = command['ids'], command['name']
    if (not isinstance(ids,list) or len(ids)<2 or any(not isinstance(key,str) for key in ids)
            or len(set(ids)) != len(ids)):
        raise ConfigurationError('Select at least two distinct collision objects')
    if not isinstance(name,str) or not re.fullmatch(r'[A-Za-z][A-Za-z0-9_]*', name):
        raise ConfigurationError('Group name must start with a letter and use letters, digits and underscores')
    identifier = name if name.startswith('cell_fixture_') else 'cell_fixture_'+name
    objects = document['CELL_COLLISION_OBJECTS']
    if identifier in objects:
        raise ConfigurationError('That collision object name already exists')
    if any(key not in objects or 'merged_into' in objects[key] for key in ids):
        raise ConfigurationError('Select existing collision objects that have not already been merged')
    selected = [objects[key] for key in ids]
    if len({item['frame'] for item in selected}) != 1:
        raise ConfigurationError('Merged collision objects must use the same reference frame')
    if len({item['enabled'] for item in selected}) != 1:
        raise ConfigurationError('Set all selected collision objects to the same enabled state before merging')
    parts = []
    for item in selected:
        parts.extend(deepcopy(item['parts']) if 'parts' in item else [
            {key:deepcopy(item[key]) for key in ('size_mm','pose')}])
    candidate = deepcopy(document)
    definitions = candidate['CELL_COLLISION_OBJECTS']
    definitions[identifier] = {'enabled':selected[0]['enabled'], 'frame':selected[0]['frame'], 'parts':parts}
    for key in ids:
        definitions[key]['enabled'] = False
        definitions[key]['merged_into'] = identifier
    return validate_cell_scene(candidate), identifier
