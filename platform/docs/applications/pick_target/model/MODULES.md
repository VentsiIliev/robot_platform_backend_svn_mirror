# Module reference: `src/applications/pick_target/model`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [pick_target_model.py](#pick_target_modelpy)

## `__init__.py`

Source: [src/applications/pick_target/model/__init__.py](../../../../src/applications/pick_target/model/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `pick_target_model.py`

Source: [src/applications/pick_target/model/pick_target_model.py](../../../../src/applications/pick_target/model/pick_target_model.py).

Imports (including optional/function-local imports; not a startup dependency list): `numpy`, `src.applications.base.i_application_model`, `src.applications.pick_target.service.i_pick_target_service`, `typing`.

### `PickTargetModel`

```python
class PickTargetModel(IApplicationModel):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, service: IPickTargetService)
```

```python
def load(self) -> None
```

```python
def save(self, *args, **kwargs) -> None
```

```python
def capture(self) -> Tuple[Optional[np.ndarray], List[Tuple[float, float]], List[Tuple[float, float, float, float, float, float]]]
```

```python
def move_to(self, x: float, y: float, z: float, rx: float, ry: float, rz: float) -> bool
```

```python
def move_to_base(self, x: float, y: float, rx: float, ry: float, rz: float, z: float | None=None) -> bool
```

```python
def move_to_with_live_height(self, x: float, y: float, rx: float, ry: float, rz: float, z: float | None=None) -> bool
```

```python
def move_to_calibration_position(self) -> bool
```

```python
def set_target(self, target: str) -> None
```

```python
def set_use_pickup_plane(self, enabled: bool) -> None
```

```python
def set_pickup_plane_rz(self, rz: float) -> None
```

```python
def capture_contour_trajectory(self) -> List[np.ndarray]
```

```python
def execute_contour_trajectory(self, contour_robot_pts: List[np.ndarray], z: float, vel: float, acc: float) -> Tuple[bool, str]
```
