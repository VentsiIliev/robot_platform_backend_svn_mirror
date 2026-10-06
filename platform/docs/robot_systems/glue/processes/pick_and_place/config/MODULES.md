# Module reference: `src/robot_systems/glue/processes/pick_and_place/config`

[Package guide](README.md) · [Complete source index](../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [pick_and_place_config.py](#pick_and_place_configpy)

## `__init__.py`

Source: [src/robot_systems/glue/processes/pick_and_place/config/__init__.py](../../../../../../src/robot_systems/glue/processes/pick_and_place/config/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `.pick_and_place_config`.

Package-level import/export surface:

```python
from .pick_and_place_config import MotionProfile, PickAndPlaceConfig, PlaneConfig
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['MotionProfile', 'PickAndPlaceConfig', 'PlaneConfig']
```

## `pick_and_place_config.py`

Source: [src/robot_systems/glue/processes/pick_and_place/config/pick_and_place_config.py](../../../../../../src/robot_systems/glue/processes/pick_and_place/config/pick_and_place_config.py).

Imports (including optional/function-local imports; not a startup dependency list): `dataclasses`, `typing`.

### `PlaneConfig`

```python
@dataclass
class PlaneConfig:
```

Declared fields/defaults:

```python
x_min: float = -450.0
x_max: float = 350.0
y_min: float = 300.0
y_max: float = 700.0
spacing: float = 30.0
row_gap: float = 50.0
```

### `MotionProfile`

```python
@dataclass
class MotionProfile:
```

Declared fields/defaults:

```python
tool: int = 0
user: int = 0
velocity: float = 20.0
acceleration: float = 10.0
blend_radius: float = 0.0
```

### `PickAndPlaceConfig`

```python
@dataclass
class PickAndPlaceConfig:
```

Declared fields/defaults:

```python
plane: PlaneConfig = field(default_factory=PlaneConfig)
pick_motion: MotionProfile = field(default_factory=MotionProfile)
place_motion: MotionProfile = field(default_factory=MotionProfile)
z_safe: float = 350.0
descent_height_offset: float = 150.0
orientation_rx: float = 180.0
orientation_ry: float = 0.0
rz_orientation: float = 90.0
pickup_target: str = 'tool'
camera_to_tcp_x_offset: float = 0.0
camera_to_tcp_y_offset: float = 0.0
gripper_z_offsets: Dict[int, float] = field(default_factory=dict)
max_vision_retries: int = 10
vision_retry_delay_s: float = 1.0
height_adjustment_mm: float = 2.0
height_source: str = 'zero'
```
