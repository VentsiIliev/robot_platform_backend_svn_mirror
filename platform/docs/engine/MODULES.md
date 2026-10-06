# Module reference: `src/engine`

[Package guide](README.md) · [Complete source index](../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [common_service_ids.py](#common_service_idspy)
- [common_settings_ids.py](#common_settings_idspy)

## `__init__.py`

Source: [src/engine/__init__.py](../../src/engine/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `common_service_ids.py`

Source: [src/engine/common_service_ids.py](../../src/engine/common_service_ids.py).

Imports (including optional/function-local imports; not a startup dependency list): `enum`.

### `CommonServiceID`

```python
class CommonServiceID(str, Enum):
```

Declared fields/defaults:

```python
ROBOT = 'robot'
NAVIGATION = 'navigation'
WORK_AREAS = 'work_areas'
VISION = 'vision'
TOOLS = 'tools'
```

## `common_settings_ids.py`

Source: [src/engine/common_settings_ids.py](../../src/engine/common_settings_ids.py).

Imports (including optional/function-local imports; not a startup dependency list): `enum`.

### `CommonSettingsID`

```python
class CommonSettingsID(str, Enum):
```

Declared fields/defaults:

```python
ROBOT_CONFIG = 'robot_config'
MOVEMENT_GROUPS = 'movement_groups'
ROBOT_CALIBRATION = 'robot_calibration'
CALIBRATION_VISION_SETTINGS = 'calibration_vision_settings'
MODBUS_CONFIG = 'modbus_config'
VISION_CAMERA_SETTINGS = 'vision_camera_settings'
TARGETING = 'targeting'
WORK_AREA_SETTINGS = 'work_area_settings'
TOOL_CHANGER_CONFIG = 'tool_changer_config'
HEIGHT_MEASURING_SETTINGS = 'height_measuring_settings'
HEIGHT_MEASURING_CALIBRATION = 'height_measuring_calibration'
DEPTH_MAP_DATA = 'depth_map_data'
```
