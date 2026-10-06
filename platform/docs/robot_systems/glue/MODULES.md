# Module reference: `src/robot_systems/glue`

[Package guide](README.md) · [Complete source index](../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [application_wiring.py](#application_wiringpy)
- [bootstrap_provider.py](#bootstrap_providerpy)
- [component_ids.py](#component_idspy)
- [glue_robot_system.py](#glue_robot_systempy)
- [navigation.py](#navigationpy)
- [service_builders.py](#service_builderspy)

## `__init__.py`

Source: [src/robot_systems/glue/__init__.py](../../../src/robot_systems/glue/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `application_wiring.py`

Source: [src/robot_systems/glue/application_wiring.py](../../../src/robot_systems/glue/application_wiring.py).

Imports (including optional/function-local imports; not a startup dependency list): `logging`, `src.applications.aruco_z_probe.aruco_z_probe_factory`, `src.applications.aruco_z_probe.service.aruco_z_probe_application_service`, `src.applications.base.robot_jog_service_builder`, `src.applications.base.widget_application`, `src.applications.broker_debug.broker_debug_factory`, `src.applications.broker_debug.service.broker_debug_application_service`, `src.applications.calibration.calibration_factory`, `src.applications.calibration.service.calibration_application_service`, `src.applications.calibration_settings`, `src.applications.camera_settings.camera_settings_factory`, `src.applications.camera_settings.service.camera_settings_application_service`, `src.applications.contour_matching_tester.contour_matching_tester_factory`, `src.applications.contour_matching_tester.service.contour_matching_tester_service`, `src.applications.device_control.device_control_factory`, `src.applications.device_control.service.device_control_application_service`, `src.applications.device_control.service.i_device_control_service`, `src.applications.glue_cell_settings`, `src.applications.height_measuring.height_measuring_factory`, `src.applications.height_measuring.service.height_measuring_application_service`, `src.applications.intrinsic_calibration_capture.intrinsic_capture_factory`, `src.applications.intrinsic_calibration_capture.service.intrinsic_capture_service`, `src.applications.modbus_settings`, `src.applications.network_settings.build_application`, `src.applications.pick_and_place_visualizer`, `src.applications.pick_and_place_visualizer.service.pick_and_place_visualizer_service`, `src.applications.pick_target.pick_target_factory`, `src.applications.pick_target.service.pick_target_application_service`, `src.applications.robot_settings.robot_settings_factory`, `src.applications.robot_settings.service.robot_settings_application_service`, `src.applications.software_update.build_application`, `src.applications.tool_settings`, `src.applications.user_management.domain.csv_user_repository`, `src.applications.user_management.service.user_management_application_service`, `src.applications.user_management.user_management_factory`, `src.applications.work_area_settings.service.work_area_settings_application_service`, `src.applications.work_area_settings.work_area_settings_factory`, `src.applications.workpiece_editor.editor_core.config`, `src.applications.workpiece_editor.service.workpiece_editor_service`, `src.applications.workpiece_editor.workpiece_editor_factory`, `src.applications.workpiece_library.workpiece_library_factory`, `src.engine.auth.authorization_service`, `src.engine.auth.json_permissions_repository`, `src.engine.common_service_ids`, `src.engine.common_settings_ids`, `src.engine.hardware.communication.modbus.modbus_action_service`, `src.engine.robot.calibration.aruco_marker_height_mapping_service`, `src.engine.robot.calibration.calibration_navigation_service`, `src.engine.robot.calibration.camera_tcp_offset_calibration_service`, `src.engine.robot.calibration.camera_z_shift_calibration_service`, `src.engine.robot.calibration.ros_tool_registry_client`, `src.engine.robot.calibration.service_builders`, `src.engine.robot.configuration.robot_settings`, `src.engine.robot.path_preparation`, `src.engine.vision.capture_snapshot_service`, `src.engine.vision.homography_residual_transformer`, `src.robot_systems.glue.applications.dashboard.glue_dashboard`, `src.robot_systems.glue.applications.dispense_channel_settings`, `src.robot_systems.glue.applications.glue_process_driver`, `src.robot_systems.glue.applications.glue_settings`, `src.robot_systems.glue.component_ids`, `src.robot_systems.glue.domain.glue_job_builder_service`, `src.robot_systems.glue.domain.glue_job_execution_service`, `src.robot_systems.glue.domain.glue_workpiece_editor_adapter`, `src.robot_systems.glue.domain.matching.matching_service`, `src.robot_systems.glue.domain.users`, `src.robot_systems.glue.domain.workpieces.glue_workpiece_library_service`, `src.robot_systems.glue.domain.workpieces.repository.json_workpiece_repository`, `src.robot_systems.glue.domain.workpieces.schemas`, `src.robot_systems.glue.domain.workpieces.service.workpiece_service`, `src.robot_systems.glue.processes.pick_and_place.config`, `src.robot_systems.glue.targeting.settings_adapter`, `src.shared_contracts.events.workpiece_events`.

### `_build_capture_snapshot_service`

```python
def _build_capture_snapshot_service(robot_system)
```

### `_build_pick_and_place_visualizer`

```python
def _build_pick_and_place_visualizer(robot_system)
```

### `_build_contour_matching_tester`

```python
def _build_contour_matching_tester(robot_system)
```

### `_build_glue_process_driver_application`

```python
def _build_glue_process_driver_application(robot_system)
```

### `_get_tools`

```python
def _get_tools(robot_system) -> list
```

### `_build_tool_settings_application`

```python
def _build_tool_settings_application(robot_system)
```

### `_build_workpiece_library_application`

```python
def _build_workpiece_library_application(robot_system)
```

### `_build_workpiece_editor_application`

```python
def _build_workpiece_editor_application(robot_system)
```

### `_build_user_management_application`

```python
def _build_user_management_application(robot_system)
```

### `_build_camera_settings_application`

```python
def _build_camera_settings_application(robot_system)
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

### `_build_dashboard_application`

```python
def _build_dashboard_application(system)
```

### `_build_broker_debug_application`

```python
def _build_broker_debug_application(robot_system)
```

### `_build_glue_cell_settings_application`

```python
def _build_glue_cell_settings_application(robot_app)
```

### `_build_dispense_channel_settings_application`

```python
def _build_dispense_channel_settings_application(robot_app)
```

### `_build_robot_settings_application`

```python
def _build_robot_settings_application(robot_app)
```

### `_build_glue_settings_application`

```python
def _build_glue_settings_application(robot_app)
```

### `_build_modbus_settings_application`

```python
def _build_modbus_settings_application(robot_app)
```

### `_build_pick_target_application`

```python
def _build_pick_target_application(robot_system)
```

### `_build_device_control_application`

```python
def _build_device_control_application(robot_system)
```

### `_build_intrinsic_capture_application`

```python
def _build_intrinsic_capture_application(robot_system)
```

### `_build_aruco_z_probe_application`

```python
def _build_aruco_z_probe_application(robot_system)
```

### `_build_height_measuring_application`

```python
def _build_height_measuring_application(robot_app)
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

Source: [src/robot_systems/glue/bootstrap_provider.py](../../../src/robot_systems/glue/bootstrap_provider.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.applications.login.login_application_service`, `src.applications.login.login_factory`, `src.applications.user_management.domain.auth_user_repository_adapter`, `src.applications.user_management.domain.csv_user_repository`, `src.engine.auth.authentication_service`, `src.engine.auth.authorization_service`, `src.engine.auth.json_permissions_repository`, `src.engine.common_service_ids`, `src.engine.robot.drivers.ros2_robot`, `src.robot_systems.glue.domain.users`, `src.robot_systems.glue.glue_robot_system`, `src.robot_systems.robot_system_bootstrap_provider`.

### `GlueBootstrapProvider`

```python
class GlueBootstrapProvider(RobotSystemBootstrapProvider):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

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

Source: [src/robot_systems/glue/component_ids.py](../../../src/robot_systems/glue/component_ids.py).

Imports (including optional/function-local imports; not a startup dependency list): `enum`.

### `ServiceID`

```python
class ServiceID(str, Enum):
```

Declared fields/defaults:

```python
WEIGHT = 'weight'
MOTOR = 'motor'
HEIGHT_MEASURING = 'height_measuring'
VACUUM_PUMP = 'vacuum_pump'
```

### `SettingsID`

```python
class SettingsID(str, Enum):
```

Declared fields/defaults:

```python
GLUE_SETTINGS = 'glue_settings'
GLUE_CELLS = 'glue_cells'
DISPENSE_CHANNELS = 'dispense_channels'
GLUE_CATALOG = 'glue_catalog'
GLUE_MOTOR_CONFIG = 'glue_motor_config'
```

### `ProcessID`

```python
class ProcessID(str, Enum):
```

Declared fields/defaults:

```python
GLUE = 'glue'
PICK_AND_PLACE = 'pick_and_place'
CLEAN = 'clean'
ROBOT_CALIBRATION = 'robot_calibration'
COORDINATOR = 'coordinator'
```

## `glue_robot_system.py`

Source: [src/robot_systems/glue/glue_robot_system.py](../../../src/robot_systems/glue/glue_robot_system.py).

Imports (including optional/function-local imports; not a startup dependency list): `os`, `src.engine.common_service_ids`, `src.engine.common_settings_ids`, `src.engine.hardware.communication.modbus.modbus`, `src.engine.hardware.motor.interfaces.i_motor_service`, `src.engine.hardware.vacuum_pump.interfaces.i_vacuum_pump_controller`, `src.engine.hardware.weight.interfaces.i_weight_cell_service`, `src.engine.process.process_requirements`, `src.engine.robot.calibration.service_builders`, `src.engine.robot.configuration`, `src.engine.robot.features.navigation_service`, `src.engine.robot.height_measuring`, `src.engine.robot.height_measuring.depth_map_data`, `src.engine.robot.height_measuring.laser_calibration_data`, `src.engine.robot.height_measuring.settings`, `src.engine.robot.interfaces.i_robot_service`, `src.engine.robot.interfaces.i_tool_service`, `src.engine.robot.targeting`, `src.engine.vision.calibration_vision_settings`, `src.engine.vision.camera_settings_serializer`, `src.engine.vision.capture_snapshot_service`, `src.engine.vision.i_vision_service`, `src.engine.work_areas`, `src.robot_systems.base_robot_system`, `src.robot_systems.glue`, `src.robot_systems.glue.calibration.provider`, `src.robot_systems.glue.component_ids`, `src.robot_systems.glue.domain.dispense_channels.dispense_channel_service`, `src.robot_systems.glue.domain.glue_job_builder_service`, `src.robot_systems.glue.domain.glue_job_execution_service`, `src.robot_systems.glue.domain.matching.matching_service`, `src.robot_systems.glue.domain.workpieces.repository.json_workpiece_repository`, `src.robot_systems.glue.domain.workpieces.service.workpiece_service`, `src.robot_systems.glue.height_measuring.provider`, `src.robot_systems.glue.navigation`, `src.robot_systems.glue.processes.clean_process`, `src.robot_systems.glue.processes.glue_dispensing.dispensing_config`, `src.robot_systems.glue.processes.glue_dispensing.glue_pump_controller`, `src.robot_systems.glue.processes.glue_operation_coordinator`, `src.robot_systems.glue.processes.glue_process`, `src.robot_systems.glue.processes.pick_and_place.config`, `src.robot_systems.glue.processes.pick_and_place_process`, `src.robot_systems.glue.processes.robot_calibration_process`, `src.robot_systems.glue.service_builders`, `src.robot_systems.glue.settings.cells`, `src.robot_systems.glue.settings.device_control`, `src.robot_systems.glue.settings.dispense_channels`, `src.robot_systems.glue.settings.glue`, `src.robot_systems.glue.settings.glue_types`, `src.robot_systems.glue.targeting.provider`, `src.shared_contracts.declarations`.

### `GlueRobotSystem`

```python
class GlueRobotSystem(BaseRobotSystem):
```

Declared fields/defaults:

```python
dispense_channels = [DispenseChannelDefinition(id='channel_1', label='Channel 1', weight_cell_id=0, pump_motor_address=0, default_glue_type=''), DispenseChannelDefinition(id='channel_2', label='Channel 2', weight_cell_id=1, pump_motor_address=2, default_glue_type=''), DispenseChannelDefinition(id='channel_3', label='Channel 3', weight_cell_id=2, pump_motor_address=4, default_glue_type='')]
tools = [ToolDefinition(id=1, name='Single Gripper')]
tool_slots = [ToolSlotDefinition(id=11, tool_id=1, pickup_movement_group_id='SLOT 11 PICKUP', dropoff_movement_group_id='SLOT 11 DROPOFF')]
movement_groups = [MovementGroupDefinition(id='LOGIN', label='Login', group_type=MovementGroupType.SINGLE_POSITION, has_trajectory_execution=True), MovementGroupDefinition(id='HOME', label='Home', group_type=MovementGroupType.SINGLE_POSITION, has_trajectory_execution=True), MovementGroupDefinition(id='CALIBRATION', label='Calibration', group_type=MovementGroupType.SINGLE_POSITION, has_trajectory_execution=True), MovementGroupDefinition(id='CLEAN', label='Clean', group_type=MovementGroupType.MULTI_POSITION, has_iterations=True, has_trajectory_execution=True), MovementGroupDefinition(id='JOG', label='Jog', group_type=MovementGroupType.VELOCITY_ONLY), MovementGroupDefinition(id='SLOT 11 PICKUP', label='Slot 11 Pickup', group_type=MovementGroupType.MULTI_POSITION, has_trajectory_execution=True), MovementGroupDefinition(id='SLOT 11 DROPOFF', label='Slot 11 Dropoff', group_type=MovementGroupType.MULTI_POSITION, has_trajectory_execution=True)]
target_points = [RemoteTcpDefinition(name='camera', display_name='camera'), RemoteTcpDefinition(name='tool', display_name='tool'), RemoteTcpDefinition(name='gripper', display_name='gripper')]
target_frames = [TargetFrameDefinition(name='calibration', work_area_id='spray', use_height_correction=True), TargetFrameDefinition(name='pickup', work_area_id='pickup', source_navigation_group='CALIBRATION', target_navigation_group='HOME', use_height_correction=False)]
work_areas = [WorkAreaDefinition(id='pickup', label='Pickup', color='#50DC64', threshold_profile='pickup', supports_detection_roi=True, supports_brightness_roi=True, supports_height_mapping=True), WorkAreaDefinition(id='spray', label='Spray', color='#FF8C32', threshold_profile='default', supports_detection_roi=True, supports_brightness_roi=True, supports_height_mapping=True)]
work_area_observers = [WorkAreaObserverBinding(area_id='pickup', movement_group_id='HOME'), WorkAreaObserverBinding(area_id='spray', movement_group_id='CALIBRATION')]
default_active_work_area_id = 'pickup'
role_policy = RolePolicy(role_values=['Admin', 'Operator', 'Viewer', 'Developer'], admin_role_value='Admin', default_permission_role_values=['Admin'], protected_app_role_values={'user_management': ['Admin'], 'softwareupdate': ['Admin']})
shell = ShellSetup(folders=[FolderSpec(folder_id=1, name='PRODUCTION', display_name='Production'), FolderSpec(folder_id=2, name='SERVICE', display_name='Service'), FolderSpec(folder_id=3, name='ADMIN', display_name='Administration')], applications=[ApplicationSpec(name='GlueDashboard', folder_id=1, icon='fa5s.tachometer-alt', factory=application_wiring._build_dashboard_application), ApplicationSpec(name='RobotSettings', folder_id=2, icon='mdi.robot-industrial', factory=application_wiring._build_robot_settings_application), ApplicationSpec(name='GlueSettings', folder_id=2, icon='ph.drop-light', factory=application_wiring._build_glue_settings_application), ApplicationSpec(name='ModbusSettings', folder_id=2, icon='fa5s.network-wired', factory=application_wiring._build_modbus_settings_application), ApplicationSpec(name='SoftwareUpdate', folder_id=3, icon='fa5s.download', factory=application_wiring._build_software_update_application), ApplicationSpec(name='NetworkSettings', folder_id=2, icon='fa5s.wifi', factory=application_wiring._build_network_settings_application), ApplicationSpec(name='DispenseChannelSettings', folder_id=2, icon='fa5s.weight', factory=application_wiring._build_dispense_channel_settings_application), ApplicationSpec(name='WorkAreaSettings', folder_id=2, icon='fa5s-vector-square', factory=application_wiring._build_work_area_settings_application), ApplicationSpec(name='CameraSettings', folder_id=2, icon='fa5s.camera', factory=application_wiring._build_camera_settings_application), ApplicationSpec(name='CalibrationSettings', folder_id=2, icon='fa5s.sliders-h', factory=application_wiring._build_calibration_settings_application), ApplicationSpec(name='DeviceControl', folder_id=2, icon='fa5s.sliders-h', factory=application_wiring._build_device_control_application), ApplicationSpec(name='Calibration', folder_id=2, icon='fa5s.crosshairs', factory=application_wiring._build_calibration_application), ApplicationSpec(name='BrokerDebug', folder_id=4, icon='fa5s.project-diagram', factory=application_wiring._build_broker_debug_application), ApplicationSpec(name='WorkpieceEditor', folder_id=1, icon='fa5s.draw-polygon', factory=application_wiring._build_workpiece_editor_application), ApplicationSpec(name='UserManagement', folder_id=3, icon='fa5s.users-cog', factory=application_wiring._build_user_management_application), ApplicationSpec(name='WorkpieceLibrary', folder_id=1, icon='fa5s.book-open', factory=application_wiring._build_workpiece_library_application), ApplicationSpec(name='ToolSettings', folder_id=2, icon='fa5s.tools', factory=application_wiring._build_tool_settings_application), ApplicationSpec(name='ContourMatchingTester', folder_id=4, icon='fa6s.shapes', factory=application_wiring._build_contour_matching_tester), ApplicationSpec(name='GlueProcessDriver', folder_id=4, icon='fa5s.vials', factory=application_wiring._build_glue_process_driver_application), ApplicationSpec(name='HeightMeasuring', folder_id=4, icon='fa5s.ruler-vertical', factory=application_wiring._build_height_measuring_application), ApplicationSpec(name='PickAndPlaceVisualizer', folder_id=4, icon='fa5s.map-marked', factory=application_wiring._build_pick_and_place_visualizer), ApplicationSpec(name='PickTarget', folder_id=4, icon='fa5s.crosshairs', factory=application_wiring._build_pick_target_application), ApplicationSpec(name='ArucoZProbe', folder_id=4, icon='fa5s.search', factory=application_wiring._build_aruco_z_probe_application), ApplicationSpec(name='IntrinsicCapture', folder_id=4, icon='fa5s.camera-retro', factory=application_wiring._build_intrinsic_capture_application)])
metadata = SystemMetadata(name='GlueSystem', version='1.0.0', description='Automated glue dispensing vision_service', author='Platform Team', settings_root=os.path.join('storage', 'settings'))
settings_specs = [SettingsSpec(CommonSettingsID.ROBOT_CONFIG, RobotSettingsSerializer(), 'robot/config.json'), SettingsSpec(CommonSettingsID.MOVEMENT_GROUPS, MovementGroupSettingsSerializer(), 'robot/movement_groups.json'), SettingsSpec(CommonSettingsID.ROBOT_CALIBRATION, RobotCalibrationSettingsSerializer(), 'robot/calibration.json'), SettingsSpec(SettingsID.GLUE_SETTINGS, GlueSettingsSerializer(), 'glue/settings.json'), SettingsSpec(CommonSettingsID.TARGETING, TargetingSettingsSerializer(), 'targeting/definitions.json'), SettingsSpec(SettingsID.GLUE_CELLS, GlueCellsConfigSerializer(default_channels=dispense_channels), 'glue/cells.json'), SettingsSpec(SettingsID.DISPENSE_CHANNELS, DispenseChannelSettingsSerializer(default_channels=dispense_channels), 'glue/dispense_channels.json'), SettingsSpec(SettingsID.GLUE_CATALOG, GlueCatalogSerializer(), 'glue/catalog.json'), SettingsSpec(CommonSettingsID.MODBUS_CONFIG, ModbusConfigSerializer(), 'hardware/modbus.json'), SettingsSpec(CommonSettingsID.CALIBRATION_VISION_SETTINGS, CalibrationVisionSettingsSerializer(), 'vision/calibration_settings.json'), SettingsSpec(CommonSettingsID.VISION_CAMERA_SETTINGS, CameraSettingsSerializer(), 'vision/camera_settings.json'), SettingsSpec(CommonSettingsID.WORK_AREA_SETTINGS, WorkAreaSettingsSerializer(), 'vision/work_areas.json'), SettingsSpec(CommonSettingsID.TOOL_CHANGER_CONFIG, ToolChangerSettingsSerializer(default_tools=tools, default_slots=tool_slots), 'tools/tool_changer.json'), SettingsSpec(CommonSettingsID.HEIGHT_MEASURING_SETTINGS, HeightMeasuringSettingsSerializer(), 'height_measuring/settings.json'), SettingsSpec(CommonSettingsID.HEIGHT_MEASURING_CALIBRATION, LaserCalibrationDataSerializer(), 'height_measuring/calibration_data.json'), SettingsSpec(CommonSettingsID.DEPTH_MAP_DATA, DepthMapDataSerializer(), 'height_measuring/depth_map.json'), SettingsSpec(SettingsID.GLUE_MOTOR_CONFIG, GlueMotorConfigSerializer(default_channels=dispense_channels), 'hardware/motors.json')]
services = [ServiceSpec(CommonServiceID.ROBOT, IRobotService, required=True, description='Motion and lifecycle control'), ServiceSpec(CommonServiceID.NAVIGATION, NavigationService, required=True, description='Named position movements'), ServiceSpec(CommonServiceID.WORK_AREAS, IWorkAreaService, required=True, description='Shared work-area storage and active-area context'), ServiceSpec(CommonServiceID.VISION, IVisionService, required=False, description='Camera-based alignment'), ServiceSpec(name=ServiceID.WEIGHT, service_type=IWeightCellService, required=True, description='Multi-cell weight monitoring', builder=build_weight_cell_service), ServiceSpec(name=ServiceID.MOTOR, service_type=IMotorService, required=True, description='Glue pump motor service', builder=build_motor_service), ServiceSpec(name=ServiceID.VACUUM_PUMP, service_type=IVacuumPumpController, required=False, description='Vacuum pump controller', builder=build_vacuum_pump_service), ServiceSpec(name=CommonServiceID.TOOLS, service_type=IToolService, required=False, description='Gripper / tool changer')]
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def on_start(self) -> None
```

```python
def on_stop(self) -> None
```

```python
@property
def coordinator(self)
```

## `navigation.py`

Source: [src/robot_systems/glue/navigation.py](../../../src/robot_systems/glue/navigation.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.robot.features.navigation_service`, `src.engine.robot.interfaces.i_robot_service`, `src.engine.vision`, `src.engine.work_areas.i_work_area_service`, `traceback`, `typing`.

### `GlueNavigationService`

```python
class GlueNavigationService:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, navigation: NavigationService, vision: Optional[IVisionService]=None, robot_service: Optional[IRobotService]=None, work_area_service: Optional[IWorkAreaService]=None, observed_area_by_group: Optional[dict[str, str]]=None)
```

```python
def move_home(self) -> bool
```

```python
def move_to_login_position(self) -> bool
```

```python
def move_to_calibration_position(self, z_offset: float=0.0, wait_cancelled: Callable[[], bool] | None=None) -> bool
```

```python
def move_to(self, group_name: str, z_offset: float=0.0, wait_cancelled: Callable[[], bool] | None=None) -> bool
```

```python
def move_linear(self, group_name: str) -> bool
```

```python
def move_to_group(self, group_name: str, wait_cancelled: Callable[[], bool] | None=None) -> bool
```

```python
def move_linear_group(self, group_name: str) -> bool
```

```python
def move_to_position(self, position: list, group_name: str, wait_cancelled: Callable[[], bool] | None=None) -> bool
```

```python
def get_group_names(self) -> list[str]
```

```python
def get_group_position(self, group_name: str) -> list[float] | None
```

## `service_builders.py`

Source: [src/robot_systems/glue/service_builders.py](../../../src/robot_systems/glue/service_builders.py).

Imports (including optional/function-local imports; not a startup dependency list): `logging`, `src.engine.common_service_ids`, `src.engine.common_settings_ids`, `src.engine.hardware.generator.modbus.modbus_generator_factory`, `src.engine.hardware.motor.modbus.modbus_motor_factory`, `src.engine.hardware.motor.models.motor_config`, `src.engine.hardware.weight.http.http_weight_cell_factory`, `src.robot_systems.glue.component_ids`, `src.robot_systems.glue.domain.vacuum_pump`, `src.robot_systems.glue.motor.glue_motor_error_decoder`, `src.robot_systems.glue.processes.glue_dispensing.i_glue_type_resolver`.

### `_build_generator_service`

```python
def _build_generator_service(robot_system)
```

### `build_weight_cell_service`

```python
def build_weight_cell_service(ctx)
```

### `build_motor_service`

```python
def build_motor_service(ctx)
```

### `build_vacuum_pump_service`

```python
def build_vacuum_pump_service(ctx)
```

### `GlueCellTypeResolver`

```python
class GlueCellTypeResolver(IGlueTypeResolver):
```

Maps glue_type string → motor_address int from the live GlueCellsConfig.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, glue_cells_config) -> None
```

```python
def resolve(self, glue_type: str) -> int
```
