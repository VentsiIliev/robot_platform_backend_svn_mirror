# Module reference: `src/applications/aruco_z_probe/service`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [aruco_z_probe_application_service.py](#aruco_z_probe_application_servicepy)
- [i_aruco_z_probe_service.py](#i_aruco_z_probe_servicepy)
- [stub_aruco_z_probe_service.py](#stub_aruco_z_probe_servicepy)

## `__init__.py`

Source: [src/applications/aruco_z_probe/service/__init__.py](../../../../src/applications/aruco_z_probe/service/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `aruco_z_probe_application_service.py`

Source: [src/applications/aruco_z_probe/service/aruco_z_probe_application_service.py](../../../../src/applications/aruco_z_probe/service/aruco_z_probe_application_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `logging`, `src.applications.aruco_z_probe.service.i_aruco_z_probe_service`, `threading`, `time`, `typing`.

### `_log`

```python
def _log(log_cb: Optional[Callable[[str], None]], msg: str) -> None
```

### `ArucoZProbeApplicationService`

```python
class ArucoZProbeApplicationService(IArucoZProbeService):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, navigation=None, robot_service=None, vision_service=None, robot_config=None)
```

```python
def move_to_calibration_position(self) -> bool
```

```python
def run_sweep(self, marker_id: int, min_z: float, sample_count: int, detection_attempts: int, stop_event: threading.Event, progress_cb: Callable[[int, int, float, Optional[float], Optional[float]], None], log_cb: Optional[Callable[[str], None]]=None, stabilization_delay: float=_STABILIZATION_DELAY) -> Tuple[bool, str, List[ArucoZSample]]
```

```python
def run_verification(self, z_heights: List[float], marker_id: int, detection_attempts: int, stop_event: threading.Event, progress_cb: Callable[[int, int, float, Optional[float], Optional[float]], None], log_cb: Optional[Callable[[str], None]]=None, stabilization_delay: float=_STABILIZATION_DELAY) -> Tuple[bool, str, List[ArucoZSample]]
```

## `i_aruco_z_probe_service.py`

Source: [src/applications/aruco_z_probe/service/i_aruco_z_probe_service.py](../../../../src/applications/aruco_z_probe/service/i_aruco_z_probe_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `abc`, `threading`, `typing`.

Module declarations (expressions are shown without evaluating them):

```python
ArucoZSample = Tuple[float, Optional[float], Optional[float]]
```

### `IArucoZProbeService`

```python
class IArucoZProbeService(ABC):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def move_to_calibration_position(self) -> bool
```

Move robot to the calibration group position.

```python
@abstractmethod
def run_sweep(self, marker_id: int, min_z: float, sample_count: int, detection_attempts: int, stop_event: threading.Event, progress_cb: Callable[[int, int, float, Optional[float], Optional[float]], None], log_cb: Optional[Callable[[str], None]]=None, stabilization_delay: float=0.3) -> Tuple[bool, str, List[ArucoZSample]]
```

Detect marker baseline at current Z, step down to min_z in sample_count equal steps, return to baseline Z at the end. progress_cb(step_index, total_steps, z_mm, dx_px, dy_px) log_cb(message) — optional, called for motion/detection status lines. Returns (success, message, samples).

```python
@abstractmethod
def run_verification(self, z_heights: List[float], marker_id: int, detection_attempts: int, stop_event: threading.Event, progress_cb: Callable[[int, int, float, Optional[float], Optional[float]], None], log_cb: Optional[Callable[[str], None]]=None, stabilization_delay: float=0.3) -> Tuple[bool, str, List[ArucoZSample]]
```

Re-detect baseline at current Z, then visit each z in z_heights, measure actual marker shift relative to that baseline, and return to the starting Z when done. progress_cb(step_index, total_steps, z_mm, dx_px, dy_px) log_cb(message) — optional, called for motion/detection status lines. Returns (success, message, samples).

## `stub_aruco_z_probe_service.py`

Source: [src/applications/aruco_z_probe/service/stub_aruco_z_probe_service.py](../../../../src/applications/aruco_z_probe/service/stub_aruco_z_probe_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `logging`, `math`, `numpy`, `src.applications.aruco_z_probe.service.i_aruco_z_probe_service`, `threading`, `time`, `typing`.

### `StubArucoZProbeService`

```python
class StubArucoZProbeService(IArucoZProbeService):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def move_to_calibration_position(self) -> bool
```

```python
def run_sweep(self, marker_id: int, min_z: float, sample_count: int, detection_attempts: int, stop_event: threading.Event, progress_cb: Callable[[int, int, float, Optional[float], Optional[float]], None], log_cb: Optional[Callable[[str], None]]=None, stabilization_delay: float=0.3) -> Tuple[bool, str, List[ArucoZSample]]
```

```python
def run_verification(self, z_heights: List[float], marker_id: int, detection_attempts: int, stop_event: threading.Event, progress_cb: Callable[[int, int, float, Optional[float], Optional[float]], None], log_cb: Optional[Callable[[str], None]]=None, stabilization_delay: float=0.3) -> Tuple[bool, str, List[ArucoZSample]]
```
