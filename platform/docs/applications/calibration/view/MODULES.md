# Module reference: `src/applications/calibration/view`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [calibration_controls_panel.py](#calibration_controls_panelpy)
- [calibration_phase_tabs.py](#calibration_phase_tabspy)
- [calibration_preview_panel.py](#calibration_preview_panelpy)
- [calibration_view.py](#calibration_viewpy)
- [compact_settings_group.py](#compact_settings_grouppy)
- [depth_map_dialog.py](#depth_map_dialogpy)
- [intrinsic_auto_capture_widget.py](#intrinsic_auto_capture_widgetpy)
- [robot_calibration_preview_dialog.py](#robot_calibration_preview_dialogpy)

## `__init__.py`

Source: [src/applications/calibration/view/__init__.py](../../../../src/applications/calibration/view/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `calibration_controls_panel.py`

Source: [src/applications/calibration/view/calibration_controls_panel.py](../../../../src/applications/calibration/view/calibration_controls_panel.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtWidgets`, `__future__`, `pl_gui.settings.settings_view.styles`, `pl_gui.utils.utils_widgets.MaterialButton`, `src.applications.base.app_styles`, `src.applications.base.widgets.keyboard_number_field`, `src.applications.calibration.view.calibration_phase_tabs`, `src.applications.calibration.view.intrinsic_auto_capture_widget`, `src.applications.calibration_settings.view.calibration_settings_schema`, `src.applications.calibration_settings.view.workobject_calibration_tab`.

### `CalibrationControlsPanel`

```python
class CalibrationControlsPanel(QWidget):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, parent=None, *, show_laser_tab: bool=True, show_height_mapping_tab: bool=True)
```

```python
def set_height_mapping_content(self, widget: QWidget) -> None
```

```python
def iter_save_settings_buttons(self)
```

```python
def set_settings_values(self, flat: dict) -> None
```

```python
def get_settings_values(self) -> dict
```

```python
def toggle_crosshair(self) -> bool
```

```python
def toggle_magnifier(self) -> bool
```

```python
def set_stop_calibration_enabled(self, enabled: bool) -> None
```

```python
def set_test_calibration_enabled(self, enabled: bool) -> None
```

```python
def set_camera_tcp_offset_enabled(self, enabled: bool) -> None
```

```python
def set_camera_z_shift_enabled(self, enabled: bool) -> None
```

```python
def set_tool_tcp_result(self, result: dict | None) -> None
```

```python
def set_measure_marker_heights_enabled(self, enabled: bool) -> None
```

```python
def set_depth_map_enabled(self, enabled: bool) -> None
```

```python
def set_laser_actions_enabled(self, enabled: bool) -> None
```

```python
def set_enabled(self, enabled: bool) -> None
```

## `calibration_phase_tabs.py`

Source: [src/applications/calibration/view/calibration_phase_tabs.py](../../../../src/applications/calibration/view/calibration_phase_tabs.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtWidgets`, `__future__`, `pl_gui.settings.settings_view.styles`, `pl_gui.utils.utils_widgets.MaterialButton`, `src.applications.base.app_styles`, `src.applications.base.widgets.keyboard_number_field`, `src.applications.calibration.view.compact_settings_group`, `src.applications.calibration.view.intrinsic_auto_capture_widget`.

### `_BaseCalibrationTab`

```python
class _BaseCalibrationTab(QWidget):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, title: str, hint: str, parent=None)
```

```python
def add_widget(self, widget: QWidget) -> None
```

```python
def add_layout(self, layout) -> None
```

```python
def add_divider(self) -> None
```

```python
def add_settings_groups(self, schemas: list) -> None
```

```python
def add_settings_page(self, title: str, widget: QWidget) -> int
```

```python
def add_save_button(self) -> QPushButton
```

```python
def changeEvent(self, event) -> None
```

```python
def set_settings_values(self, flat: dict) -> None
```

```python
def get_settings_values(self) -> dict
```

### `SystemCalibrationTab`

```python
class SystemCalibrationTab(_BaseCalibrationTab):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, sequence_btn: QWidget, stop_btn: QWidget, parent=None)
```

### `CameraCalibrationTab`

```python
class CameraCalibrationTab(_BaseCalibrationTab):
```

Declared fields/defaults:

```python
auto_capture_config_saved = pyqtSignal(object)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, capture_btn: QWidget, crosshair_btn: QWidget, magnifier_btn: QWidget, calibrate_camera_btn: QWidget, auto_capture_widget: IntrinsicAutoCaptureWidget | None, settings_schemas: list, parent=None)
```

### `RobotCalibrationTab`

```python
class RobotCalibrationTab(_BaseCalibrationTab):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, calibrate_robot_btn: QWidget, calibrate_tcp_btn: QWidget, calibrate_z_shift_btn: QWidget, test_btn: QWidget, settings_schemas: list, parent=None)
```

### `ToolTcpCalibrationTab`

```python
class ToolTcpCalibrationTab(_BaseCalibrationTab):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, tool_spin: KeyboardNumberField, start_btn: QWidget, capture_btn: QWidget, solve_btn: QWidget, save_btn: QWidget, clear_btn: QWidget, result_label: QLabel, parent=None)
```

### `LaserCalibrationTab`

```python
class LaserCalibrationTab(_BaseCalibrationTab):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, calibrate_laser_btn: QWidget, detect_laser_btn: QWidget, settings_schemas: list, parent=None)
```

### `HeightMappingTab`

```python
class HeightMappingTab(_BaseCalibrationTab):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, verify_saved_model_btn: QWidget, settings_schemas: list, height_mapping_content: QWidget | None=None, parent=None)
```

```python
def set_height_mapping_content(self, widget: QWidget) -> None
```

## `calibration_preview_panel.py`

Source: [src/applications/calibration/view/calibration_preview_panel.py](../../../../src/applications/calibration/view/calibration_preview_panel.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtGui`, `PyQt6.QtWidgets`, `__future__`, `cv2`, `numpy`, `pl_gui.settings.settings_view.styles`, `pl_gui.utils.utils_widgets.MaterialButton`, `pl_gui.utils.utils_widgets.camera_view`, `src.applications.base.app_styles`, `src.applications.base.widgets.keyboard_number_field`, `src.shared_contracts.declarations`.

### `_GridCameraView`

```python
class _GridCameraView(CameraView):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, parent=None)
```

```python
def set_grid_points(self, points: list[tuple[float, float]], *, point_labels: list[str] | None=None, point_statuses: dict[str, str] | None=None) -> None
```

```python
def set_substitute_regions(self, polygons: dict[str, list[tuple[float, float]]]) -> None
```

### `CalibrationAreaGridPanel`

```python
class CalibrationAreaGridPanel(QWidget):
```

Declared fields/defaults:

```python
work_area_changed = pyqtSignal(str)
measurement_area_changed = pyqtSignal()
generate_area_grid_requested = pyqtSignal()
verify_area_grid_requested = pyqtSignal()
measure_area_grid_requested = pyqtSignal()
view_depth_map_requested = pyqtSignal()
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, preview_label: _GridCameraView, work_area_definitions: list[WorkAreaDefinition] | None=None, parent=None)
```

```python
def set_measure_area_grid_enabled(self, enabled: bool) -> None
```

```python
def set_verify_area_grid_busy(self, busy: bool, current: int=0, total: int=0) -> None
```

```python
def set_depth_map_enabled(self, enabled: bool) -> None
```

```python
def set_enabled(self, enabled: bool) -> None
```

```python
def current_work_area_id(self) -> str
```

```python
def set_current_work_area_id(self, area_id: str) -> None
```

```python
def current_height_mapping_area_key(self) -> str | None
```

```python
def set_work_area_options(self, definitions: list[WorkAreaDefinition]) -> None
```

```python
def get_measurement_area_corners(self) -> list[tuple[float, float]]
```

```python
def clear_measurement_area(self) -> None
```

```python
def set_measurement_area_corners(self, area_id: str, corners: list[tuple[float, float]]) -> None
```

```python
def set_generated_grid_points(self, points: list[tuple[float, float]], *, point_labels: list[str] | None=None, point_statuses: dict[str, str] | None=None) -> None
```

```python
def set_substitute_regions(self, polygons: dict[str, list[tuple[float, float]]]) -> None
```

```python
def get_area_grid_shape(self) -> tuple[int, int]
```

### `CalibrationPreviewPanel`

```python
class CalibrationPreviewPanel(QWidget):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, work_area_definitions: list[WorkAreaDefinition] | None=None, parent=None)
```

```python
def add_preview_action(self, button: QWidget) -> None
```

```python
def add_stop_action(self, button: QWidget) -> None
```

```python
def set_robot_calibration_status(self, payload: dict | None) -> None
```

## `calibration_view.py`

Source: [src/applications/calibration/view/calibration_view.py](../../../../src/applications/calibration/view/calibration_view.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtGui`, `PyQt6.QtWidgets`, `__future__`, `cv2`, `dataclasses`, `numpy`, `pl_gui.settings.settings_view.styles`, `src.applications.base.i_application_view`, `src.applications.base.styled_message_box`, `src.applications.base.widgets.keyboard_number_field`, `src.applications.calibration.service.i_calibration_service`, `src.applications.calibration.view.calibration_controls_panel`, `src.applications.calibration.view.calibration_preview_panel`, `src.applications.calibration.view.robot_calibration_preview_dialog`, `src.applications.calibration_settings.calibration_settings_data`, `src.applications.intrinsic_calibration_capture.service.i_intrinsic_capture_service`, `src.shared_contracts.declarations`.

### `ZShiftCalibrationDialogResult`

```python
@dataclass(frozen=True)
class ZShiftCalibrationDialogResult:
```

Declared fields/defaults:

```python
marker_id: int
samples: int
z_step_mm: float
settle_time_s: float
```

### `TcpOffsetCalibrationDialogResult`

```python
@dataclass(frozen=True)
class TcpOffsetCalibrationDialogResult:
```

Declared fields/defaults:

```python
marker_id: int
rotation_step_deg: float
iterations: int
approach_z: float
approach_rx: float
approach_ry: float
approach_rz: float
velocity: int
acceleration: int
settle_time_s: float
recenter_max_iterations: int
recenter_stability_wait_s: float
recenter_alignment_threshold_mm: float
```

### `_CalibrationAreaDialog`

```python
class _CalibrationAreaDialog(QDialog):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, title: str, prompt: str, options: list[tuple[str, str]], current_id: str, parent=None)
```

```python
def area_id(self) -> str
```

### `_ZShiftCalibrationDialog`

```python
class _ZShiftCalibrationDialog(QDialog):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, *, marker_id: int, samples: int, z_step_mm: float, settle_time_s: float, parent=None)
```

```python
def get_result(self) -> ZShiftCalibrationDialogResult
```

### `_TcpOffsetCalibrationDialog`

```python
class _TcpOffsetCalibrationDialog(QDialog):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, *, marker_id: int, rotation_step_deg: float, iterations: int, approach_z: float, approach_rx: float, approach_ry: float, approach_rz: float, velocity: int, acceleration: int, settle_time_s: float, recenter_max_iterations: int, recenter_stability_wait_s: float, recenter_alignment_threshold_mm: float, parent=None)
```

```python
def get_result(self) -> TcpOffsetCalibrationDialogResult
```

### `CalibrationView`

```python
class CalibrationView(IApplicationView):
```

Declared fields/defaults:

```python
SHOW_JOG_WIDGET = True
JOG_FRAME_SELECTOR_ENABLED = True
capture_requested = pyqtSignal()
calibrate_camera_requested = pyqtSignal()
intrinsic_auto_capture_requested = pyqtSignal()
intrinsic_auto_capture_stop_requested = pyqtSignal()
intrinsic_capture_config_save_requested = pyqtSignal(object)
calibrate_robot_requested = pyqtSignal()
calibrate_sequence_requested = pyqtSignal()
calibrate_camera_tcp_offset_requested = pyqtSignal()
calibrate_camera_z_shift_requested = pyqtSignal()
tool_tcp_start_requested = pyqtSignal(int)
tool_tcp_capture_requested = pyqtSignal()
tool_tcp_solve_requested = pyqtSignal()
tool_tcp_save_requested = pyqtSignal()
tool_tcp_clear_requested = pyqtSignal()
workobject_capture_requested = pyqtSignal(str)
workobject_solve_requested = pyqtSignal(int, str)
workobject_save_requested = pyqtSignal(int, str)
calibrate_laser_requested = pyqtSignal()
detect_laser_requested = pyqtSignal()
stop_calibration_requested = pyqtSignal()
test_calibration_requested = pyqtSignal()
measure_marker_heights_requested = pyqtSignal()
generate_area_grid_requested = pyqtSignal()
verify_area_grid_requested = pyqtSignal()
measure_area_grid_requested = pyqtSignal()
view_depth_map_requested = pyqtSignal()
verify_saved_model_requested = pyqtSignal()
save_calibration_settings_requested = pyqtSignal(dict)
work_area_changed = pyqtSignal(str)
measurement_area_changed = pyqtSignal()
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, work_area_definitions: list[WorkAreaDefinition] | None=None, parent=None, *, show_laser_tab: bool=True, show_height_mapping_tab: bool=True)
```

```python
def setup_ui(self) -> None
```

```python
def retranslateUi(self) -> None
```

```python
def can_close(self) -> bool
```

```python
def clean_up(self) -> None
```

```python
def set_stop_calibration_enabled(self, enabled: bool) -> None
```

```python
def set_test_calibration_enabled(self, enabled: bool) -> None
```

```python
def set_camera_tcp_offset_enabled(self, enabled: bool) -> None
```

```python
def set_camera_z_shift_enabled(self, enabled: bool) -> None
```

```python
def set_tool_tcp_result(self, result: dict | None) -> None
```

```python
def set_workobject_capture(self, point: str, pose) -> None
```

```python
def set_workobject_result(self, ok: bool, message: str, payload: dict | None=None) -> None
```

```python
def prompt_z_shift_calibration_config(self, *, marker_id: int=4, samples: int=10, z_step_mm: float=-1.0, settle_time_s: float=0.3) -> ZShiftCalibrationDialogResult | None
```

```python
def prompt_tcp_offset_calibration_config(self, *, marker_id: int, rotation_step_deg: float, iterations: int, approach_z: float, approach_rx: float, approach_ry: float, approach_rz: float, velocity: int, acceleration: int, settle_time_s: float, recenter_max_iterations: int, recenter_stability_wait_s: float, recenter_alignment_threshold_mm: float) -> TcpOffsetCalibrationDialogResult | None
```

```python
def set_measure_marker_heights_enabled(self, enabled: bool) -> None
```

```python
def set_measure_area_grid_enabled(self, enabled: bool) -> None
```

```python
def set_verify_area_grid_busy(self, busy: bool, current: int=0, total: int=0) -> None
```

```python
def set_depth_map_enabled(self, enabled: bool) -> None
```

```python
def set_laser_actions_enabled(self, enabled: bool) -> None
```

```python
def load_calibration_settings(self, _settings: CalibrationSettingsData | None, flat: dict) -> None
```

```python
def set_intrinsic_capture_config(self, config: IntrinsicCaptureConfig) -> None
```

```python
def get_intrinsic_capture_config(self) -> IntrinsicCaptureConfig
```

```python
def set_intrinsic_auto_capture_running(self, running: bool) -> None
```

```python
def update_camera_view(self, image) -> None
```

```python
def set_robot_calibration_status(self, payload: dict | None) -> None
```

```python
def append_log(self, message: str) -> None
```

```python
def clear_log(self) -> None
```

```python
def set_buttons_enabled(self, enabled: bool) -> None
```

```python
def confirm_robot_calibration_preview(self, preview: RobotCalibrationPreview) -> bool
```

```python
def prompt_robot_calibration_area(self, current_area_id: str='global', configured_area_ids: set[str] | None=None) -> str | None
```

```python
def prompt_camera_tcp_calibration_area(self, current_area_id: str='global') -> str | None
```

```python
@property
def work_area_definitions(self) -> list[WorkAreaDefinition]
```

```python
def current_work_area_id(self) -> str
```

```python
def set_current_work_area_id(self, area_id: str) -> None
```

```python
def current_height_mapping_area_key(self) -> str | None
```

```python
def set_work_area_options(self, definitions: list[WorkAreaDefinition]) -> None
```

```python
def get_measurement_area_corners(self) -> list[tuple[float, float]]
```

```python
def clear_measurement_area(self) -> None
```

```python
def set_measurement_area_corners(self, area_id: str, corners: list[tuple[float, float]]) -> None
```

```python
def set_generated_grid_points(self, points: list[tuple[float, float]], *, point_labels: list[str] | None=None, point_statuses: dict[str, str] | None=None) -> None
```

```python
def set_substitute_regions(self, polygons: dict[str, list[tuple[float, float]]]) -> None
```

```python
def get_area_grid_shape(self) -> tuple[int, int]
```

## `compact_settings_group.py`

Source: [src/applications/calibration/view/compact_settings_group.py](../../../../src/applications/calibration/view/compact_settings_group.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtWidgets`, `__future__`, `pl_gui.settings.settings_view.schema`, `pl_gui.settings.settings_view.styles`, `src.applications.base.widgets.custom_virtual_keyboard`, `src.applications.base.widgets.keyboard_number_field`.

### `_IntListEditor`

```python
class _IntListEditor(QWidget):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, field: SettingField, parent=None)
```

```python
def get_ids(self) -> list[int]
```

```python
def set_ids(self, value) -> None
```

### `CompactSettingsGroup`

```python
class CompactSettingsGroup(QWidget):
```

Compact editor for calibration SettingGroup values.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, schema: SettingGroup, parent=None)
```

```python
def set_values(self, values: dict) -> None
```

```python
def get_values(self) -> dict
```

## `depth_map_dialog.py`

Source: [src/applications/calibration/view/depth_map_dialog.py](../../../../src/applications/calibration/view/depth_map_dialog.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtWidgets`, `matplotlib`, `matplotlib.backends.backend_qtagg`, `matplotlib.figure`, `mpl_toolkits.mplot3d`, `numpy`, `scipy.interpolate`, `src.engine.robot.height_measuring.area_grid_height_model`, `src.engine.robot.height_measuring.piecewise_bilinear_height_model`.

### `DepthMapDialog`

```python
class DepthMapDialog(QDialog):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, depth_map_data, parent=None)
```

## `intrinsic_auto_capture_widget.py`

Source: [src/applications/calibration/view/intrinsic_auto_capture_widget.py](../../../../src/applications/calibration/view/intrinsic_auto_capture_widget.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtWidgets`, `__future__`, `dataclasses`, `pl_gui.settings.settings_view.styles`, `pl_gui.utils.utils_widgets.MaterialButton`, `src.applications.base.app_styles`, `src.applications.base.widgets.keyboard_number_field`, `src.applications.intrinsic_calibration_capture.service.i_intrinsic_capture_service`.

### `IntrinsicAutoCaptureWidget`

```python
class IntrinsicAutoCaptureWidget(QWidget):
```

Declared fields/defaults:

```python
start_requested = pyqtSignal()
stop_requested = pyqtSignal()
config_changed = pyqtSignal(object)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, parent=None)
```

```python
def settings_widget(self) -> QWidget
```

```python
def setEnabled(self, enabled: bool) -> None
```

```python
def retranslateUi(self) -> None
```

```python
def changeEvent(self, event) -> None
```

```python
def get_config(self) -> IntrinsicCaptureConfig
```

```python
def set_config(self, config: IntrinsicCaptureConfig) -> None
```

```python
def set_running(self, running: bool) -> None
```

## `robot_calibration_preview_dialog.py`

Source: [src/applications/calibration/view/robot_calibration_preview_dialog.py](../../../../src/applications/calibration/view/robot_calibration_preview_dialog.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtGui`, `PyQt6.QtWidgets`, `__future__`, `cv2`, `src.applications.base.app_dialog`, `src.applications.calibration.service.i_calibration_service`.

### `RobotCalibrationPreviewDialog`

```python
class RobotCalibrationPreviewDialog(AppDialog):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, preview: RobotCalibrationPreview, parent=None)
```

```python
def accept(self) -> None
```
