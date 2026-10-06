# Module reference: `src/applications/aruco_z_probe/model`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [aruco_z_probe_model.py](#aruco_z_probe_modelpy)

## `__init__.py`

Source: [src/applications/aruco_z_probe/model/__init__.py](../../../../src/applications/aruco_z_probe/model/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `aruco_z_probe_model.py`

Source: [src/applications/aruco_z_probe/model/aruco_z_probe_model.py](../../../../src/applications/aruco_z_probe/model/aruco_z_probe_model.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.aruco_z_probe.service.i_aruco_z_probe_service`, `src.applications.base.i_application_model`, `threading`, `typing`.

### `ArucoZProbeModel`

```python
class ArucoZProbeModel(IApplicationModel):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, service: IArucoZProbeService)
```

```python
def load(self) -> None
```

```python
def save(self, *args, **kwargs) -> None
```

```python
def move_to_calibration_position(self) -> bool
```

```python
def run_sweep(self, marker_id: int, min_z: float, sample_count: int, detection_attempts: int, stop_event: threading.Event, progress_cb: Callable[[int, int, float, Optional[float], Optional[float]], None], log_cb: Optional[Callable[[str], None]]=None, stabilization_delay: float=0.3) -> Tuple[bool, str, List[ArucoZSample]]
```

```python
def run_verification(self, z_heights: List[float], marker_id: int, detection_attempts: int, stop_event: threading.Event, progress_cb: Callable[[int, int, float, Optional[float], Optional[float]], None], log_cb: Optional[Callable[[str], None]]=None, stabilization_delay: float=0.3) -> Tuple[bool, str, List[ArucoZSample]]
```
