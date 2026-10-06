# Module reference: `src/robot_systems/ROBOT_SYSTEM_BLUEPRINT`

[Package guide](README.md) · [Complete source index](../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [application_wiring.py](#application_wiringpy)
- [bootstrap_provider.py](#bootstrap_providerpy)
- [component_ids.py](#component_idspy)
- [my_robot_system.py](#my_robot_systempy)
- [run_demo.py](#run_demopy)
- [service_builders.py](#service_builderspy)

## `__init__.py`

Source: [src/robot_systems/ROBOT_SYSTEM_BLUEPRINT/__init__.py](../../../src/robot_systems/ROBOT_SYSTEM_BLUEPRINT/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.robot_systems.ROBOT_SYSTEM_BLUEPRINT.my_robot_system`.

Package-level import/export surface:

```python
from src.robot_systems.ROBOT_SYSTEM_BLUEPRINT.my_robot_system import MyRobotSystem
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['MyRobotSystem']
```

## `application_wiring.py`

Source: [src/robot_systems/ROBOT_SYSTEM_BLUEPRINT/application_wiring.py](../../../src/robot_systems/ROBOT_SYSTEM_BLUEPRINT/application_wiring.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.applications.base.robot_jog_service_builder`, `src.applications.base.widget_application`, `src.applications.calibration_settings`, `src.applications.camera_settings.camera_settings_factory`, `src.applications.camera_settings.service.camera_settings_application_service`, `src.applications.robot_settings.robot_settings_factory`, `src.applications.robot_settings.service.robot_settings_application_service`, `src.applications.tool_settings`, `src.applications.user_management.domain.csv_user_repository`, `src.applications.user_management.service.user_management_application_service`, `src.applications.user_management.user_management_factory`, `src.applications.work_area_settings.service.work_area_settings_application_service`, `src.applications.work_area_settings.work_area_settings_factory`, `src.engine.auth.authorization_service`, `src.engine.auth.json_permissions_repository`, `src.engine.common_service_ids`, `src.engine.common_settings_ids`, `src.robot_systems.ROBOT_SYSTEM_BLUEPRINT.applications.dashboard`, `src.robot_systems.ROBOT_SYSTEM_BLUEPRINT.component_ids`, `src.robot_systems.ROBOT_SYSTEM_BLUEPRINT.domain.users`, `src.robot_systems.ROBOT_SYSTEM_BLUEPRINT.targeting.settings_adapter`.

### `_build_dashboard_application`

```python
def _build_dashboard_application(robot_system)
```

### `_build_user_management_application`

```python
def _build_user_management_application(robot_system)
```

### `_build_robot_settings_application`

```python
def _build_robot_settings_application(robot_system)
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

### `_build_tool_settings_application`

```python
def _build_tool_settings_application(robot_system)
```

## `bootstrap_provider.py`

Source: [src/robot_systems/ROBOT_SYSTEM_BLUEPRINT/bootstrap_provider.py](../../../src/robot_systems/ROBOT_SYSTEM_BLUEPRINT/bootstrap_provider.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.applications.login.login_application_service`, `src.applications.login.login_factory`, `src.applications.user_management.domain.auth_user_repository_adapter`, `src.applications.user_management.domain.csv_user_repository`, `src.engine.auth.authentication_service`, `src.engine.auth.authorization_service`, `src.engine.auth.json_permissions_repository`, `src.engine.common_service_ids`, `src.engine.robot.drivers.fairino.test_robot`, `src.robot_systems.ROBOT_SYSTEM_BLUEPRINT.domain.users`, `src.robot_systems.ROBOT_SYSTEM_BLUEPRINT.my_robot_system`, `src.robot_systems.robot_system_bootstrap_provider`.

### `MyRobotSystemBootstrapProvider`

```python
class MyRobotSystemBootstrapProvider(RobotSystemBootstrapProvider):
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

Source: [src/robot_systems/ROBOT_SYSTEM_BLUEPRINT/component_ids.py](../../../src/robot_systems/ROBOT_SYSTEM_BLUEPRINT/component_ids.py).

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
```

## `my_robot_system.py`

Source: [src/robot_systems/ROBOT_SYSTEM_BLUEPRINT/my_robot_system.py](../../../src/robot_systems/ROBOT_SYSTEM_BLUEPRINT/my_robot_system.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.engine.common_service_ids`, `src.engine.common_settings_ids`, `src.engine.robot.configuration`, `src.engine.robot.drivers.fairino.test_robot`, `src.engine.robot.features.navigation_service`, `src.engine.robot.interfaces.i_robot_service`, `src.engine.robot.interfaces.i_tool_service`, `src.engine.robot.targeting`, `src.engine.vision.calibration_vision_settings`, `src.engine.vision.camera_settings_serializer`, `src.engine.vision.i_vision_service`, `src.engine.work_areas`, `src.robot_systems.ROBOT_SYSTEM_BLUEPRINT`, `src.robot_systems.ROBOT_SYSTEM_BLUEPRINT.applications.dashboard.service.demo_my_dashboard_service`, `src.robot_systems.ROBOT_SYSTEM_BLUEPRINT.processes`, `src.robot_systems.ROBOT_SYSTEM_BLUEPRINT.targeting.provider`, `src.robot_systems.base_robot_system`, `src.shared_contracts.declarations`.

### `MyRobotSystem`

```python
class MyRobotSystem(BaseRobotSystem):
```

Runnable minimal demo robot system blueprint.

Declared fields/defaults:

```python
tools = [ToolDefinition(id=1, name='Single Gripper'), ToolDefinition(id=4, name='Double Gripper')]
tool_slots = [ToolSlotDefinition(id=10, tool_id=1, pickup_movement_group_id='SLOT 10 PICKUP', dropoff_movement_group_id='SLOT 10 DROPOFF'), ToolSlotDefinition(id=11, tool_id=4, pickup_movement_group_id='SLOT 11 PICKUP', dropoff_movement_group_id='SLOT 11 DROPOFF')]
movement_groups = [MovementGroupDefinition(id='LOGIN', label='Login', group_type=MovementGroupType.SINGLE_POSITION, has_trajectory_execution=True), MovementGroupDefinition(id='HOME', label='Home', group_type=MovementGroupType.SINGLE_POSITION, has_trajectory_execution=True), MovementGroupDefinition(id='CALIBRATION', label='Calibration', group_type=MovementGroupType.SINGLE_POSITION, has_trajectory_execution=True), MovementGroupDefinition(id='JOG', label='Jog', group_type=MovementGroupType.VELOCITY_ONLY), MovementGroupDefinition(id='SLOT 10 PICKUP', label='Slot 10 Pickup', group_type=MovementGroupType.MULTI_POSITION, has_trajectory_execution=True), MovementGroupDefinition(id='SLOT 10 DROPOFF', label='Slot 10 Dropoff', group_type=MovementGroupType.MULTI_POSITION, has_trajectory_execution=True), MovementGroupDefinition(id='SLOT 11 PICKUP', label='Slot 11 Pickup', group_type=MovementGroupType.MULTI_POSITION, has_trajectory_execution=True), MovementGroupDefinition(id='SLOT 11 DROPOFF', label='Slot 11 Dropoff', group_type=MovementGroupType.MULTI_POSITION, has_trajectory_execution=True)]
target_points = [RemoteTcpDefinition(name='camera', display_name='camera')]
target_frames = [TargetFrameDefinition(name='calibration', work_area_id='default', use_height_correction=True)]
work_areas = [WorkAreaDefinition(id='default', label='Default', color='#00CCFF', threshold_profile='default', supports_detection_roi=True, supports_brightness_roi=True, supports_height_mapping=True)]
work_area_observers = [WorkAreaObserverBinding(area_id='default', movement_group_id='CALIBRATION')]
default_active_work_area_id = 'default'
role_policy = RolePolicy(role_values=['Admin'], admin_role_value='Admin', default_permission_role_values=['Admin'], protected_app_role_values={'user_management': ['Admin']})
shell = ShellSetup(folders=[FolderSpec(folder_id=1, name='PRODUCTION', display_name='Production'), FolderSpec(folder_id=2, name='SERVICE', display_name='Service'), FolderSpec(folder_id=3, name='ADMIN', display_name='Administration')], applications=[ApplicationSpec(name='MyDashboard', folder_id=1, icon='fa5s.tachometer-alt', factory=application_wiring._build_dashboard_application), ApplicationSpec(name='WorkAreaSettings', folder_id=2, icon='fa5s-vector-square', factory=application_wiring._build_work_area_settings_application), ApplicationSpec(name='CameraSettings', folder_id=2, icon='fa5s.camera', factory=application_wiring._build_camera_settings_application), ApplicationSpec(name='CalibrationSettings', folder_id=2, icon='fa5s.sliders-h', factory=application_wiring._build_calibration_settings_application), ApplicationSpec(name='RobotSettings', folder_id=2, icon='mdi.robot-industrial', factory=application_wiring._build_robot_settings_application), ApplicationSpec(name='ToolSettings', folder_id=2, icon='fa5s.tools', factory=application_wiring._build_tool_settings_application), ApplicationSpec(name='UserManagement', folder_id=3, icon='fa5s.users-cog', factory=application_wiring._build_user_management_application)])
metadata = SystemMetadata(name='MyRobotSystem', version='1.0.0', description='TODO: Describe the robot system purpose.', author='Platform Team', settings_root='storage/settings')
settings_specs = [SettingsSpec(CommonSettingsID.ROBOT_CONFIG, RobotSettingsSerializer(), 'robot/config.json'), SettingsSpec(CommonSettingsID.MOVEMENT_GROUPS, MovementGroupSettingsSerializer(), 'robot/movement_groups.json'), SettingsSpec(CommonSettingsID.ROBOT_CALIBRATION, RobotCalibrationSettingsSerializer(), 'robot/calibration.json'), SettingsSpec(CommonSettingsID.CALIBRATION_VISION_SETTINGS, CalibrationVisionSettingsSerializer(), 'vision/calibration_settings.json'), SettingsSpec(CommonSettingsID.VISION_CAMERA_SETTINGS, CameraSettingsSerializer(), 'vision/camera_settings.json'), SettingsSpec(CommonSettingsID.WORK_AREA_SETTINGS, WorkAreaSettingsSerializer(), 'vision/work_areas.json'), SettingsSpec(CommonSettingsID.TOOL_CHANGER_CONFIG, ToolChangerSettingsSerializer(default_tools=tools, default_slots=tool_slots), 'tools/tool_changer.json'), SettingsSpec(CommonSettingsID.TARGETING, TargetingSettingsSerializer(), 'targeting/definitions.json')]
services = [ServiceSpec(CommonServiceID.ROBOT, IRobotService, required=True, description='Shared robot runtime service'), ServiceSpec(CommonServiceID.NAVIGATION, NavigationService, required=True, description='Shared named-position navigation service'), ServiceSpec(CommonServiceID.WORK_AREAS, IWorkAreaService, required=True, description='Shared work-area storage and active-area context'), ServiceSpec(CommonServiceID.VISION, IVisionService, required=False, description='Shared vision pipeline service'), ServiceSpec(CommonServiceID.TOOLS, IToolService, required=False, description='Shared tool changer runtime service')]
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def on_start(self) -> None
```

```python
def on_stop(self) -> None
```

```python
@staticmethod
def build_demo_robot()
```

## `run_demo.py`

Source: [src/robot_systems/ROBOT_SYSTEM_BLUEPRINT/run_demo.py](../../../src/robot_systems/ROBOT_SYSTEM_BLUEPRINT/run_demo.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtWidgets`, `__future__`, `logging`, `pathlib`, `pl_gui.shell.AppShell`, `src.bootstrap.application_loader`, `src.bootstrap.build_engine`, `src.bootstrap.logging_config`, `src.bootstrap.shell_configurator`, `src.engine.auth.user_session`, `src.engine.localization.localization_service`, `src.robot_systems.ROBOT_SYSTEM_BLUEPRINT.bootstrap_provider`, `src.robot_systems.system_builder`, `sys`.

### `run_demo`

```python
def run_demo() -> None
```

### `_load_apps_into_shell`

```python
def _load_apps_into_shell(shell, session, robot_system, ctx, provider) -> None
```

### `_build_localization_service`

```python
def _build_localization_service(robot_system, messaging_service) -> LocalizationService
```

## `service_builders.py`

Source: [src/robot_systems/ROBOT_SYSTEM_BLUEPRINT/service_builders.py](../../../src/robot_systems/ROBOT_SYSTEM_BLUEPRINT/service_builders.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.engine.robot.calibration.service_builders`, `src.engine.robot.height_measuring.service_builders`, `src.robot_systems.default_service_builders`.

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.
