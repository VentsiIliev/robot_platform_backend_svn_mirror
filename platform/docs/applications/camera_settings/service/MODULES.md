# Module reference: `src/applications/camera_settings/service`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [camera_settings_application_service.py](#camera_settings_application_servicepy)
- [i_camera_settings_service.py](#i_camera_settings_servicepy)
- [stub_camera_settings_service.py](#stub_camera_settings_servicepy)

## `camera_settings_application_service.py`

Source: [src/applications/camera_settings/service/camera_settings_application_service.py](../../../../src/applications/camera_settings/service/camera_settings_application_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `logging`, `pathlib`, `src.applications.camera_settings.camera_settings_data`, `src.applications.camera_settings.mapper`, `src.applications.camera_settings.service.i_camera_settings_service`, `src.engine.common_settings_ids`, `src.engine.repositories.interfaces.i_settings_service`, `src.engine.vision.camera_device_settings`, `src.engine.vision.camera_settings_serializer`, `src.engine.vision.frame_orientation`, `src.engine.vision.i_vision_service`, `typing`.

### `CameraSettingsApplicationService`

```python
class CameraSettingsApplicationService(ICameraSettingsService):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, settings_service: ISettingsService, vision_service: IVisionService, work_area_service=None, camera_devices_settings_key=None, camera_orientation_setter: Callable[[str, bool, bool, int], None] | None=None)
```

```python
def load_settings(self) -> CameraSettingsData
```

```python
def save_settings(self, settings: CameraSettingsData) -> None
```

```python
def set_raw_mode(self, enabled: bool) -> None
```

```python
def update_settings(self, settings: dict) -> tuple[bool, str]
```

```python
def save_work_area(self, area_type: str, points: List[Tuple[float, float]]) -> tuple[bool, str]
```

```python
def get_work_area(self, area_type: str) -> tuple[bool, str, List[Tuple[float, float]]]
```

```python
def load_camera_devices(self) -> CameraDevicesState
```

```python
def save_camera_devices(self, assignments: dict[str, str], orientation: dict[str, CameraOrientation]) -> None
```

## `i_camera_settings_service.py`

Source: [src/applications/camera_settings/service/i_camera_settings_service.py](../../../../src/applications/camera_settings/service/i_camera_settings_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `abc`, `dataclasses`, `src.applications.camera_settings.camera_settings_data`, `typing`.

### `CameraDeviceOption`

```python
@dataclass(frozen=True)
class CameraDeviceOption:
```

Declared fields/defaults:

```python
device: str
capture_node: str
connected: bool
```

### `CameraOrientation`

```python
@dataclass(frozen=True)
class CameraOrientation:
```

Capture orientation for one camera role. Rotation is always applied first, then the mirror, so ``flip_vertical`` keeps meaning "mirror the image as displayed" for any rotation.

Declared fields/defaults:

```python
VALID_ROTATIONS: ClassVar[tuple[int, ...]] = (0, 90, 180, 270)
flip_horizontal: bool = False
flip_vertical: bool = False
rotate_degrees: int = 0
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@property
def transposes_frame(self) -> bool
```

### `CameraDevicesState`

```python
@dataclass(frozen=True)
class CameraDevicesState:
```

Declared fields/defaults:

```python
assignments: dict[str, str]
options: tuple[CameraDeviceOption, ...]
orientation: dict[str, CameraOrientation] = field(default_factory=dict)
```

### `ICameraSettingsService`

```python
class ICameraSettingsService(ABC):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def load_settings(self) -> CameraSettingsData
```

```python
@abstractmethod
def save_settings(self, settings: CameraSettingsData) -> None
```

```python
@abstractmethod
def set_raw_mode(self, enabled: bool) -> None
```

```python
@abstractmethod
def update_settings(self, settings: dict) -> tuple[bool, str]
```

```python
@abstractmethod
def save_work_area(self, area_type: str, points: List[Tuple[float, float]]) -> tuple[bool, str]
```

```python
@abstractmethod
def get_work_area(self, area_type: str) -> tuple[bool, str, List[Tuple[float, float]]]
```

```python
@abstractmethod
def load_camera_devices(self) -> CameraDevicesState
```

```python
@abstractmethod
def save_camera_devices(self, assignments: dict[str, str], orientation: dict[str, CameraOrientation]) -> None
```

## `stub_camera_settings_service.py`

Source: [src/applications/camera_settings/service/stub_camera_settings_service.py](../../../../src/applications/camera_settings/service/stub_camera_settings_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `logging`, `src.applications.camera_settings.camera_settings_data`, `src.applications.camera_settings.service.i_camera_settings_service`.

### `StubCameraSettingsService`

```python
class StubCameraSettingsService(ICameraSettingsService):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self)
```

```python
def load_settings(self) -> CameraSettingsData
```

```python
def save_settings(self, settings: CameraSettingsData) -> None
```

```python
def set_raw_mode(self, enabled: bool) -> None
```

```python
def update_settings(self, settings: dict) -> tuple[bool, str]
```

```python
def save_work_area(self, area_type: str, points) -> tuple[bool, str]
```

```python
def get_work_area(self, area_type: str) -> tuple[bool, str, list]
```

```python
def load_camera_devices(self) -> CameraDevicesState
```

```python
def save_camera_devices(self, assignments: dict[str, str], orientation: dict[str, CameraOrientation]) -> None
```
