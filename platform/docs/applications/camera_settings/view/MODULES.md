# Module reference: `src/applications/camera_settings/view`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [camera_controls_widget.py](#camera_controls_widgetpy)
- [camera_devices_widget.py](#camera_devices_widgetpy)
- [camera_settings_schema.py](#camera_settings_schemapy)
- [camera_settings_view.py](#camera_settings_viewpy)
- [camera_tab.py](#camera_tabpy)

## `camera_controls_widget.py`

Source: [src/applications/camera_settings/view/camera_controls_widget.py](../../../../src/applications/camera_settings/view/camera_controls_widget.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtWidgets`, `pl_gui.utils.utils_widgets.SwitchButton`.

### `CameraControlsWidget`

```python
class CameraControlsWidget(QWidget):
```

Declared fields/defaults:

```python
raw_mode_toggled = pyqtSignal(bool)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, parent=None)
```

```python
def set_raw_mode(self, enabled: bool) -> None
```

## `camera_devices_widget.py`

Source: [src/applications/camera_settings/view/camera_devices_widget.py](../../../../src/applications/camera_settings/view/camera_devices_widget.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtGui`, `PyQt6.QtWidgets`, `__future__`, `cv2`, `pl_gui.settings.settings_view.styles`, `pl_gui.utils.utils_widgets.SwitchButton`, `pl_gui.utils.utils_widgets.camera_view`, `src.applications.camera_settings.service.i_camera_settings_service`.

### `CameraDevicesWidget`

```python
class CameraDevicesWidget(QWidget):
```

Declared fields/defaults:

```python
refresh_requested = pyqtSignal()
save_requested = pyqtSignal(dict, dict)
preview_requested = pyqtSignal(str, str)
preview_visibility_changed = pyqtSignal(bool)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, parent=None, *, device_control_mode: bool=False) -> None
```

```python
def set_camera_devices(self, state: CameraDevicesState) -> None
```

```python
def assignments(self) -> dict[str, str]
```

```python
def orientation_settings(self) -> dict[str, CameraOrientation]
```

```python
def set_preview_frame(self, frame) -> None
```

```python
def set_saved(self) -> None
```

```python
def set_error(self, message: str) -> None
```

```python
def showEvent(self, event) -> None
```

```python
def hideEvent(self, event) -> None
```

```python
def changeEvent(self, event) -> None
```

```python
def retranslateUi(self) -> None
```

## `camera_settings_schema.py`

Source: [src/applications/camera_settings/view/camera_settings_schema.py](../../../../src/applications/camera_settings/view/camera_settings_schema.py).

Imports (including optional/function-local imports; not a startup dependency list): `pl_gui.settings.settings_view.schema`.

Module declarations (expressions are shown without evaluating them):

```python
CORE_GROUP = SettingGroup('Core', [SettingField('index', 'Camera Index', 'spinbox', default=0, min_val=0, max_val=10, step=1), SettingField('width', 'Width', 'spinbox', default=1280, min_val=320, max_val=4096, step=1, step_options=[1, 10, 100]), SettingField('height', 'Height', 'spinbox', default=720, min_val=240, max_val=2160, step=1, step_options=[1, 10, 100]), SettingField('skip_frames', 'Skip Frames', 'spinbox', default=30, min_val=0, max_val=200, step=1, step_options=[1, 5, 10]), SettingField('capture_position_offset', 'Capture Position Offset', 'double_spinbox', default=-4.0, min_val=-500.0, max_val=500.0, step=0.5, decimals=1, step_options=[0.5, 1.0, 5.0])])
CONTOUR_GROUP = SettingGroup('Contour Detection', [SettingField('contour_detection', 'Enable Detection', 'toggle', default=True), SettingField('draw_contours', 'Draw Contours', 'toggle', default=True), SettingField('threshold', 'Threshold', 'spinbox', default=150, min_val=0, max_val=255, step=1, step_options=[1, 5, 10]), SettingField('threshold_pickup_area', 'Pickup Area Threshold', 'spinbox', default=200, min_val=0, max_val=255, step=1, step_options=[1, 5, 10]), SettingField('epsilon', 'Epsilon', 'double_spinbox', default=0.05, min_val=0.0, max_val=10.0, step=0.001, decimals=3, step_options=[0.001, 0.01, 0.1]), SettingField('min_contour_area', 'Min Contour Area', 'double_spinbox', default=1000.0, min_val=0.0, max_val=1000000.0, step=100, decimals=1, step_options=[100, 1000, 10000]), SettingField('max_contour_area', 'Max Contour Area', 'double_spinbox', default=10000000.0, min_val=0.0, max_val=100000000.0, step=10000, decimals=1, step_options=[10000, 100000, 1000000])])
PREPROCESSING_GROUP = SettingGroup('Preprocessing', [SettingField('gaussian_blur', 'Gaussian Blur', 'toggle', default=True), SettingField('blur_kernel_size', 'Blur Kernel Size', 'spinbox', default=3, min_val=1, max_val=99, step=2, step_options=[2]), SettingField('threshold_type', 'Threshold Type', 'combo', default='binary_inv', choices=['binary', 'binary_inv', 'trunc', 'tozero', 'tozero_inv']), SettingField('contour_smoothing_mode', 'Contour Smoothing', 'combo', default='none', choices=['none', 'moving_average', 'savgol']), SettingField('contour_smoothing_strength', 'Smoothing Strength', 'double_spinbox', default=5.0, min_val=0.0, max_val=25.0, step=1.0, decimals=1, step_options=[0.5, 1.0, 2.0, 5.0]), SettingField('dilate_enabled', 'Dilate', 'toggle', default=True), SettingField('dilate_kernel_size', 'Dilate Kernel', 'spinbox', default=3, min_val=1, max_val=99, step=2, step_options=[2]), SettingField('dilate_iterations', 'Dilate Iterations', 'spinbox', default=2, min_val=1, max_val=50, step=1, step_options=[1, 5]), SettingField('erode_enabled', 'Erode', 'toggle', default=True), SettingField('erode_kernel_size', 'Erode Kernel', 'spinbox', default=3, min_val=1, max_val=99, step=2, step_options=[2]), SettingField('erode_iterations', 'Erode Iterations', 'spinbox', default=4, min_val=1, max_val=50, step=1, step_options=[1, 5])])
BRIGHTNESS_GROUP = SettingGroup('Brightness Control', [SettingField('hardware_auto_exposure', 'Hardware Auto Exposure', 'toggle', default=False), SettingField('brightness_auto', 'Auto Adjust', 'toggle', default=True), SettingField('brightness_kp', 'Kp', 'double_spinbox', default=0.0, min_val=0.0, max_val=10.0, step=0.001, decimals=3, step_options=[0.001, 0.01, 0.1]), SettingField('brightness_ki', 'Ki', 'double_spinbox', default=0.2, min_val=0.0, max_val=10.0, step=0.001, decimals=3, step_options=[0.001, 0.01, 0.1]), SettingField('brightness_kd', 'Kd', 'double_spinbox', default=0.05, min_val=0.0, max_val=10.0, step=0.001, decimals=3, step_options=[0.001, 0.01, 0.1]), SettingField('target_brightness', 'Target Brightness', 'double_spinbox', default=200.0, min_val=0.0, max_val=255.0, step=1.0, decimals=1, step_options=[1, 5, 10])])
ARUCO_GROUP = SettingGroup('ArUco Detection', [SettingField('aruco_enabled', 'Enable Detection', 'toggle', default=False), SettingField('aruco_dictionary', 'Dictionary', 'combo', default='DICT_4X4_1000', choices=_ARUCO_DICTS), SettingField('aruco_flip_image', 'Flip Image', 'toggle', default=False)])
```

## `camera_settings_view.py`

Source: [src/applications/camera_settings/view/camera_settings_view.py](../../../../src/applications/camera_settings/view/camera_settings_view.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtGui`, `PyQt6.QtWidgets`, `cv2`, `pl_gui.settings.settings_view.settings_view`, `pl_gui.utils.utils_widgets.camera_view`, `src.applications.base.app_styles`, `src.applications.base.i_application_view`, `src.applications.camera_settings.view.camera_controls_widget`, `src.applications.camera_settings.view.camera_devices_widget`.

### `CameraSettingsView`

```python
class CameraSettingsView(IApplicationView):
```

Declared fields/defaults:

```python
SHOW_JOG_WIDGET = True
JOG_FRAME_SELECTOR_ENABLED = True
raw_mode_toggled = pyqtSignal(bool)
value_changed_signal = pyqtSignal(str, object, str)
save_requested = pyqtSignal(dict)
vision_state_changed = pyqtSignal(str)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, settings_view: SettingsView, camera_devices_widget: CameraDevicesWidget | None, parent=None)
```

```python
def setup_ui(self) -> None
```

```python
def clean_up(self) -> None
```

```python
def set_vision_state(self, state: str) -> None
```

```python
def update_camera_view(self, image) -> None
```

```python
def update_threshold_view(self, image) -> None
```

```python
@property
def preview_label(self) -> CameraView | None
```

```python
@property
def controls(self) -> CameraControlsWidget
```

```python
@property
def settings_view(self) -> SettingsView
```

```python
@property
def camera_devices_widget(self) -> CameraDevicesWidget | None
```

## `camera_tab.py`

Source: [src/applications/camera_settings/view/camera_tab.py](../../../../src/applications/camera_settings/view/camera_tab.py).

Imports (including optional/function-local imports; not a startup dependency list): `pl_gui.settings.settings_view.settings_view`, `src.applications.base.collapsible_settings_view`, `src.applications.base.keyboard_settings_view`, `src.applications.camera_settings.view.camera_devices_widget`, `src.applications.camera_settings.view.camera_settings_schema`, `src.applications.camera_settings.view.camera_settings_view`, `typing`.

### `_keyboard_collapsible_group`

```python
def _keyboard_collapsible_group(schema) -> CollapsibleGroup
```

### `camera_tab_factory`

```python
def camera_tab_factory(mapper: Callable, parent=None, show_camera_devices: bool=False) -> Tuple[CameraSettingsView, SettingsView]
```
