# Module reference: `src/applications/calibration_settings/view`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [calibration_settings_schema.py](#calibration_settings_schemapy)
- [calibration_settings_view.py](#calibration_settings_viewpy)
- [workobject_calibration_tab.py](#workobject_calibration_tabpy)

## `calibration_settings_schema.py`

Source: [src/applications/calibration_settings/view/calibration_settings_schema.py](../../../../src/applications/calibration_settings/view/calibration_settings_schema.py).

Imports (including optional/function-local imports; not a startup dependency list): `pl_gui.settings.settings_view.schema`, `src.applications.height_measuring.view.height_measuring_schema`, `src.applications.robot_settings.view.robot_settings_schema`.

Module declarations (expressions are shown without evaluating them):

```python
VISION_CALIBRATION_GROUP = SettingGroup('Camera Calibration', [SettingField('calib_vision_chessboard_width', 'Chessboard Width', 'spinbox', default=32, min_val=3, max_val=50, step=1), SettingField('calib_vision_chessboard_height', 'Chessboard Height', 'spinbox', default=20, min_val=3, max_val=50, step=1), SettingField('calib_vision_square_size_mm', 'Square Size', 'double_spinbox', default=25.0, min_val=1.0, max_val=200.0, step=0.5, decimals=1, suffix=' mm', step_options=[0.5, 1.0, 5.0]), SettingField('calib_vision_reference_board_mode', 'Reference Board Mode', 'combo', default='auto', choices=['auto', 'charuco', 'chessboard']), SettingField('calib_vision_charuco_board_width', 'ChArUco Width', 'spinbox', default=0, min_val=0, max_val=80, step=1), SettingField('calib_vision_charuco_board_height', 'ChArUco Height', 'spinbox', default=0, min_val=0, max_val=80, step=1), SettingField('calib_vision_charuco_square_size_mm', 'ChArUco Square Size', 'double_spinbox', default=0.0, min_val=0.0, max_val=200.0, step=0.5, decimals=1, suffix=' mm', step_options=[0.5, 1.0, 5.0]), SettingField('calib_vision_charuco_marker_size_mm', 'ChArUco Marker Size', 'double_spinbox', default=0.0, min_val=0.0, max_val=200.0, step=0.5, decimals=1, suffix=' mm', step_options=[0.5, 1.0, 5.0]), SettingField('calib_vision_skip_frames', 'Skip Frames', 'spinbox', default=30, min_val=1, max_val=200, step=1, step_options=[1, 5, 10])])
COORDINATE_CALIBRATION_GROUP = SettingGroup('Coordinate Calibration', [SettingField('coordinate_calibration_mode', 'Calibration Mode', 'combo', default='global', choices=['global', 'per_area']), SettingField('calibration_target_work_area', 'Calibration Destination', 'combo', default='global', choices=['global']), SettingField('coordinate_calibration_profiles', 'Named Profiles (JSON)', 'line_edit', default='{}'), SettingField('work_area_calibration_profiles', 'Work Area Assignments (JSON)', 'line_edit', default='{}')])
__all__ = ['VISION_CALIBRATION_GROUP', 'COORDINATE_CALIBRATION_GROUP', 'CALIBRATION_ADAPTIVE_GROUP', 'CALIBRATION_MARKER_GROUP', 'CALIBRATION_AXIS_MAPPING_GROUP', 'CALIBRATION_CAMERA_TCP_GROUP', 'LASER_DETECTION_GROUP', 'LASER_CALIBRATION_GROUP', 'HEIGHT_MAPPING_GROUP']
```

## `calibration_settings_view.py`

Source: [src/applications/calibration_settings/view/calibration_settings_view.py](../../../../src/applications/calibration_settings/view/calibration_settings_view.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtWidgets`, `copy`, `src.applications.base.i_application_view`, `src.applications.base.keyboard_settings_view`, `src.applications.calibration_settings.view.calibration_settings_schema`, `src.applications.calibration_settings.view.workobject_calibration_tab`.

### `CalibrationSettingsView`

```python
class CalibrationSettingsView(IApplicationView):
```

Declared fields/defaults:

```python
workobject_capture_requested = pyqtSignal(str)
workobject_solve_requested = pyqtSignal(int, str)
workobject_save_requested = pyqtSignal(int, str)
save_requested = None
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, parent=None, work_area_ids=None)
```

```python
def setup_ui(self) -> None
```

```python
def set_workobject_capture(self, point: str, pose) -> None
```

```python
def set_height_settings_available(self, available: bool) -> None
```

Show laser and height settings only for systems that supply them.

```python
def set_workobject_result(self, ok: bool, message: str, payload: dict | None=None) -> None
```

## `workobject_calibration_tab.py`

Source: [src/applications/calibration_settings/view/workobject_calibration_tab.py](../../../../src/applications/calibration_settings/view/workobject_calibration_tab.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtWidgets`, `__future__`, `pl_gui.settings.settings_view.styles`, `src.applications.base.widgets.custom_virtual_keyboard`, `src.applications.base.widgets.keyboard_number_field`.

### `_fmt_pose`

```python
def _fmt_pose(values) -> str
```

### `WorkObjectCalibrationTab`

```python
class WorkObjectCalibrationTab(QWidget):
```

Declared fields/defaults:

```python
capture_requested = pyqtSignal(str)
solve_requested = pyqtSignal(int, str)
save_requested = pyqtSignal(int, str)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, parent=None)
```

```python
def changeEvent(self, event) -> None
```

```python
def user_id(self) -> int
```

```python
def name(self) -> str
```

```python
def set_capture_result(self, point: str, pose) -> None
```

```python
def set_result(self, ok: bool, message: str, payload: dict | None=None) -> None
```
