# Module reference: `src/applications/height_measuring/service`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [height_measuring_application_service.py](#height_measuring_application_servicepy)
- [i_height_measuring_app_service.py](#i_height_measuring_app_servicepy)
- [stub_height_measuring_app_service.py](#stub_height_measuring_app_servicepy)

## `__init__.py`

Source: [src/applications/height_measuring/service/__init__.py](../../../../src/applications/height_measuring/service/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `height_measuring_application_service.py`

Source: [src/applications/height_measuring/service/height_measuring_application_service.py](../../../../src/applications/height_measuring/service/height_measuring_application_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `cv2`, `logging`, `numpy`, `src.applications.height_measuring.service.i_height_measuring_app_service`, `src.engine.repositories.interfaces.settings_repository`, `src.engine.robot.height_measuring.i_height_measuring_service`, `src.engine.robot.height_measuring.settings`, `src.engine.vision.i_vision_service`, `threading`, `typing`.

### `_ILaserCalibrator`

```python
class _ILaserCalibrator(Protocol):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def calibrate(self, initial_position: list) -> bool
```

### `_ILaserOps`

```python
class _ILaserOps(Protocol):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def turn_on(self) -> None
```

```python
def turn_off(self) -> None
```

```python
def detect(self) -> tuple
```

```python
def restore(self) -> None
```

### `HeightMeasuringApplicationService`

```python
class HeightMeasuringApplicationService(IHeightMeasuringAppService):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, vision_service: Optional[IVisionService], height_measuring_service: IHeightMeasuringService, calibration_service: _ILaserCalibrator, settings_repo: ISettingsRepository, laser_ops: Optional[_ILaserOps]=None)
```

```python
def run_calibration(self) -> tuple[bool, str]
```

```python
def cancel_calibration(self) -> None
```

```python
def is_calibrated(self) -> bool
```

```python
def get_calibration_info(self) -> Optional[dict]
```

```python
def get_settings(self) -> HeightMeasuringModuleSettings
```

```python
def save_settings(self, settings: HeightMeasuringModuleSettings) -> tuple[bool, str]
```

```python
def get_latest_frame(self) -> Optional[np.ndarray]
```

```python
def reload_calibration(self) -> None
```

```python
def laser_on(self) -> tuple[bool, str]
```

```python
def laser_off(self) -> tuple[bool, str]
```

```python
def detect_once(self) -> LaserDetectionResult
```

```python
def cleanup(self) -> None
```

## `i_height_measuring_app_service.py`

Source: [src/applications/height_measuring/service/i_height_measuring_app_service.py](../../../../src/applications/height_measuring/service/i_height_measuring_app_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `abc`, `dataclasses`, `numpy`, `src.engine.robot.height_measuring.settings`, `typing`.

### `LaserDetectionResult`

```python
@dataclass
class LaserDetectionResult:
```

Declared fields/defaults:

```python
ok: bool
message: str
pixel_coords: Optional[tuple[float, float]] = None
height_mm: Optional[float] = None
debug_image: Optional[np.ndarray] = field(default=None, repr=False)
mask: Optional[np.ndarray] = field(default=None, repr=False)
```

### `IHeightMeasuringAppService`

```python
class IHeightMeasuringAppService(ABC):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def run_calibration(self) -> tuple[bool, str]
```

```python
@abstractmethod
def is_calibrated(self) -> bool
```

```python
@abstractmethod
def get_calibration_info(self) -> Optional[dict]
```

```python
@abstractmethod
def get_settings(self) -> HeightMeasuringModuleSettings
```

```python
@abstractmethod
def save_settings(self, settings: HeightMeasuringModuleSettings) -> tuple[bool, str]
```

```python
@abstractmethod
def get_latest_frame(self) -> Optional[np.ndarray]
```

```python
@abstractmethod
def reload_calibration(self) -> None
```

```python
@abstractmethod
def laser_on(self) -> tuple[bool, str]
```

```python
@abstractmethod
def laser_off(self) -> tuple[bool, str]
```

```python
@abstractmethod
def detect_once(self) -> LaserDetectionResult
```

```python
@abstractmethod
def cleanup(self) -> None
```

```python
@abstractmethod
def cancel_calibration(self) -> None
```

## `stub_height_measuring_app_service.py`

Source: [src/applications/height_measuring/service/stub_height_measuring_app_service.py](../../../../src/applications/height_measuring/service/stub_height_measuring_app_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `cv2`, `numpy`, `src.applications.height_measuring.service.i_height_measuring_app_service`, `src.engine.robot.height_measuring.settings`, `typing`.

### `StubHeightMeasuringAppService`

```python
class StubHeightMeasuringAppService(IHeightMeasuringAppService):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def run_calibration(self) -> tuple[bool, str]
```

```python
def is_calibrated(self) -> bool
```

```python
def get_calibration_info(self) -> Optional[dict]
```

```python
def get_settings(self) -> HeightMeasuringModuleSettings
```

```python
def save_settings(self, settings: HeightMeasuringModuleSettings) -> tuple[bool, str]
```

```python
def get_latest_frame(self) -> Optional[np.ndarray]
```

```python
def reload_calibration(self) -> None
```

```python
def laser_on(self) -> tuple[bool, str]
```

```python
def laser_off(self) -> tuple[bool, str]
```

```python
def detect_once(self) -> LaserDetectionResult
```

```python
def cleanup(self) -> None
```

```python
def cancel_calibration(self) -> None
```
