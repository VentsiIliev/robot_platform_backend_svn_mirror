"""Load explicit profile components and expand their robot description once per content.

No robot control or ROS node calls. The resulting plain URDF is suitable for
MoveIt, KDL, workspace extraction, calibration and the real-time observer.
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
import tempfile
import xml.etree.ElementTree as ET

import yaml


def load_yaml_layers(path: str | Path, *, _stack: tuple[Path, ...] = ()) -> dict:
    """Merge included mappings in order, then apply this file's explicit values."""
    path = Path(path).resolve()
    if path in _stack:
        raise ValueError('Configuration include cycle: ' + ' -> '.join(map(str, (*_stack, path))))
    document = yaml.safe_load(path.read_text(encoding='utf-8'))
    if document is None:
        document = {}
    if not isinstance(document, dict):
        raise ValueError(f'Configuration must be a mapping: {path}')
    includes = document.pop('RUNTIME_INCLUDES', [])
    if not isinstance(includes, list) or any(not isinstance(p, str) or not p.strip() for p in includes):
        raise ValueError(f'RUNTIME_INCLUDES must be a list of paths: {path}')
    result = {}
    for include in includes:
        result.update(load_yaml_layers(path.parent / include, _stack=(*_stack, path)))
    result.update(document)
    return result


def resolve_robot_description(profile_yaml: str | Path, configuration: dict) -> str:
    """Expand a profile's Xacro to an atomically written, content-addressed URDF."""
    import xacro

    entry = Path(str(configuration['URDF_PATH']))
    if not entry.is_absolute():
        entry = Path(profile_yaml).parent / entry
    entry = entry.resolve(strict=True)
    expanded = xacro.process_file(str(entry)).toxml().encode('utf-8')
    root = ET.fromstring(expanded)
    if root.tag != 'robot':
        raise ValueError(f'Xacro must produce a robot description: {entry}')
    if any(node.tag.startswith('{http://www.ros.org/wiki/xacro}') for node in root.iter()):
        raise ValueError(f'Unexpanded Xacro in robot description: {entry}')
    # Strip Xacro provenance comments and optional empty geometry names so the
    # cache key reflects the expanded robot rather than its source-file location.
    for node in root.iter():
        if node.tag in ('visual', 'collision') and node.get('name') == '':
            del node.attrib['name']
    expanded = ET.tostring(root, encoding='utf-8', xml_declaration=True)
    digest = hashlib.sha256(expanded).hexdigest()
    # Per-user writable cache; installed package shares remain read-only.
    cache = Path(os.environ.get('XDG_CACHE_HOME', Path.home() / '.cache')) / 'zeroerr' / 'descriptions'
    cache.mkdir(parents=True, exist_ok=True)
    output = cache / f'{digest}.urdf'
    if output.exists() and output.read_bytes() == expanded:
        return str(output)
    fd, temporary = tempfile.mkstemp(prefix='.description-', dir=cache)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(expanded)
        os.replace(temporary, output)
    finally:
        Path(temporary).unlink(missing_ok=True)
    return str(output)
