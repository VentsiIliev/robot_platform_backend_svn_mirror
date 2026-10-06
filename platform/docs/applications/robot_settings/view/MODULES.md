# Module reference: `src/applications/robot_settings/view`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [camera_keyboard_settings_tab.py](#camera_keyboard_settings_tabpy)
- [collapsible_settings_view.py](#collapsible_settings_viewpy)
- [movement_groups_tab.py](#movement_groups_tabpy)
- [robot_settings_schema.py](#robot_settings_schemapy)
- [robot_settings_view.py](#robot_settings_viewpy)
- [targeting_definitions_tab.py](#targeting_definitions_tabpy)

## `__init__.py`

Source: [src/applications/robot_settings/view/__init__.py](../../../../src/applications/robot_settings/view/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `camera_keyboard_settings_tab.py`

Source: [src/applications/robot_settings/view/camera_keyboard_settings_tab.py](../../../../src/applications/robot_settings/view/camera_keyboard_settings_tab.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtWidgets`, `__future__`, `pl_gui.settings.settings_view.schema`, `pl_gui.settings.settings_view.styles`, `src.applications.base.widgets.custom_virtual_keyboard`, `src.applications.robot_settings.view.robot_settings_schema`, `typing`.

### `_CameraKeyboardFieldCard`

```python
class _CameraKeyboardFieldCard(QWidget):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, field: SettingField, editor: QWidget, parent: QWidget | None=None) -> None
```

### `_CameraKeyboardGroup`

```python
class _CameraKeyboardGroup(QGroupBox):
```

Declared fields/defaults:

```python
value_changed = pyqtSignal(str, object)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, schema: SettingGroup, parent: QWidget | None=None) -> None
```

```python
def set_values(self, values: dict) -> None
```

```python
def get_values(self) -> dict
```

```python
def reset_to_defaults(self) -> None
```

### `CameraKeyboardSettingsTab`

```python
class CameraKeyboardSettingsTab(QWidget):
```

Declared fields/defaults:

```python
value_changed = pyqtSignal(str, object)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, parent: QWidget | None=None) -> None
```

```python
def set_values(self, values: dict) -> None
```

```python
def get_values(self) -> dict
```

```python
def reset_to_defaults(self) -> None
```

## `collapsible_settings_view.py`

Source: [src/applications/robot_settings/view/collapsible_settings_view.py](../../../../src/applications/robot_settings/view/collapsible_settings_view.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.base.collapsible_settings_view`.

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['CollapsibleGroup', 'CollapsibleSettingsView']
```

## `movement_groups_tab.py`

Source: [src/applications/robot_settings/view/movement_groups_tab.py](../../../../src/applications/robot_settings/view/movement_groups_tab.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtWidgets`, `pl_gui.settings.settings_view.styles`, `pl_gui.utils.utils_widgets.touch_spinbox`, `src.applications.base.widgets.custom_virtual_keyboard`, `src.applications.base.widgets.keyboard_number_field`, `src.engine.robot.configuration`, `src.shared_contracts.declarations`, `typing`.

### `_t`

```python
def _t(text: str) -> str
```

### `PositionEditorDialog`

```python
class PositionEditorDialog(QDialog):
```

Touch-friendly 6-DOF position editor. Layout: two columns — X / Y / Z on the left, RX / RY / RZ on the right. Each coordinate gets a keyboard-aware spin box with the configured range.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, title: str, position_str: str='', parent=None)
```

```python
def get_position_str(self) -> str
```

### `MovementGroupWidget`

```python
class MovementGroupWidget(QWidget):
```

Collapsible widget for a single movement group. Collapsed by default — click the header to expand/collapse.

Declared fields/defaults:

```python
velocity_changed = pyqtSignal(str, int)
acceleration_changed = pyqtSignal(str, int)
motion_type_changed = pyqtSignal(str, str)
iterations_changed = pyqtSignal(str, int)
position_changed = pyqtSignal(str, str)
points_changed = pyqtSignal(str, list)
set_current_requested = pyqtSignal(str)
move_to_requested = pyqtSignal(str, object)
execute_trajectory_requested = pyqtSignal(str)
remove_requested = pyqtSignal(str)
add_current_requested = pyqtSignal(str)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, definition: MovementGroupDefinition, parent=None)
```

```python
def use_card_layout(self) -> None
```

```python
def changeEvent(self, event) -> None
```

```python
def load(self, group: MovementGroup) -> None
```

Populate all widgets from a model — no signals emitted.

```python
def get_values(self) -> MovementGroup
```

```python
def set_position(self, position_str: str) -> None
```

Called by controller after handling set_current_requested.

```python
def add_point(self, point_str: str) -> None
```

Called by controller after handling set_current_requested on a multi-pos group.

### `MovementGroupsTab`

```python
class MovementGroupsTab(QWidget):
```

Group selector and editor driven by RobotConfig.movement_groups. Usage: tab = MovementGroupsTab() tab.load(config.movement_groups) # Wire actions to controller externally: tab.set_current_requested.connect(controller.handle_set_current) tab.execute_trajectory_requested.connect(controller.handle_execute)

Declared fields/defaults:

```python
values_changed = pyqtSignal(str, object)
set_current_requested = pyqtSignal(str)
move_to_requested = pyqtSignal(str, object)
execute_trajectory_requested = pyqtSignal(str)
remove_group_requested = pyqtSignal(str)
add_current_requested = pyqtSignal(str)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, parent=None)
```

```python
def load(self, groups: Dict[str, MovementGroup], definitions: List[MovementGroupDefinition] | None=None) -> None
```

```python
def get_values(self) -> Dict[str, MovementGroup]
```

```python
def get_widget(self, group_name: str) -> Optional[MovementGroupWidget]
```

```python
def add_group(self, name: str, defn: MovementGroupDefinition, group: MovementGroup) -> None
```

```python
def remove_group(self, name: str) -> None
```

## `robot_settings_schema.py`

Source: [src/applications/robot_settings/view/robot_settings_schema.py](../../../../src/applications/robot_settings/view/robot_settings_schema.py).

Imports (including optional/function-local imports; not a startup dependency list): `pl_gui.settings.settings_view.schema`.

Module declarations (expressions are shown without evaluating them):

```python
ROBOT_INFO_GROUP = SettingGroup('Robot Information', [SettingField('robot_ip', 'IP Address', 'line_edit', default='192.168.58.2'), SettingField('robot_tool', 'Tool Number', 'spinbox', default=0, min_val=0, max_val=10, step=1, step_options=[1]), SettingField('robot_user', 'User Number', 'spinbox', default=0, min_val=0, max_val=10, step=1, step_options=[1])], columns=3)
CAMERA_TCP_GROUP = SettingGroup('Camera-to-TCP Offset', [SettingField('use_automatic_camera_to_tcp_offset', 'Use Automatic Camera-to-TCP Offset', 'checkbox_string', default='True'), SettingField('camera_to_tcp_x_offset', 'Camera To TCP X Offset', 'double_spinbox', default=0.0, min_val=-1000, max_val=1000, decimals=3, suffix=' mm', step=0.001, step_options=[0.001, 0.01, 0.1, 1]), SettingField('camera_to_tcp_y_offset', 'Camera To TCP Y Offset', 'double_spinbox', default=0.0, min_val=-1000, max_val=1000, decimals=3, suffix=' mm', step=0.001, step_options=[0.001, 0.01, 0.1, 1])])
CAMERA_Z_SHIFT_GROUP = SettingGroup('Camera Z Shift', [SettingField('camera_z_shift_x_per_mm_px', 'Camera Z Shift X / mm', 'double_spinbox', default=0.0, min_val=-1000, max_val=1000, decimals=6, suffix=' px/mm', step=0.0001, step_options=[0.0001, 0.001, 0.01, 0.1]), SettingField('camera_z_shift_y_per_mm_px', 'Camera Z Shift Y / mm', 'double_spinbox', default=0.0, min_val=-1000, max_val=1000, decimals=6, suffix=' px/mm', step=0.0001, step_options=[0.0001, 0.001, 0.01, 0.1]), SettingField('camera_z_shift_x_per_mm', 'Camera Z Shift X / mm', 'double_spinbox', default=0.0, min_val=-1000, max_val=1000, decimals=6, suffix=' mm/mm', step=0.0001, step_options=[0.0001, 0.001, 0.01, 0.1]), SettingField('camera_z_shift_y_per_mm', 'Camera Z Shift Y / mm', 'double_spinbox', default=0.0, min_val=-1000, max_val=1000, decimals=6, suffix=' mm/mm', step=0.0001, step_options=[0.0001, 0.001, 0.01, 0.1])])
GLOBAL_MOTION_GROUP = SettingGroup('Global Motion Settings', [SettingField('global_velocity', 'Global Velocity', 'spinbox', default=100, min_val=1, max_val=1000, suffix=' mm/s', step=1, step_options=[1, 5, 10, 50]), SettingField('global_acceleration', 'Global Acceleration', 'spinbox', default=100, min_val=1, max_val=1000, suffix=' mm/s²', step=1, step_options=[1, 5, 10, 50]), SettingField('emergency_decel', 'Emergency Deceleration', 'spinbox', default=500, min_val=1, max_val=1000, suffix=' mm/s²', step=1, step_options=[1, 5, 10, 50]), SettingField('max_jog_step', 'Max Jog Step', 'spinbox', default=50, min_val=1, max_val=100, suffix=' mm', step=1, step_options=[1, 5, 10]), SettingField('recovery_servo_linear_mm_s', 'Recovery Servo Linear Limit', 'double_spinbox', default=25.0, min_val=1.0, max_val=250.0, decimals=1, suffix=' mm/s', step=1.0, step_options=[1, 5, 10, 25]), SettingField('recovery_servo_angular_deg_s', 'Recovery Servo Angular Limit', 'double_spinbox', default=5.0, min_val=0.1, max_val=30.0, decimals=1, suffix=' °/s', step=0.5, step_options=[0.5, 1, 2, 5])], columns=3)
TCP_STEP_GROUP = SettingGroup('TCP Step Settings', [SettingField('tcp_x_step_distance', 'X Step Distance', 'double_spinbox', default=50.0, min_val=0, max_val=200, decimals=1, suffix=' mm', step=0.1, step_options=[0.1, 1, 5, 10]), SettingField('tcp_x_step_offset', 'X Step Offset', 'double_spinbox', default=0.1, min_val=0, max_val=10, decimals=3, step=0.001, step_options=[0.001, 0.01, 0.1]), SettingField('tcp_y_step_distance', 'Y Step Distance', 'double_spinbox', default=50.0, min_val=0, max_val=200, decimals=1, suffix=' mm', step=0.1, step_options=[0.1, 1, 5, 10]), SettingField('tcp_y_step_offset', 'Y Step Offset', 'double_spinbox', default=0.1, min_val=0, max_val=10, decimals=3, step=0.001, step_options=[0.001, 0.01, 0.1])])
OFFSET_DIRECTION_GROUP = SettingGroup('Offset Direction Map', [SettingField('offset_pos_x', '+X Direction', 'combo', default='True', choices=['True', 'False']), SettingField('offset_neg_x', '-X Direction', 'combo', default='True', choices=['True', 'False']), SettingField('offset_pos_y', '+Y Direction', 'combo', default='True', choices=['True', 'False']), SettingField('offset_neg_y', '-Y Direction', 'combo', default='True', choices=['True', 'False'])])
CALIBRATION_ADAPTIVE_GROUP = SettingGroup('Adaptive Movement', [SettingField('calib_min_step_mm', 'Min Step', 'double_spinbox', default=0.1, min_val=0.0, max_val=10.0, decimals=2, suffix=' mm', step=0.01, step_options=[0.01, 0.1, 1.0]), SettingField('calib_max_step_mm', 'Max Step', 'double_spinbox', default=25.0, min_val=0.0, max_val=100.0, decimals=1, suffix=' mm', step=0.1, step_options=[0.1, 1.0, 5.0]), SettingField('calib_target_error_mm', 'Target Error', 'double_spinbox', default=0.25, min_val=0.0, max_val=10.0, decimals=2, suffix=' mm', step=0.01, step_options=[0.01, 0.1, 1.0]), SettingField('calib_max_error_ref', 'Max Error Reference', 'double_spinbox', default=100.0, min_val=0.0, max_val=1000.0, decimals=1, suffix=' mm', step=1.0, step_options=[1, 5, 10, 50]), SettingField('calib_k', 'Responsiveness (k)', 'double_spinbox', default=2.0, min_val=0.1, max_val=10.0, decimals=1, step=0.1, step_options=[0.1, 0.5, 1.0]), SettingField('calib_derivative_scaling', 'Derivative Scaling', 'double_spinbox', default=0.5, min_val=0.0, max_val=2.0, decimals=2, step=0.01, step_options=[0.01, 0.1, 0.5]), SettingField('calib_initial_align_y_scale', 'Initial Y Scale', 'double_spinbox', default=1.0, min_val=0.5, max_val=2.0, decimals=3, step=0.01, step_options=[0.01, 0.05, 0.1])])
CALIBRATION_MARKER_GROUP = SettingGroup('Marker Detection', [SettingField('calib_run_height_measurement', 'Measure Height', 'combo', default='True', choices=['True', 'False']), SettingField('calib_z_target', 'Z Target Height', 'spinbox', default=300, min_val=0, max_val=1000, suffix=' mm', step=1, step_options=[1, 10, 50]), SettingField('calib_required_ids', 'Required IDs', 'int_list', default='0,1,2,3,4,5,6,8', min_val=0, max_val=255), SettingField('calib_candidate_ids', 'Candidate IDs', 'int_list', default='', min_val=0, max_val=999), SettingField('calib_min_target_separation_px', 'Min Separation', 'double_spinbox', default=120.0, min_val=0.0, max_val=2000.0, decimals=1, suffix=' px', step=1.0, step_options=[1, 10, 50, 100, 150]), SettingField('calib_travel_velocity', 'Travel Velocity', 'spinbox', default=30, min_val=1, max_val=1000, suffix=' mm/s', step=1, step_options=[1, 5, 10, 50]), SettingField('calib_travel_acceleration', 'Travel Acceleration', 'spinbox', default=10, min_val=1, max_val=1000, suffix=' mm/s²', step=1, step_options=[1, 5, 10, 50]), SettingField('calib_iterative_velocity', 'Iter Align Velocity', 'spinbox', default=30, min_val=1, max_val=1000, suffix=' mm/s', step=1, step_options=[1, 5, 10, 50]), SettingField('calib_iterative_acceleration', 'Iter Align Accel', 'spinbox', default=10, min_val=1, max_val=1000, suffix=' mm/s²', step=1, step_options=[1, 5, 10, 50]), SettingField('calib_fast_iteration_wait', 'Stability Wait', 'double_spinbox', default=1.0, min_val=0.0, max_val=10.0, suffix=' s', step=0.1, decimals=1, step_options=[0.1, 0.5, 1.0])])
SAFETY_LIMITS_GROUP = SettingGroup('Safety Limits', [SettingField('safety_x_min', 'X Min', 'spinbox', default=-500, min_val=-1000, max_val=1000, suffix=' mm', step=1, step_options=[1, 10, 50, 100]), SettingField('safety_x_max', 'X Max', 'spinbox', default=500, min_val=-1000, max_val=1000, suffix=' mm', step=1, step_options=[1, 10, 50, 100]), SettingField('safety_y_min', 'Y Min', 'spinbox', default=-500, min_val=-1000, max_val=1000, suffix=' mm', step=1, step_options=[1, 10, 50, 100]), SettingField('safety_y_max', 'Y Max', 'spinbox', default=500, min_val=-1000, max_val=1000, suffix=' mm', step=1, step_options=[1, 10, 50, 100]), SettingField('safety_z_min', 'Z Min', 'spinbox', default=100, min_val=0, max_val=1000, suffix=' mm', step=1, step_options=[1, 10, 50, 100]), SettingField('safety_z_max', 'Z Max', 'spinbox', default=800, min_val=0, max_val=1000, suffix=' mm', step=1, step_options=[1, 10, 50, 100]), SettingField('safety_rx_min', 'RX Min', 'spinbox', default=170, min_val=-180, max_val=180, suffix=' °', step=1, step_options=[1, 5, 10]), SettingField('safety_rx_max', 'RX Max', 'spinbox', default=180, min_val=-180, max_val=180, suffix=' °', step=1, step_options=[1, 5, 10]), SettingField('safety_ry_min', 'RY Min', 'spinbox', default=-10, min_val=-180, max_val=180, suffix=' °', step=1, step_options=[1, 5, 10]), SettingField('safety_ry_max', 'RY Max', 'spinbox', default=10, min_val=-180, max_val=180, suffix=' °', step=1, step_options=[1, 5, 10]), SettingField('safety_rz_min', 'RZ Min', 'spinbox', default=-180, min_val=-180, max_val=180, suffix=' °', step=1, step_options=[1, 5, 10]), SettingField('safety_rz_max', 'RZ Max', 'spinbox', default=180, min_val=-180, max_val=180, suffix=' °', step=1, step_options=[1, 5, 10])])
POSITION_LIMITS_GROUP = SettingGroup('Position Limits', SAFETY_LIMITS_GROUP.fields[:6], axis_pairs=True)
ORIENTATION_LIMITS_GROUP = SettingGroup('Orientation Limits', SAFETY_LIMITS_GROUP.fields[6:], axis_pairs=True)
CALIBRATION_AXIS_MAPPING_GROUP = SettingGroup('Axis Mapping', [SettingField('calib_axis_marker_id', 'Marker ID', 'spinbox', default=4, min_val=0, max_val=255, step=1, step_options=[1]), SettingField('calib_axis_move_mm', 'Move Distance', 'double_spinbox', default=100.0, min_val=1.0, max_val=500.0, decimals=1, suffix=' mm', step=1.0, step_options=[1, 5, 10, 50]), SettingField('calib_axis_max_attempts', 'Max Detect Attempts', 'spinbox', default=100, min_val=1, max_val=1000, step=10, step_options=[10, 50, 100]), SettingField('calib_axis_delay_after_move', 'Delay After Move', 'double_spinbox', default=1.0, min_val=0.0, max_val=10.0, decimals=2, suffix=' s', step=0.1, step_options=[0.1, 0.5, 1.0])])
CALIBRATION_CAMERA_TCP_GROUP = SettingGroup('Camera TCP Offset Calibration', [SettingField('calib_tcp_marker_id', 'Marker ID', 'spinbox', default=4, min_val=0, max_val=255, step=1, step_options=[1]), SettingField('calib_tcp_run_during_main', 'Capture In Main Cal', 'combo', default='False', choices=['False', 'True']), SettingField('calib_tcp_max_markers', 'Max Markers', 'spinbox', default=2, min_val=1, max_val=50, step=1, step_options=[1, 2, 3, 5, 10]), SettingField('calib_tcp_rotation_step_deg', 'Rotation Step', 'double_spinbox', default=15.0, min_val=0.1, max_val=180.0, decimals=2, suffix=' °', step=0.1, step_options=[0.1, 1.0, 5.0, 15.0]), SettingField('calib_tcp_iterations', 'Iterations', 'spinbox', default=6, min_val=1, max_val=100, step=1, step_options=[1, 2, 5, 10]), SettingField('calib_tcp_approach_z', 'Approach Z', 'double_spinbox', default=300.0, min_val=0.0, max_val=1000.0, decimals=3, suffix=' mm', step=0.1, step_options=[0.1, 1.0, 10.0, 50.0]), SettingField('calib_tcp_approach_rx', 'Approach RX', 'double_spinbox', default=180.0, min_val=-180.0, max_val=180.0, decimals=3, suffix=' °', step=0.1, step_options=[0.1, 1.0, 5.0, 10.0]), SettingField('calib_tcp_approach_ry', 'Approach RY', 'double_spinbox', default=0.0, min_val=-180.0, max_val=180.0, decimals=3, suffix=' °', step=0.1, step_options=[0.1, 1.0, 5.0, 10.0]), SettingField('calib_tcp_approach_rz', 'Reference RZ', 'double_spinbox', default=0.0, min_val=-180.0, max_val=180.0, decimals=3, suffix=' °', step=0.1, step_options=[0.1, 1.0, 5.0, 10.0]), SettingField('calib_tcp_velocity', 'Velocity', 'spinbox', default=20, min_val=1, max_val=1000, suffix=' mm/s', step=1, step_options=[1, 5, 10, 50]), SettingField('calib_tcp_acceleration', 'Acceleration', 'spinbox', default=10, min_val=1, max_val=1000, suffix=' mm/s²', step=1, step_options=[1, 5, 10, 50]), SettingField('calib_tcp_settle_time_s', 'Settle Time', 'double_spinbox', default=1.0, min_val=0.0, max_val=10.0, decimals=2, suffix=' s', step=0.1, step_options=[0.1, 0.5, 1.0, 2.0]), SettingField('calib_tcp_detection_attempts', 'Detection Attempts', 'spinbox', default=20, min_val=1, max_val=1000, step=1, step_options=[1, 5, 10, 20, 50]), SettingField('calib_tcp_retry_delay_s', 'Retry Delay', 'double_spinbox', default=0.1, min_val=0.0, max_val=10.0, decimals=2, suffix=' s', step=0.01, step_options=[0.01, 0.1, 0.5, 1.0]), SettingField('calib_tcp_recenter_max_iterations', 'Recenter Max Iters', 'spinbox', default=20, min_val=1, max_val=200, step=1, step_options=[1, 5, 10, 20, 50]), SettingField('calib_tcp_min_samples', 'Min Samples', 'spinbox', default=3, min_val=1, max_val=200, step=1, step_options=[1, 2, 3, 5, 10]), SettingField('calib_tcp_max_acceptance_std_mm', 'Max Std', 'double_spinbox', default=10.0, min_val=0.0, max_val=100.0, decimals=3, suffix=' mm', step=0.1, step_options=[0.1, 1.0, 5.0, 10.0])])
```

## `robot_settings_view.py`

Source: [src/applications/robot_settings/view/robot_settings_view.py](../../../../src/applications/robot_settings/view/robot_settings_view.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtWidgets`, `pl_gui.settings.settings_view.settings_view`, `pl_gui.settings.settings_view.styles`, `src.applications.base.i_application_view`, `src.applications.base.keyboard_settings_view`, `src.applications.robot_settings.model.mapper`, `src.applications.robot_settings.view.movement_groups_tab`, `src.applications.robot_settings.view.robot_settings_schema`, `src.applications.robot_settings.view.targeting_definitions_tab`, `src.shared_contracts.declarations`.

### `_RobotCardSettingsView`

```python
class _RobotCardSettingsView(KeyboardSettingsView):
```

Use open section cards while retaining shared virtual keyboard fields.

### `RobotSettingsView`

```python
class RobotSettingsView(IApplicationView):
```

View — pure Qt widget. No services, no business logic.

Declared fields/defaults:

```python
SHOW_JOG_WIDGET = True
JOG_LIVE_POSITION_ENABLED = True
JOG_FRAME_SELECTOR_ENABLED = True
save_requested = pyqtSignal(dict)
discard_requested = pyqtSignal()
value_changed = pyqtSignal(str, object, str)
movement_changed = pyqtSignal(str, object)
targeting_changed = pyqtSignal()
remove_group_requested = pyqtSignal(str)
set_current_requested = pyqtSignal(str)
move_to_requested = pyqtSignal(str, object)
execute_requested = pyqtSignal(str)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, movement_group_definitions: list[MovementGroupDefinition] | None=None, parent=None)
```

```python
def setup_ui(self) -> None
```

```python
def mark_saved(self) -> None
```

```python
def load_config(self, flat: dict) -> None
```

```python
def update_robot_config(self, config) -> None
```

```python
def load_movement_groups(self, groups: dict, definitions: list[MovementGroupDefinition] | None=None) -> None
```

```python
def load_targeting_definitions(self, data: dict | None) -> None
```

```python
def get_values(self) -> dict
```

```python
def get_movement_groups(self) -> dict
```

```python
def get_targeting_definitions(self) -> dict
```

```python
def add_movement_group(self, name: str, defn, group) -> None
```

```python
def remove_movement_group(self, name: str) -> None
```

```python
def get_group_widget(self, group_name: str)
```

```python
def clean_up(self) -> None
```

## `targeting_definitions_tab.py`

Source: [src/applications/robot_settings/view/targeting_definitions_tab.py](../../../../src/applications/robot_settings/view/targeting_definitions_tab.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtWidgets`, `__future__`, `copy`, `pl_gui.settings.settings_view.styles`, `src.applications.base.app_dialog`, `src.applications.base.styled_message_box`, `src.applications.base.widgets.custom_virtual_keyboard`, `src.applications.base.widgets.keyboard_number_field`, `typing`.

### `_t`

```python
def _t(text: str) -> str
```

### `_calibration_choice`

```python
def _calibration_choice(frame: dict) -> str
```

### `_apply_calibration_choice`

```python
def _apply_calibration_choice(frame: dict, choice: str) -> dict
```

### `TargetingDefinitionsTab`

```python
class TargetingDefinitionsTab(QWidget):
```

Declared fields/defaults:

```python
definitions_changed = pyqtSignal()
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, parent=None)
```

```python
def changeEvent(self, event) -> None
```

```python
def load(self, data: dict | None) -> None
```

```python
def get_values(self) -> dict
```

### `_PointDialog`

```python
class _PointDialog(AppDialog):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, data: dict | None=None, protected_name: bool=False, parent=None)
```

```python
def get_values(self) -> dict
```

```python
def accept(self) -> None
```

### `_FrameDialog`

```python
class _FrameDialog(AppDialog):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, data: dict | None=None, parent=None)
```

```python
def get_values(self) -> dict
```

```python
def accept(self) -> None
```
