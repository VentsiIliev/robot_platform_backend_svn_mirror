# Module reference: `src/robot_systems/paint/processes/paint/motion`

[Package guide](README.md) · [Complete source index](../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [path_geometry.py](#path_geometrypy)
- [pose_comparison.py](#pose_comparisonpy)
- [pose_sampling.py](#pose_samplingpy)

## `__init__.py`

Source: [src/robot_systems/paint/processes/paint/motion/__init__.py](../../../../../../src/robot_systems/paint/processes/paint/motion/__init__.py).

Shared motion primitives for the paint process.

Imports (including optional/function-local imports; not a startup dependency list): `.path_geometry`, `.pose_comparison`, `.pose_sampling`.

Package-level import/export surface:

```python
from .path_geometry import shift_path_rotation
from .pose_comparison import poses_close
from .pose_sampling import FreshPoseReadError, read_fresh_pose, wait_for_stable_pose
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['FreshPoseReadError', 'poses_close', 'read_fresh_pose', 'shift_path_rotation', 'wait_for_stable_pose']
```

## `path_geometry.py`

Source: [src/robot_systems/paint/processes/paint/motion/path_geometry.py](../../../../../../src/robot_systems/paint/processes/paint/motion/path_geometry.py).

Pure path transformations shared by paint motion workflows.

Imports (including optional/function-local imports; not a startup dependency list): `__future__`.

### `shift_path_rotation`

```python
def shift_path_rotation(path: list[list[float]], rotation_index: int, shift_degrees: float) -> list[list[float]]
```

Return a copied path with a constant shift applied to one rotation component.

## `pose_comparison.py`

Source: [src/robot_systems/paint/processes/paint/motion/pose_comparison.py](../../../../../../src/robot_systems/paint/processes/paint/motion/pose_comparison.py).

Pose comparison helpers shared by paint motion workflows.

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.engine.geometry.planar`.

### `poses_close`

```python
def poses_close(left: list[float] | None, right: list[float] | None, tolerance: float=0.001) -> bool
```

Return whether two six-axis poses match, accounting for wrapped RZ angles.

## `pose_sampling.py`

Source: [src/robot_systems/paint/processes/paint/motion/pose_sampling.py](../../../../../../src/robot_systems/paint/processes/paint/motion/pose_sampling.py).

Robot-pose sampling shared by paint pickup workflows.

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `collections.abc`, `logging`, `math`, `time`.

### `FreshPoseReadError`

```python
class FreshPoseReadError(RuntimeError):
```

Raised when a required fresh six-axis robot pose cannot be acquired.

### `read_fresh_pose`

```python
def read_fresh_pose(robot_service: object, *, error_message: str) -> list[float]
```

Read one valid six-axis pose through the required fresh-read API.

### `wait_for_stable_pose`

```python
def wait_for_stable_pose(robot_service: object, *, logger: logging.Logger, read_error_message: str, timeout_message: str, timeout_s: float=1.0, minimum_timeout_s: float=0.0, sample_interval_s: float=0.05, minimum_sample_interval_s: float=0.0, required_stable_samples: int=3, xyz_tolerance_mm: float=0.5, angular_tolerance_deg: float=0.2, stable_log_prefix: str | None=None, monotonic: Callable[[], float]=time.monotonic, sleep: Callable[[float], None]=time.sleep) -> list[float] | None
```

Return a pose after consecutive samples show that robot motion has settled.
