# Module reference: `src/robot_systems/paint`

[Package guide](README.md) · [Complete source index](../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [application_wiring.py](#application_wiringpy)
- [bootstrap_provider.py](#bootstrap_providerpy)
- [component_ids.py](#component_idspy)
- [navigation.py](#navigationpy)
- [paint_robot_system.py](#paint_robot_systempy)
- [paint_system_config.py](#paint_system_configpy)
- [run_servo_pickup_test.py](#run_servo_pickup_testpy)
- [service_builders.py](#service_builderspy)
- [timing.py](#timingpy)

## `__init__.py`

Source: [src/robot_systems/paint/__init__.py](../../../src/robot_systems/paint/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.robot_systems.paint.paint_robot_system`.

Package-level import/export surface:

```python
from src.robot_systems.paint.paint_robot_system import PaintRobotSystem
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['PaintRobotSystem']
```

## `application_wiring.py`

Source: [src/robot_systems/paint/application_wiring.py](../../../src/robot_systems/paint/application_wiring.py).

Imports (including optional/function-local imports; not a startup dependency list): `contour_editor`, `copy`, `logging`, `numpy`, `os`, `src.applications.base.robot_jog_service_builder`, `src.applications.base.widget_application`, `src.applications.broker_debug.broker_debug_factory`, `src.applications.broker_debug.service.broker_debug_application_service`, `src.applications.calibration.calibration_factory`, `src.applications.calibration.service.calibration_application_service`, `src.applications.calibration_settings`, `src.applications.camera_settings.camera_settings_factory`, `src.applications.camera_settings.controller.camera_devices_controller`, `src.applications.camera_settings.model.camera_settings_model`, `src.applications.camera_settings.service.camera_settings_application_service`, `src.applications.camera_settings.view.camera_devices_widget`, `src.applications.contour_matching_tester.contour_matching_tester_factory`, `src.applications.contour_matching_tester.service.contour_matching_tester_service`, `src.applications.device_control.device_control_factory`, `src.applications.device_control.dryer`, `src.applications.device_control.service.device_control_application_service`, `src.applications.ethercat_diagnostics`, `src.applications.ethercat_diagnostics.service`, `src.applications.hand_eye_calibration.hand_eye_calibration_factory`, `src.applications.hand_eye_calibration.service.hand_eye_service`, `src.applications.intrinsic_calibration_capture.intrinsic_capture_factory`, `src.applications.intrinsic_calibration_capture.service.intrinsic_capture_service`, `src.applications.modbus_settings`, `src.applications.network_settings.build_application`, `src.applications.pick_target.pick_target_factory`, `src.applications.pick_target.service.pick_target_application_service`, `src.applications.robot_settings.robot_settings_factory`, `src.applications.robot_settings.service.robot_settings_application_service`, `src.applications.shaft_alignment.service.paint_vision_shaft_alignment_service`, `src.applications.shaft_alignment.shaft_alignment_factory`, `src.applications.software_update`, `src.applications.software_update.service.software_update_service`, `src.applications.tool_settings`, `src.applications.user_management.domain.auth_user_repository_adapter`, `src.applications.user_management.domain.csv_user_repository`, `src.applications.user_management.service.user_management_application_service`, `src.applications.user_management.user_management_factory`, `src.applications.work_area_settings.service.work_area_settings_application_service`, `src.applications.work_area_settings.work_area_settings_factory`, `src.applications.workpiece_editor.editor_core.config`, `src.applications.workpiece_editor.service.workpiece_editor_service`, `src.applications.workpiece_editor.workpiece_editor_factory`, `src.applications.workpiece_library.workpiece_library_factory`, `src.engine.auth.authentication_service`, `src.engine.auth.authorization_service`, `src.engine.auth.json_permissions_repository`, `src.engine.common_service_ids`, `src.engine.common_settings_ids`, `src.engine.hardware.communication.modbus.modbus_action_service`, `src.engine.hardware.peripherals`, `src.engine.hardware.peripherals.device_control_adapters`, `src.engine.robot.calibration.calibration_navigation_service`, `src.engine.robot.calibration.camera_tcp_offset_calibration_service`, `src.engine.robot.calibration.camera_z_shift_calibration_service`, `src.engine.robot.calibration.ros_tool_registry_client`, `src.engine.robot.calibration.service_builders`, `src.engine.robot.calibration.tool_tcp_calibration_service`, `src.engine.robot.path_preparation`, `src.engine.vision.calibration_vision_settings`, `src.engine.vision.capture_snapshot_service`, `src.engine.vision.homography_residual_transformer`, `src.robot_systems.paint`, `src.robot_systems.paint.applications.dashboard`, `src.robot_systems.paint.applications.paint_adjustment`, `src.robot_systems.paint.applications.paint_head_settings.paint_head_settings_controller`, `src.robot_systems.paint.applications.paint_head_settings.paint_head_settings_model`, `src.robot_systems.paint.applications.paint_head_settings.paint_head_settings_service`, `src.robot_systems.paint.applications.paint_head_settings.paint_head_settings_view`, `src.robot_systems.paint.applications.paint_motion_plane_setup`, `src.robot_systems.paint.applications.paint_motion_plane_setup.service.paint_motion_plane_setup_service`, `src.robot_systems.paint.applications.paint_motion_recipe`, `src.robot_systems.paint.applications.paint_motion_recipe.service`, `src.robot_systems.paint.applications.paint_process_settings.paint_process_settings_factory`, `src.robot_systems.paint.applications.paint_process_settings.service.paint_process_settings_application_service`, `src.robot_systems.paint.component_ids`, `src.robot_systems.paint.domain.contour_editor_schema`, `src.robot_systems.paint.domain.paint_segment_selection`, `src.robot_systems.paint.domain.paint_workpiece_editor_adapter`, `src.robot_systems.paint.domain.users`, `src.robot_systems.paint.domain.workpieces`, `src.robot_systems.paint.hardware.paint_head_availability_adapter`, `src.robot_systems.paint.processes.paint.auto_dryer.dryer_release_coordinator`, `src.robot_systems.paint.processes.paint.config`, `src.robot_systems.paint.processes.paint.execute`, `src.robot_systems.paint.processes.paint.magazine_load_service`, `src.robot_systems.paint.processes.paint.match.workpiece_matching_service`, `src.robot_systems.paint.processes.paint.plan`, `src.robot_systems.paint.processes.paint.plan.paint_contour_interpolation`, `src.robot_systems.paint.targeting.settings_adapter`, `src.shared_contracts.events.process_events`, `time`.

### `_effective_camera_to_tcp_offsets`

```python
def _effective_camera_to_tcp_offsets(robot_system, robot_config=None, area_id: str='') -> tuple[float, float]
```

### `_bypass_contour_preparation_enabled`

```python
def _bypass_contour_preparation_enabled(robot_system=None) -> bool
```

### `_get_paint_process_config`

```python
def _get_paint_process_config(robot_system=None)
```

### `_get_paint_execution_target_point_name`

```python
def _get_paint_execution_target_point_name(robot_system) -> str
```

### `_get_paint_base_group_id`

```python
def _get_paint_base_group_id(robot_system=None) -> str
```

### `_get_pickup_base_group_id`

```python
def _get_pickup_base_group_id(robot_system=None) -> str
```

### `_get_cleanup_base_group_id`

```python
def _get_cleanup_base_group_id(robot_system=None) -> str
```

### `_get_dropoff_group_id`

```python
def _get_dropoff_group_id(robot_system=None) -> str
```

### `_get_active_work_area_id`

```python
def _get_active_work_area_id(robot_system=None) -> str
```

### `_get_target_frame_name_for_work_area`

```python
def _get_target_frame_name_for_work_area(robot_system=None, work_area_id: str='paint') -> str
```

### `_get_active_target_frame_name`

```python
def _get_active_target_frame_name(robot_system=None) -> str
```

### `_get_capture_group_for_work_area`

```python
def _get_capture_group_for_work_area(robot_system=None, work_area_id: str='paint') -> str
```

### `_get_active_capture_group`

```python
def _get_active_capture_group(robot_system=None) -> str
```

### `_angle_delta_degrees`

```python
def _angle_delta_degrees(a: float, b: float) -> float
```

### `_validate_active_capture_area`

```python
def _validate_active_capture_area(robot_system, area_id: str, robot_pose) -> tuple[bool, str]
```

### `_validate_current_capture_state`

```python
def _validate_current_capture_state(robot_system) -> tuple[bool, str]
```

### `_get_pickup_axis_alignment_sign`

```python
def _get_pickup_axis_alignment_sign(robot_system=None) -> float
```

### `_get_pivot_side`

```python
def _get_pivot_side(robot_system=None) -> str
```

### `_get_pivot_translation_direction`

```python
def _get_pivot_translation_direction(robot_system=None) -> str
```

### `_get_pivot_profile`

```python
def _get_pivot_profile(robot_system=None) -> PaintPivotProfile
```

### `_get_paint_pivot_side`

```python
def _get_paint_pivot_side(robot_system=None) -> str
```

### `_build_dashboard_application`

```python
def _build_dashboard_application(robot_system)
```

### `_build_paint_adjustment_application`

```python
def _build_paint_adjustment_application(robot_system)
```

### `_build_capture_snapshot_service`

```python
def _build_capture_snapshot_service(robot_system)
```

### `_build_paint_workpiece_service`

```python
def _build_paint_workpiece_service(robot_system)
```

### `_build_contour_matching_tester`

```python
def _build_contour_matching_tester(robot_system)
```

### `_build_paint_path_debug_dump_dir`

```python
def _build_paint_path_debug_dump_dir()
```

### `_build_dryer_release_coordinator`

```python
def _build_dryer_release_coordinator(robot_system)
```

### `_build_paint_path_executor`

```python
def _build_paint_path_executor(robot_system)
```

### `_build_paint_path_preparation_service`

```python
def _build_paint_path_preparation_service(robot_system)
```

### `_build_paint_matching_service`

```python
def _build_paint_matching_service(robot_system, workpiece_service=None, capture_snapshot_service=None, debug_dump_dir=None)
```

### `_build_paint_workpiece_preparation_service`

```python
def _build_paint_workpiece_preparation_service(robot_system)
```

### `_build_paint_magazine_load_service`

```python
def _build_paint_magazine_load_service(robot_system)
```

### `_paint_camera_image_size`

```python
def _paint_camera_image_size(robot_system) -> tuple[int, int]
```

### `_build_paint_workpiece_editor_service`

```python
def _build_paint_workpiece_editor_service(robot_system)
```

### `_build_paint_contour_editor_application`

```python
def _build_paint_contour_editor_application(robot_system)
```

### `_build_paint_process_settings_application`

```python
def _build_paint_process_settings_application(robot_system)
```

### `_build_paint_motion_recipe_application`

```python
def _build_paint_motion_recipe_application(robot_system)
```

### `_build_workpiece_library_application`

```python
def _build_workpiece_library_application(robot_system)
```

### `_build_paint_motion_plane_setup_application`

```python
def _build_paint_motion_plane_setup_application(robot_system)
```

### `_build_user_management_application`

```python
def _build_user_management_application(robot_system)
```

### `_build_camera_settings_application`

```python
def _build_camera_settings_application(robot_system)
```

### `_build_shaft_alignment_application`

```python
def _build_shaft_alignment_application(robot_system)
```

### `_build_calibration_settings_application`

```python
def _build_calibration_settings_application(robot_system)
```

### `_build_work_area_settings_application`

```python
def _build_work_area_settings_application(robot_system)
```

### `_build_calibration_application`

```python
def _build_calibration_application(robot_system)
```

### `_build_broker_debug_application`

```python
def _build_broker_debug_application(robot_system)
```

### `_build_robot_settings_application`

```python
def _build_robot_settings_application(robot_app)
```

### `_build_tool_settings_application`

```python
def _build_tool_settings_application(robot_app)
```

### `_build_modbus_settings_application`

```python
def _build_modbus_settings_application(robot_app)
```

### `_build_device_control_application`

```python
def _build_device_control_application(robot_system)
```

Build the shared dynamic device-control app from configured peripherals.

### `_build_ethercat_diagnostics_application`

```python
def _build_ethercat_diagnostics_application(robot_app)
```

### `_build_intrinsic_capture_application`

```python
def _build_intrinsic_capture_application(robot_system)
```

### `_build_hand_eye_calibration_application`

```python
def _build_hand_eye_calibration_application(robot_system)
```

### `_build_pick_target_application`

```python
def _build_pick_target_application(robot_system)
```

### `_build_network_settings_application`

```python
def _build_network_settings_application(robot_system)
```

### `_build_software_update_application`

```python
def _build_software_update_application(robot_system)
```

## `bootstrap_provider.py`

Source: [src/robot_systems/paint/bootstrap_provider.py](../../../src/robot_systems/paint/bootstrap_provider.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.applications.login.login_application_service`, `src.applications.login.login_factory`, `src.applications.user_management.domain.auth_user_repository_adapter`, `src.applications.user_management.domain.csv_user_repository`, `src.engine.auth.authentication_service`, `src.engine.auth.authorization_service`, `src.engine.auth.json_permissions_repository`, `src.engine.common_service_ids`, `src.engine.robot.drivers.ros2_robot`, `src.robot_systems.paint.domain.users`, `src.robot_systems.paint.paint_robot_system`, `src.robot_systems.robot_system_bootstrap_provider`.

### `PaintBootstrapProvider`

```python
class PaintBootstrapProvider(RobotSystemBootstrapProvider):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, system_class=PaintRobotSystem)
```

```python
@property
def system_class(self)
```

```python
def build_robot(self)
```

```python
def build_login_view(self, robot_system, messaging_service)
```

```python
def build_authorization_service(self, robot_system)
```

### `create_bootstrap_provider`

```python
def create_bootstrap_provider() -> RobotSystemBootstrapProvider
```

## `component_ids.py`

Source: [src/robot_systems/paint/component_ids.py](../../../src/robot_systems/paint/component_ids.py).

Imports (including optional/function-local imports; not a startup dependency list): `enum`.

### `ServiceID`

```python
class ServiceID(str, Enum):
```

Declared fields/defaults:

```python
CUSTOM_DEVICE = 'custom_device'
VACUUM_PUMP = 'vacuum_pump'
FAN = 'fan'
TRAY_FAN = 'tray_fan'
PHYSICAL_CONTROL_BUTTONS = 'physical_control_buttons'
VACUUM_SENSOR = 'vacuum_sensor'
DRYER = 'dryer'
```

### `SettingsID`

```python
class SettingsID(str, Enum):
```

Declared fields/defaults:

```python
CAMERAS = 'cameras'
PAINT_PROCESS_CONFIG = 'paint_process_config'
PAINT_ADJUSTMENT_SETTINGS = 'paint_adjustment_settings'
DRYER_CONFIG = 'dryer_config'
PERIPHERALS = 'peripherals'
```

### `ProcessID`

```python
class ProcessID(str, Enum):
```

Declared fields/defaults:

```python
MAIN_PROCESS = 'main_process'
ROBOT_CALIBRATION = 'robot_calibration'
```

## `navigation.py`

Source: [src/robot_systems/paint/navigation.py](../../../src/robot_systems/paint/navigation.py).

Imports (including optional/function-local imports; not a startup dependency list): `logging`, `src.engine.robot.features.navigation_service`, `src.engine.robot.interfaces.i_robot_service`, `src.engine.vision`, `src.engine.work_areas.i_work_area_service`, `src.robot_systems.paint.processes.paint.config`, `src.robot_systems.paint.timing`, `traceback`, `typing`.

### `PaintNavigationService`

```python
class PaintNavigationService:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, navigation: NavigationService, vision: Optional[IVisionService]=None, robot_service: Optional[IRobotService]=None, work_area_service: Optional[IWorkAreaService]=None, observed_area_by_group: Optional[dict[str, str]]=None, unwind_vel_percent: float=100.0, unwind_acc_percent: float=100.0, unwind_queue_if_busy: bool=True, calibration_move_vel_percent: float | None=None, calibration_move_acc_percent: float | None=None, calibration_move_motion_type: str | None=None, calibration_move_blendR: float | None=None, paint_process_config_service: object | None=None, calibration_tool_id: int | None=None, configured_tool_getter: Callable[[], int] | None=None)
```

```python
def move_home(self) -> bool
```

```python
def move_to_login_position(self) -> bool
```

```python
@timed_step(_logger, 'move_to_calibration_position')
def move_to_calibration_position(self, z_offset: float=0.0, wait_cancelled: Callable[[], bool] | None=None, unwind_before_move: bool=True) -> bool
```

```python
def move_to(self, group_name: str, z_offset: float=0.0, wait_cancelled: Callable[[], bool] | None=None) -> bool
```

```python
def move_linear(self, group_name: str) -> bool
```

```python
def move_to_group(self, group_name: str, wait_cancelled: Callable[[], bool] | None=None, velocity: float | None=None, acceleration: float | None=None, motion_type: str | None=None, blendR: float | None=None) -> bool
```

```python
def stop_motion(self) -> bool
```

```python
def mark_group_observed_area_verified(self, group_name: str) -> None
```

```python
def move_linear_group(self, group_name: str) -> bool
```

```python
def move_to_position(self, position: list, group_name: str, wait_cancelled: Callable[[], bool] | None=None, velocity: float | None=None, acceleration: float | None=None, motion_type: str | None=None, blendR: float | None=None) -> bool
```

```python
def get_group_names(self) -> list[str]
```

```python
def get_group_position(self, group_name: str) -> list[float] | None
```

```python
def get_current_observer_position(self, group_name: str, *, fresh: bool=False) -> list[float] | None
```

Read an observer pose using the same calibration TCP as its taught group.

## `paint_robot_system.py`

Source: [src/robot_systems/paint/paint_robot_system.py](../../../src/robot_systems/paint/paint_robot_system.py).

Imports (including optional/function-local imports; not a startup dependency list): `dataclasses`, `logging`, `os`, `src.engine.common_service_ids`, `src.engine.common_settings_ids`, `src.engine.hardware.communication.modbus.modbus`, `src.engine.hardware.dryer.interfaces.i_dryer_service`, `src.engine.hardware.dryer.models.dryer_config`, `src.engine.hardware.fan.interfaces.i_fan_control`, `src.engine.hardware.peripherals`, `src.engine.hardware.physical_control_buttons.interfaces.i_physical_control_buttons`, `src.engine.hardware.vacuum_pump.interfaces.i_vacuum_pump_controller`, `src.engine.hardware.vacuum_sensor.interfaces.i_vacuum_sensor_service`, `src.engine.robot.calibration.robot_calibration_process`, `src.engine.robot.calibration.service_builders`, `src.engine.robot.configuration`, `src.engine.robot.features.navigation_service`, `src.engine.robot.interfaces.i_robot_service`, `src.engine.robot.interfaces.i_tool_service`, `src.engine.robot.procedures`, `src.engine.robot.safety`, `src.engine.robot.targeting`, `src.engine.updates.paths`, `src.engine.vision.calibration_vision_settings`, `src.engine.vision.camera_device_settings`, `src.engine.vision.camera_settings_serializer`, `src.engine.vision.camera_stream_publisher`, `src.engine.vision.i_vision_service`, `src.engine.work_areas`, `src.robot_systems.base_robot_system`, `src.robot_systems.paint`, `src.robot_systems.paint.applications.dashboard.config`, `src.robot_systems.paint.applications.dashboard.service.paint_dashboard_service`, `src.robot_systems.paint.applications.paint_adjustment.service.paint_adjustment_service`, `src.robot_systems.paint.calibration.coordinator`, `src.robot_systems.paint.calibration.provider`, `src.robot_systems.paint.component_ids`, `src.robot_systems.paint.destinations`, `src.robot_systems.paint.domain.workpieces.matching_selection`, `src.robot_systems.paint.navigation`, `src.robot_systems.paint.processes`, `src.robot_systems.paint.processes.paint.adjustment_settings_serializer`, `src.robot_systems.paint.processes.paint.config`, `src.robot_systems.paint.processes.paint.destination`, `src.robot_systems.paint.processes.paint.paint_process_config_serializer`, `src.robot_systems.paint.processes.paint.paint_process_config_service`, `src.robot_systems.paint.processes.paint.paint_production_service`, `src.robot_systems.paint.service_builders`, `src.robot_systems.paint.targeting.provider`, `src.shared_contracts.declarations`, `types`.

### `_build_sub_zero_dropoff_corridor`

```python
def _build_sub_zero_dropoff_corridor(corridor_id, dropoff_pose, dropoff_config)
```

Build the bounded passage corridor for a configured sub-zero Dropoff pose.

### `_build_application_specs`

```python
def _build_application_specs(config=paint_system_config)
```

Return the Paint applications enabled by config.

### `_build_dashboard_ui_config`

```python
def _build_dashboard_ui_config(config, base=None)
```

### `PaintRobotSystem`

```python
class PaintRobotSystem(BaseRobotSystem):
```

Declared fields/defaults:

```python
allowed_dropoff_strategies = ('movement_group', 'plate_layout')
calibration_tool = ToolDefinition(id=1, name='Calibration Tool')
tools = [calibration_tool]
tool_slots = []
system_config = paint_system_config
ui_config = _build_dashboard_ui_config(paint_system_config)
movement_groups = [MovementGroupDefinition(id='HOME', label='Home', group_type=MovementGroupType.SINGLE_POSITION, has_trajectory_execution=True), MovementGroupDefinition(id='CALIBRATION', label='Calibration', group_type=MovementGroupType.SINGLE_POSITION, has_trajectory_execution=True), MovementGroupDefinition(id='JOG', label='Jog', group_type=MovementGroupType.VELOCITY_ONLY), MovementGroupDefinition(id='Horizontal Shaft', label='Horizontal Shaft', group_type=MovementGroupType.SINGLE_POSITION, has_trajectory_execution=True), MovementGroupDefinition(id='Vertical Shaft', label='Vertical Shaft', group_type=MovementGroupType.SINGLE_POSITION, has_trajectory_execution=True), MovementGroupDefinition(id='Vertical Shaft Alignment', label='Vertical Shaft Alignment', group_type=MovementGroupType.SINGLE_POSITION, has_trajectory_execution=True), MovementGroupDefinition(id='Clean', label='Clean', group_type=MovementGroupType.SINGLE_POSITION, has_trajectory_execution=True), MovementGroupDefinition(id='Dropoff', label='Dropoff', group_type=MovementGroupType.SINGLE_POSITION, has_trajectory_execution=True), MovementGroupDefinition(id='Magazine', label='Magazine', group_type=MovementGroupType.SINGLE_POSITION, has_trajectory_execution=True), MovementGroupDefinition(id='Magazine Fixed Pickup', label='Magazine Fixed Pickup', group_type=MovementGroupType.SINGLE_POSITION, has_trajectory_execution=True)]
target_points = [RemoteTcpDefinition(name='camera', display_name='camera'), RemoteTcpDefinition(name='tool', display_name='tool')]
target_frames = [TargetFrameDefinition(name='calibration', work_area_id='paint', use_height_correction=False), TargetFrameDefinition(name='magazine', work_area_id='magazine', source_navigation_group='CALIBRATION', target_navigation_group='Magazine', use_height_correction=False), TargetFrameDefinition(name='vertical_shaft_alignment', work_area_id='vertical_shaft_alignment', source_navigation_group='CALIBRATION', target_navigation_group='Vertical Shaft Alignment', use_height_correction=False)]
work_areas = [WorkAreaDefinition(id='paint', label='Paint', color='#FF8C32', threshold_profile='default', supports_detection_roi=True, supports_brightness_roi=True, supports_height_mapping=False), WorkAreaDefinition(id='magazine', label='Magazine', color='#4A90E2', threshold_profile='default', supports_detection_roi=True, supports_brightness_roi=True, supports_height_mapping=False), WorkAreaDefinition(id='vertical_shaft_alignment', label='Vertical Shaft Alignment', color='#905BA9', threshold_profile='default', supports_detection_roi=True, supports_brightness_roi=True, supports_height_mapping=False)]
work_area_observers = [WorkAreaObserverBinding(area_id='paint', movement_group_id='CALIBRATION'), WorkAreaObserverBinding(area_id='magazine', movement_group_id='Magazine'), WorkAreaObserverBinding(area_id='vertical_shaft_alignment', movement_group_id='Vertical Shaft Alignment')]
default_active_work_area_id = ''
role_policy = RolePolicy(role_values=['Admin', 'Operator', 'Viewer', 'Developer'], admin_role_value='Admin', default_permission_role_values=['Admin'], protected_app_role_values={'user_management': ['Admin'], 'softwareupdate': ['Admin'], 'paintmotionrecipe': ['Admin', 'Developer'], 'contourmatchingtester': ['Admin', 'Developer']})
shell = ShellSetup(folders=[FolderSpec(folder_id=1, name='PRODUCTION', display_name='Production'), FolderSpec(folder_id=2, name='SERVICE', display_name='Service'), FolderSpec(folder_id=3, name='ADMIN', display_name='Administration'), FolderSpec(folder_id=4, name='Tests', display_name='Tests')], applications=_build_application_specs())
metadata = SystemMetadata(name='PaintSystem', version='1.0.0', description='Automated edge painting', author='Platform Team', settings_root=os.path.join('storage', 'settings'))
settings_specs = [SettingsSpec(CommonSettingsID.ROBOT_CONFIG, RobotSettingsSerializer(), 'robot/config.json'), SettingsSpec(CommonSettingsID.MOVEMENT_GROUPS, MovementGroupSettingsSerializer(), 'robot/movement_groups.json'), SettingsSpec(CommonSettingsID.ROBOT_CALIBRATION, RobotCalibrationSettingsSerializer(), 'robot/calibration.json'), SettingsSpec(CommonSettingsID.TARGETING, TargetingSettingsSerializer(), 'targeting/definitions.json'), SettingsSpec(CommonSettingsID.TOOL_CHANGER_CONFIG, ToolChangerSettingsSerializer(default_tools=tools, default_slots=tool_slots), 'tools/tool_changer.json'), SettingsSpec(CommonSettingsID.CALIBRATION_VISION_SETTINGS, CalibrationVisionSettingsSerializer(), 'vision/calibration_settings.json'), SettingsSpec(CommonSettingsID.VISION_CAMERA_SETTINGS, CameraSettingsSerializer(), 'vision/camera_settings.json'), SettingsSpec(SettingsID.CAMERAS, CameraDevicesConfigSerializer(), 'hardware/cameras.json'), SettingsSpec(CommonSettingsID.WORK_AREA_SETTINGS, WorkAreaSettingsSerializer(), 'vision/work_areas.json'), SettingsSpec(CommonSettingsID.MODBUS_CONFIG, ModbusConfigSerializer(), 'hardware/modbus.json'), SettingsSpec(SettingsID.PERIPHERALS, PeripheralConfigSerializer(), 'hardware/peripherals.json'), SettingsSpec(SettingsID.DRYER_CONFIG, DryerConfigSerializer(), 'dryer/settings.json'), SettingsSpec(SettingsID.PAINT_PROCESS_CONFIG, PaintProcessConfigSerializer(), 'paint/process.json'), SettingsSpec(SettingsID.PAINT_ADJUSTMENT_SETTINGS, PaintAdjustmentSettingsSerializer(), 'paint/adjustment.json')]
services = [ServiceSpec(CommonServiceID.ROBOT, IRobotService, required=True, description='Motion and lifecycle control'), ServiceSpec(CommonServiceID.NAVIGATION, NavigationService, required=True, description='Named position movements'), ServiceSpec(CommonServiceID.WORK_AREAS, IWorkAreaService, required=True, description='Shared work-area storage and active-area context'), ServiceSpec(CommonServiceID.VISION, IVisionService, required=False, description='Camera-based alignment', builder=build_paint_vision_service), ServiceSpec(CommonServiceID.TOOLS, IToolService, required=False, description='Tool catalog and optional magazine changer'), ServiceSpec(name=ServiceID.VACUUM_PUMP, service_type=IVacuumPumpController, required=False, description='Vacuum pump controller', builder=build_vacuum_pump_service), ServiceSpec(name=ServiceID.FAN, service_type=IFanControl, required=False, description='Fan controller', builder=build_fan_service), ServiceSpec(name=ServiceID.TRAY_FAN, service_type=IFanControl, required=False, description='Manual dryer tray fan controller', builder=build_tray_fan_service), ServiceSpec(name=ServiceID.PHYSICAL_CONTROL_BUTTONS, service_type=IPhysicalControlButtons, required=False, description='Physical start, pause, and reset buttons', builder=build_physical_control_buttons_service), ServiceSpec(name=ServiceID.VACUUM_SENSOR, service_type=IVacuumSensorService, required=False, description='Vacuum sensor service', builder=build_vacuum_sensor_service), ServiceSpec(name=ServiceID.DRYER, service_type=IDryerService, required=False, description='Managed dryer hardware service', builder=build_dryer_service)]
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def build_production_start_guard(self)
```

Return the system-specific guard used before production starts.

```python
@classmethod
def storage_path(cls, *parts: str) -> str
```

Resolve all persisted paint data beneath the selected profile root.

```python
def on_start(self) -> None
```

```python
def on_stop(self) -> None
```

```python
def apply_camera_orientation(self, role: str, horizontal: bool, vertical: bool, rotate_degrees: int=0) -> None
```

### `with_paint_system_overrides`

```python
def with_paint_system_overrides(system_class, overrides)
```

Compose a system's switches without mutating shared defaults/classes.

## `paint_system_config.py`

Source: [src/robot_systems/paint/paint_system_config.py](../../../src/robot_systems/paint/paint_system_config.py).

Top-level paint-system development and diagnostic switches. Keep temporary system-wide switches here so their active state is visible in source control and does not depend on the shell used to launch the platform.

Module declarations (expressions are shown without evaluating them):

```python
BYPASS_CONTOUR_PREPARATION = False
PAINT_DASHBOARD_APP = True
PAINT_ADJUSTMENT_APP = True
SHOW_DASHBOARD_CAMERA_PREVIEW = False
SHOW_TRAY_DASHBOARD_CAMERA_TAB = True
USE_COLLAPSIBLE_DASHBOARD_SETTINGS_PANEL = True
USE_COMBINED_PAINT_SPEED_CONTROL = True
COMBINED_PAINT_SPEED_MINIMUM_PERCENT = 10.0
COMBINED_PAINT_SPEED_MAXIMUM_PERCENT = 100.0
COMBINED_PAINT_ACCELERATION_MINIMUM_PERCENT = 1.0
COMBINED_PAINT_ACCELERATION_MAXIMUM_PERCENT = 100.0
SHOW_RESOLVED_PAINT_SPEED_VALUES = True
ALLOW_RUNNING_PAINT_SETTINGS_UPDATES = True
USE_TRAY_DRY_DURATION = True
TRAY_DRY_DURATION_MINUTES = 5
WORKPIECE_LIBRARY_APP = True
WORKPIECE_EDITOR_APP = True
CONTOUR_MATCHING_TESTER_APP = True
ROBOT_SETTINGS_APP = True
TOOL_SETTINGS_APP = True
ETHERCAT_DIAGNOSTICS_APP = False
MODBUS_SETTINGS_APP = True
NETWORK_SETTINGS_APP = True
DEVICE_CONTROL_APP = True
WORK_AREA_SETTINGS_APP = True
CAMERA_SETTINGS_APP = True
CALIBRATION_SETTINGS_APP = True
PAINT_PROCESS_SETTINGS_APP = True
CALIBRATION_APP = True
BROKER_DEBUG_APP = False
USER_MANAGEMENT_APP = True
INTRINSIC_CAPTURE_APP = False
HAND_EYE_CALIBRATION_APP = False
PICK_TARGET_APP = True
PAINT_MOTION_PLANE_SETUP_APP = False
PAINT_MOTION_RECIPE_APP = False
SHAFT_ALIGNMENT_APP = False
```

## `run_servo_pickup_test.py`

Source: [src/robot_systems/paint/run_servo_pickup_test.py](../../../src/robot_systems/paint/run_servo_pickup_test.py).

Hardware-only smoke test for the paint pickup servo descent. Run from the repository root only after positioning the robot above the test part: python src/robot_systems/paint/run_servo_pickup_test.py

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `logging`, `pathlib`, `src.bootstrap.build_engine`, `src.bootstrap.logging_config`, `src.engine.common_service_ids`, `src.engine.common_settings_ids`, `src.engine.robot.enums.axis`, `src.engine.robot.procedures`, `src.robot_systems.paint.bootstrap_provider`, `src.robot_systems.paint.component_ids`, `src.robot_systems.system_builder`, `sys`.

### `_current_z`

```python
def _current_z(robot_service) -> float
```

### `_retract_after_detection`

```python
def _retract_after_detection(robot, *, tool: int, user: int) -> bool
```

### `main`

```python
def main() -> int
```

## `service_builders.py`

Source: [src/robot_systems/paint/service_builders.py](../../../src/robot_systems/paint/service_builders.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `logging`, `src.engine.common_settings_ids`, `src.engine.hardware.communication.modbus.modbus`, `src.engine.hardware.communication.transport_registry`, `src.engine.hardware.dryer.dryer_controller`, `src.engine.hardware.dryer.dryer_service`, `src.engine.hardware.dryer.models.dryer_config`, `src.engine.hardware.dryer.models.dryer_modbus_registers`, `src.engine.hardware.fan.modbus.modbus_fan_factory`, `src.engine.hardware.peripherals`, `src.engine.hardware.physical_control_buttons.modbus.modbus_physical_control_buttons_factory`, `src.engine.hardware.vacuum_pump.modbus.modbus_vacuum_pump_factory`, `src.engine.hardware.vacuum_pump.models.vacuum_pump_config`, `src.engine.hardware.vacuum_sensor.models.vacuum_sensor_config`, `src.engine.hardware.vacuum_sensor.vacuum_sensor_service`, `src.robot_systems.default_service_builders`, `src.robot_systems.paint.component_ids`.

### `build_paint_vision_service`

```python
def build_paint_vision_service(ctx)
```

Build paint vision with an explicitly assigned primary camera.

### `build_vacuum_pump_service`

```python
def build_vacuum_pump_service(ctx)
```

### `build_fan_service`

```python
def build_fan_service(ctx)
```

### `build_tray_fan_service`

```python
def build_tray_fan_service(ctx)
```

### `build_physical_control_buttons_service`

```python
def build_physical_control_buttons_service(ctx)
```

### `build_dryer_service`

```python
def build_dryer_service(ctx)
```

### `build_vacuum_sensor_service`

```python
def build_vacuum_sensor_service(ctx)
```

Build the configured vacuum sensor using the selected slave transport.

## `timing.py`

Source: [src/robot_systems/paint/timing.py](../../../src/robot_systems/paint/timing.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `contextlib`, `contextvars`, `csv`, `dataclasses`, `datetime`, `functools`, `inspect`, `logging`, `os`, `time`, `typing`.

Module declarations (expressions are shown without evaluating them):

```python
P = ParamSpec('P')
R = TypeVar('R')
```

### `TimingRecord`

```python
@dataclass(frozen=True)
class TimingRecord:
```

Declared fields/defaults:

```python
order: int
step: str
label: str
success: bool
exception: bool
elapsed_s: float
start_offset_s: float
end_offset_s: float
```

### `StateTimingRecord`

```python
@dataclass(frozen=True)
class StateTimingRecord:
```

Declared fields/defaults:

```python
order: int
state: str
next_state: str
success: bool
exception: bool
elapsed_s: float
start_offset_s: float
end_offset_s: float
message: str = ''
```

### `TimingRecorder`

```python
class TimingRecorder:
```

Collect process timing records and emit an end-of-run summary.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, name: str) -> None
```

```python
def record(self, *, step: str, label: object | None, success: bool, elapsed_s: float, started_at: float, ended_at: float, exception: bool=False) -> None
```

```python
def record_state(self, *, state: object, next_state: object | None, success: bool, elapsed_s: float, started_at: float, ended_at: float, exception: bool=False, message: str='') -> None
```

```python
def write_csv(self, output_dir: str | None) -> str | None
```

```python
def log_summary(self, logger: logging.Logger, *, csv_path: str | None=None) -> None
```

```python
def log_state_summary(self, logger: logging.Logger) -> None
```

### `timing_session`

```python
def timing_session(name: str) -> Iterator[TimingRecorder]
```

### `timed_step`

```python
def timed_step(logger: logging.Logger, step: str, *, label_arg: str | None=None) -> Callable[[Callable[P, R]], Callable[P, R]]
```

Log elapsed time for a process/navigation step without changing behavior.

### `timed_block`

```python
def timed_block(logger: logging.Logger, step: str, *, label: object | None=None) -> Iterator[None]
```

Record a named timing block in the active timing session.

### `_result_success`

```python
def _result_success(result: object) -> bool
```

### `_record_or_log`

```python
def _record_or_log(logger: logging.Logger, *, step: str, label: object | None, success: bool, exception: bool, started: float, ended: float) -> None
```

### `_safe_name`

```python
def _safe_name(value: str) -> str
```

### `_state_name`

```python
def _state_name(value: object | None) -> str
```
