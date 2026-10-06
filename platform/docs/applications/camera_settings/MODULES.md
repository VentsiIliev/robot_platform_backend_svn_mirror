# Module reference: `src/applications/camera_settings`

[Package guide](README.md) · [Complete source index](../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [camera_settings_data.py](#camera_settings_datapy)
- [camera_settings_factory.py](#camera_settings_factorypy)
- [example_usage.py](#example_usagepy)
- [mapper.py](#mapperpy)

## `__init__.py`

Source: [src/applications/camera_settings/__init__.py](../../../src/applications/camera_settings/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.camera_settings.service.i_camera_settings_service`, `src.applications.camera_settings.service.stub_camera_settings_service`.

Package-level import/export surface:

```python
from src.applications.camera_settings.service.i_camera_settings_service import ICameraSettingsService
from src.applications.camera_settings.service.stub_camera_settings_service import StubCameraSettingsService
```

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `camera_settings_data.py`

Source: [src/applications/camera_settings/camera_settings_data.py](../../../src/applications/camera_settings/camera_settings_data.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`, `typing`.

### `CameraSettingsData`

```python
@dataclass
class CameraSettingsData:
```

Declared fields/defaults:

```python
index: int = 0
width: int = 1280
height: int = 720
skip_frames: int = 30
capture_position_offset: float = -4.0
contour_detection: bool = True
draw_contours: bool = True
threshold: int = 150
threshold_pickup_area: int = 200
epsilon: float = 0.05
min_contour_area: float = 1000.0
max_contour_area: float = 10000000.0
gaussian_blur: bool = True
blur_kernel_size: int = 3
threshold_type: str = 'binary_inv'
contour_smoothing_mode: str = 'none'
contour_smoothing_strength: float = 5.0
dilate_enabled: bool = True
dilate_kernel_size: int = 3
dilate_iterations: int = 2
erode_enabled: bool = True
erode_kernel_size: int = 3
erode_iterations: int = 4
hardware_auto_exposure: bool = False
brightness_auto: bool = True
brightness_kp: float = 0.0
brightness_ki: float = 0.2
brightness_kd: float = 0.05
target_brightness: float = 200.0
brightness_area_points: List[Tuple[int, int]] = field(default_factory=list)
aruco_enabled: bool = False
aruco_dictionary: str = 'DICT_4X4_1000'
aruco_flip_image: bool = False
```

## `camera_settings_factory.py`

Source: [src/applications/camera_settings/camera_settings_factory.py](../../../src/applications/camera_settings/camera_settings_factory.py).

Imports (including optional/function-local imports; not a startup dependency list): `logging`, `src.applications.base.application_factory`, `src.applications.camera_settings.controller.camera_settings_controller`, `src.applications.camera_settings.mapper`, `src.applications.camera_settings.model.camera_settings_model`, `src.applications.camera_settings.service.i_camera_settings_service`, `src.applications.camera_settings.view.camera_tab`, `src.engine.core.i_messaging_service`.

### `CameraSettingsFactory`

```python
class CameraSettingsFactory:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def build(self, service: ICameraSettingsService, messaging: IMessagingService, jog_service=None, show_camera_devices: bool=False)
```

## `example_usage.py`

Source: [src/applications/camera_settings/example_usage.py](../../../src/applications/camera_settings/example_usage.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtWidgets`, `src.applications.camera_settings`, `src.applications.camera_settings.camera_settings_factory`, `src.engine.core.messaging_service`, `sys`.

### `run_standalone`

```python
def run_standalone()
```

## `mapper.py`

Source: [src/applications/camera_settings/mapper.py](../../../src/applications/camera_settings/mapper.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`, `src.applications.camera_settings.camera_settings_data`, `typing`.

### `CameraSettingsMapper`

```python
class CameraSettingsMapper:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@staticmethod
def from_json(data: dict) -> CameraSettingsData
```

```python
@staticmethod
def to_json(data: CameraSettingsData) -> dict
```

```python
@staticmethod
def to_flat_dict(data: CameraSettingsData) -> dict
```

```python
@staticmethod
def from_flat_dict(flat: dict, base: CameraSettingsData) -> CameraSettingsData
```
