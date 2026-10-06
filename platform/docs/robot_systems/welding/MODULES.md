# Module reference: `src/robot_systems/welding`

[Package guide](README.md) · [Complete source index](../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [application_wiring.py](#application_wiringpy)
- [bootstrap_provider.py](#bootstrap_providerpy)
- [component_ids.py](#component_idspy)
- [navigation.py](#navigationpy)
- [welding_robot_system.py](#welding_robot_systempy)
- [workpiece_path_executor.py](#workpiece_path_executorpy)

## `__init__.py`

Source: [src/robot_systems/welding/__init__.py](../../../src/robot_systems/welding/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.robot_systems.welding.welding_robot_system`.

Package-level import/export surface:

```python
from src.robot_systems.welding.welding_robot_system import WeldingRobotSystem
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['WeldingRobotSystem']
```

## `application_wiring.py`

Source: [src/robot_systems/welding/application_wiring.py](../../../src/robot_systems/welding/application_wiring.py).

Imports (including optional/function-local imports; not a startup dependency list): `json`, `logging`, `os`, `src.applications.base.robot_jog_service_builder`, `src.applications.base.widget_application`, `src.applications.broker_debug.broker_debug_factory`, `src.applications.broker_debug.service.broker_debug_application_service`, `src.applications.calibration.calibration_factory`, `src.applications.calibration.service.calibration_application_service`, `src.applications.calibration_settings`, `src.applications.camera_settings.camera_settings_factory`, `src.applications.camera_settings.service.camera_settings_application_service`, `src.applications.hand_eye_calibration.hand_eye_calibration_factory`, `src.applications.hand_eye_calibration.service.hand_eye_service`, `src.applications.intrinsic_calibration_capture.intrinsic_capture_factory`, `src.applications.intrinsic_calibration_capture.service.intrinsic_capture_service`, `src.applications.network_settings.build_application`, `src.applications.robot_settings.robot_settings_factory`, `src.applications.robot_settings.service.robot_settings_application_service`, `src.applications.software_update.build_application`, `src.applications.user_management.domain.csv_user_repository`, `src.applications.user_management.service.user_management_application_service`, `src.applications.user_management.user_management_factory`, `src.applications.work_area_settings.service.work_area_settings_application_service`, `src.applications.work_area_settings.work_area_settings_factory`, `src.applications.workpiece_editor.editor_core.config`, `src.applications.workpiece_editor.service.workpiece_editor_service`, `src.applications.workpiece_editor.workpiece_editor_factory`, `src.engine.auth.authorization_service`, `src.engine.auth.json_permissions_repository`, `src.engine.common_service_ids`, `src.engine.common_settings_ids`, `src.engine.robot.calibration.aruco_marker_height_mapping_service`, `src.engine.robot.calibration.calibration_navigation_service`, `src.engine.robot.calibration.camera_tcp_offset_calibration_service`, `src.engine.robot.calibration.camera_z_shift_calibration_service`, `src.engine.robot.calibration.service_builders`, `src.engine.robot.path_preparation`, `src.engine.vision.capture_snapshot_service`, `src.engine.vision.homography_residual_transformer`, `src.robot_systems.welding.applications.dashboard`, `src.robot_systems.welding.domain.contour_editor_schema`, `src.robot_systems.welding.domain.users`, `src.robot_systems.welding.targeting.settings_adapter`, `src.robot_systems.welding.workpiece_path_executor`, `src.shared_contracts.events.process_events`.

### `_build_dashboard_application`

```python
def _build_dashboard_application(robot_system)
```

### `_build_capture_snapshot_service`

```python
def _build_capture_snapshot_service(robot_system)
```

### `_build_welding_contour_editor_application`

```python
def _build_welding_contour_editor_application(robot_system)
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

### `_build_broker_debug_application`

```python
def _build_broker_debug_application(robot_system)
```

### `_build_robot_settings_application`

```python
def _build_robot_settings_application(robot_app)
```

### `_build_intrinsic_capture_application`

```python
def _build_intrinsic_capture_application(robot_system)
```

### `_build_hand_eye_calibration_application`

```python
def _build_hand_eye_calibration_application(robot_system)
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

Source: [src/robot_systems/welding/bootstrap_provider.py](../../../src/robot_systems/welding/bootstrap_provider.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.applications.login.login_application_service`, `src.applications.login.login_factory`, `src.applications.user_management.domain.auth_user_repository_adapter`, `src.applications.user_management.domain.csv_user_repository`, `src.engine.auth.authentication_service`, `src.engine.auth.authorization_service`, `src.engine.auth.json_permissions_repository`, `src.engine.common_service_ids`, `src.engine.robot.drivers.ros2_robot`, `src.robot_systems.robot_system_bootstrap_provider`, `src.robot_systems.welding.domain.users`, `src.robot_systems.welding.welding_robot_system`.

### `WeldingBootstrapProvider`

```python
class WeldingBootstrapProvider(RobotSystemBootstrapProvider):
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

Source: [src/robot_systems/welding/component_ids.py](../../../src/robot_systems/welding/component_ids.py).

Imports (including optional/function-local imports; not a startup dependency list): `enum`.

### `ServiceID`

```python
class ServiceID(str, Enum):
```

Declared fields/defaults:

```python
CUSTOM_DEVICE = 'custom_device'
```

### `SettingsID`

```python
class SettingsID(str, Enum):
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

Source: [src/robot_systems/welding/navigation.py](../../../src/robot_systems/welding/navigation.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.robot.features.navigation_service`, `src.engine.robot.interfaces.i_robot_service`, `src.engine.vision`, `src.engine.work_areas.i_work_area_service`, `traceback`, `typing`.

### `WeldingNavigationService`

```python
class WeldingNavigationService:
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

## `welding_robot_system.py`

Source: [src/robot_systems/welding/welding_robot_system.py](../../../src/robot_systems/welding/welding_robot_system.py).

Imports (including optional/function-local imports; not a startup dependency list): `os`, `src.engine.common_service_ids`, `src.engine.common_settings_ids`, `src.engine.robot.calibration.robot_calibration_process`, `src.engine.robot.calibration.service_builders`, `src.engine.robot.configuration`, `src.engine.robot.features.navigation_service`, `src.engine.robot.height_measuring`, `src.engine.robot.height_measuring.depth_map_data`, `src.engine.robot.interfaces.i_robot_service`, `src.engine.robot.targeting`, `src.engine.vision.calibration_vision_settings`, `src.engine.vision.camera_settings_serializer`, `src.engine.vision.i_vision_service`, `src.engine.work_areas`, `src.robot_systems.base_robot_system`, `src.robot_systems.welding`, `src.robot_systems.welding.applications.dashboard.service.welding_dashboard_service`, `src.robot_systems.welding.calibration.coordinator`, `src.robot_systems.welding.calibration.provider`, `src.robot_systems.welding.component_ids`, `src.robot_systems.welding.height_measuring.provider`, `src.robot_systems.welding.navigation`, `src.robot_systems.welding.processes`, `src.robot_systems.welding.targeting.provider`, `src.shared_contracts.declarations`.

### `WeldingRobotSystem`

```python
class WeldingRobotSystem(BaseRobotSystem):
```

Declared fields/defaults:

```python
movement_groups = [MovementGroupDefinition(id='HOME', label='Home', group_type=MovementGroupType.SINGLE_POSITION, has_trajectory_execution=True), MovementGroupDefinition(id='CALIBRATION', label='Calibration', group_type=MovementGroupType.SINGLE_POSITION, has_trajectory_execution=True), MovementGroupDefinition(id='CAMERA_CALIBRATION', label='Camera Calibration', group_type=MovementGroupType.SINGLE_POSITION, has_trajectory_execution=True), MovementGroupDefinition(id='JOG', label='Jog', group_type=MovementGroupType.VELOCITY_ONLY), MovementGroupDefinition(id='WELDINGING', label='Weldinging', group_type=MovementGroupType.SINGLE_POSITION, has_trajectory_execution=True)]
target_points = [RemoteTcpDefinition(name='camera', display_name='camera'), RemoteTcpDefinition(name='tool', display_name='tool')]
target_frames = [TargetFrameDefinition(name='calibration', work_area_id='welding', use_height_correction=True)]
work_areas = [WorkAreaDefinition(id='welding', label='Welding', color='#FF8C32', threshold_profile='default', supports_detection_roi=True, supports_brightness_roi=True, supports_height_mapping=True)]
work_area_observers = [WorkAreaObserverBinding(area_id='welding', movement_group_id='CALIBRATION')]
default_active_work_area_id = 'welding'
role_policy = RolePolicy(role_values=['Admin', 'Operator', 'Viewer', 'Developer'], admin_role_value='Admin', default_permission_role_values=['Admin'], protected_app_role_values={'user_management': ['Admin'], 'softwareupdate': ['Admin']})
shell = ShellSetup(folders=[FolderSpec(folder_id=1, name='PRODUCTION', display_name='Production'), FolderSpec(folder_id=2, name='SERVICE', display_name='Service'), FolderSpec(folder_id=3, name='ADMIN', display_name='Administration'), FolderSpec(folder_id=4, name='Tests', display_name='Tests')], applications=[ApplicationSpec(name='WeldingDashboard', folder_id=1, icon='fa5s.tachometer-alt', factory=application_wiring._build_dashboard_application), ApplicationSpec(name='WeldingContourEditor', folder_id=1, icon='fa5s.draw-polygon', factory=application_wiring._build_welding_contour_editor_application), ApplicationSpec(name='RobotSettings', folder_id=2, icon='mdi.robot-industrial', factory=application_wiring._build_robot_settings_application), ApplicationSpec(name='SoftwareUpdate', folder_id=3, icon='fa5s.download', factory=application_wiring._build_software_update_application), ApplicationSpec(name='NetworkSettings', folder_id=2, icon='fa5s.wifi', factory=application_wiring._build_network_settings_application), ApplicationSpec(name='WorkAreaSettings', folder_id=2, icon='fa5s-vector-square', factory=application_wiring._build_work_area_settings_application), ApplicationSpec(name='CameraSettings', folder_id=2, icon='fa5s.camera', factory=application_wiring._build_camera_settings_application), ApplicationSpec(name='CalibrationSettings', folder_id=2, icon='fa5s.sliders-h', factory=application_wiring._build_calibration_settings_application), ApplicationSpec(name='Calibration', folder_id=2, icon='fa5s.crosshairs', factory=application_wiring._build_calibration_application), ApplicationSpec(name='BrokerDebug', folder_id=4, icon='fa5s.project-diagram', factory=application_wiring._build_broker_debug_application), ApplicationSpec(name='UserManagement', folder_id=3, icon='fa5s.users-cog', factory=application_wiring._build_user_management_application), ApplicationSpec(name='IntrinsicCapture', folder_id=4, icon='fa5s.camera-retro', factory=application_wiring._build_intrinsic_capture_application), ApplicationSpec(name='HandEyeCalibration', folder_id=4, icon='fa5s.hand-paper', factory=application_wiring._build_hand_eye_calibration_application)])
metadata = SystemMetadata(name='WeldingSystem', version='1.0.0', description='Automated edge weldinging', author='Platform Team', settings_root=os.path.join('storage', 'settings'))
settings_specs = [SettingsSpec(CommonSettingsID.ROBOT_CONFIG, RobotSettingsSerializer(), 'robot/config.json'), SettingsSpec(CommonSettingsID.MOVEMENT_GROUPS, MovementGroupSettingsSerializer(), 'robot/movement_groups.json'), SettingsSpec(CommonSettingsID.ROBOT_CALIBRATION, RobotCalibrationSettingsSerializer(), 'robot/calibration.json'), SettingsSpec(CommonSettingsID.TARGETING, TargetingSettingsSerializer(), 'targeting/definitions.json'), SettingsSpec(CommonSettingsID.CALIBRATION_VISION_SETTINGS, CalibrationVisionSettingsSerializer(), 'vision/calibration_settings.json'), SettingsSpec(CommonSettingsID.VISION_CAMERA_SETTINGS, CameraSettingsSerializer(), 'vision/camera_settings.json'), SettingsSpec(CommonSettingsID.WORK_AREA_SETTINGS, WorkAreaSettingsSerializer(), 'vision/work_areas.json'), SettingsSpec(CommonSettingsID.HEIGHT_MEASURING_SETTINGS, HeightMeasuringSettingsSerializer(), 'height_measuring/settings.json'), SettingsSpec(CommonSettingsID.HEIGHT_MEASURING_CALIBRATION, LaserCalibrationDataSerializer(), 'height_measuring/calibration_data.json'), SettingsSpec(CommonSettingsID.DEPTH_MAP_DATA, DepthMapDataSerializer(), 'height_measuring/depth_map.json')]
services = [ServiceSpec(CommonServiceID.ROBOT, IRobotService, required=True, description='Motion and lifecycle control'), ServiceSpec(CommonServiceID.NAVIGATION, NavigationService, required=True, description='Named position movements'), ServiceSpec(CommonServiceID.WORK_AREAS, IWorkAreaService, required=True, description='Shared work-area storage and active-area context'), ServiceSpec(CommonServiceID.VISION, IVisionService, required=False, description='Camera-based alignment')]
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def on_start(self) -> None
```

```python
def on_stop(self) -> None
```

## `workpiece_path_executor.py`

Source: [src/robot_systems/welding/workpiece_path_executor.py](../../../src/robot_systems/welding/workpiece_path_executor.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `logging`, `src.applications.workpiece_editor.service.i_workpiece_path_executor`, `src.engine.robot.path_preparation`.

### `WeldingWorkpiecePathExecutor`

```python
class WeldingWorkpiecePathExecutor(IWorkpiecePathExecutor):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, robot_service) -> None
```

```python
def get_supported_execution_modes(self) -> tuple[str, ...]
```

```python
def get_process_actions(self) -> tuple[WorkpieceProcessAction, ...]
```

```python
def execute_process_action(self, execution_plan: WorkpieceExecutionPlan, action_id: str) -> tuple[bool, str]
```

```python
def get_projected_pivot_paths(self, execution_plan: WorkpieceExecutionPlan) -> tuple[list[list[list[float]]], list[float] | None]
```

```python
def get_pivot_motion_snapshots(self, execution_plan: WorkpieceExecutionPlan)
```

```python
def execute_process_paths(self, execution_plan: WorkpieceExecutionPlan, mode: str='continuous') -> tuple[bool, str]
```
