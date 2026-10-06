# Module reference: `src/robot_systems/paint/applications/paint_motion_plane_setup/domain`

[Package guide](README.md) · [Complete source index](../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [plane_inference.py](#plane_inferencepy)

## `plane_inference.py`

Source: [src/robot_systems/paint/applications/paint_motion_plane_setup/domain/plane_inference.py](../../../../../../src/robot_systems/paint/applications/paint_motion_plane_setup/domain/plane_inference.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`, `math`.

Module declarations (expressions are shown without evaluating them):

```python
AXES = ('x', 'y', 'z')
ROT_AXES = ('rx', 'ry', 'rz')
POSITION_INDICES = {'x': 0, 'y': 1, 'z': 2}
ROTATION_INDICES = {'rx': 3, 'ry': 4, 'rz': 5}
ROTATION_PLANES = {'rx': (('y', 'z'), 'x'), 'ry': (('x', 'z'), 'y'), 'rz': (('x', 'y'), 'z')}
```

### `Pose6D`

```python
@dataclass(frozen=True)
class Pose6D:
```

Declared fields/defaults:

```python
x: float
y: float
z: float
rx: float
ry: float
rz: float
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def from_sequence(cls, values) -> 'Pose6D'
```

```python
def as_list(self) -> list[float]
```

```python
def position_delta(self, other: 'Pose6D') -> dict[str, float]
```

```python
def rotation_delta(self, other: 'Pose6D') -> dict[str, float]
```

### `PlaneInference`

```python
@dataclass(frozen=True)
class PlaneInference:
```

Declared fields/defaults:

```python
translation_axis: str
translation_direction: str
rotation_axis: str
planar_axes: tuple[str, str]
fixed_axis: str
suggested_plane_key: str
axis_offsets_deg: dict[str, float]
warnings: tuple[str, ...]
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def as_plane_object(self) -> dict
```

```python
def as_runtime_config(self) -> dict
```

```python
def as_paint_plane_config(self, *, movement_group_id: str, reference_pose: Pose6D | None) -> dict
```

### `unwrap_degrees`

```python
def unwrap_degrees(reference: float, value: float) -> float
```

### `dominant_axis`

```python
def dominant_axis(deltas: dict[str, float], *, min_abs: float) -> tuple[str, float] | None
```

### `infer_plane`

```python
def infer_plane(reference_pose: Pose6D, translation_pose: Pose6D, rotation_pose: Pose6D, *, fixed_axis_override: str | None=None, min_translation_mm: float=1.0, min_rotation_deg: float=1.0) -> PlaneInference
```
