# Module reference: `src/robot_systems/twin_robot`

[Package guide](README.md) · [Complete source index](../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [application_wiring.py](#application_wiringpy)
- [bootstrap_provider.py](#bootstrap_providerpy)
- [twin_robot_system.py](#twin_robot_systempy)

## `__init__.py`

Source: [src/robot_systems/twin_robot/__init__.py](../../../src/robot_systems/twin_robot/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.robot_systems.twin_robot.twin_robot_system`.

Package-level import/export surface:

```python
from src.robot_systems.twin_robot.twin_robot_system import TwinRobotSystem
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['TwinRobotSystem']
```

## `application_wiring.py`

Source: [src/robot_systems/twin_robot/application_wiring.py](../../../src/robot_systems/twin_robot/application_wiring.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.applications.base.widget_application`, `src.applications.network_settings.build_application`, `src.applications.software_update.build_application`, `src.robot_systems.twin_robot.applications.choreography_setup`, `src.robot_systems.twin_robot.applications.dashboard`.

### `_build_dashboard_application`

```python
def _build_dashboard_application(robot_system)
```

### `_build_choreography_setup_application`

```python
def _build_choreography_setup_application(robot_system)
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

Source: [src/robot_systems/twin_robot/bootstrap_provider.py](../../../src/robot_systems/twin_robot/bootstrap_provider.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.applications.login.login_application_service`, `src.applications.login.login_factory`, `src.applications.user_management.domain.auth_user_repository_adapter`, `src.applications.user_management.domain.csv_user_repository`, `src.engine.auth.authentication_service`, `src.engine.auth.authorization_service`, `src.engine.auth.json_permissions_repository`, `src.engine.common_service_ids`, `src.engine.robot.drivers.ros2_robot`, `src.robot_systems.robot_system_bootstrap_provider`, `src.robot_systems.twin_robot.domain.users`, `src.robot_systems.twin_robot.twin_robot_system`.

### `TwinBootstrapProvider`

```python
class TwinBootstrapProvider(RobotSystemBootstrapProvider):
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

## `twin_robot_system.py`

Source: [src/robot_systems/twin_robot/twin_robot_system.py](../../../src/robot_systems/twin_robot/twin_robot_system.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `os`, `src.robot_systems.base_robot_system`, `src.robot_systems.twin_robot`, `src.robot_systems.twin_robot.applications.choreography_setup.service.choreography_setup_service`, `src.robot_systems.twin_robot.applications.dashboard.service.twin_dashboard_service`, `src.robot_systems.twin_robot.storage`, `src.shared_contracts.declarations`.

### `TwinRobotSystem`

```python
class TwinRobotSystem(BaseRobotSystem):
```

Platform composition for synchronized two-robot choreography. Concrete twin applications live under this robot-system package. The ROS transport is injected through ``set_twin_runtime`` so the platform remains decoupled from the motion-stack implementation.

Declared fields/defaults:

```python
services = []
settings_specs = []
movement_groups = []
work_areas = []
role_policy = RolePolicy(role_values=['Admin', 'Operator', 'Viewer', 'Developer'], admin_role_value='Admin', default_permission_role_values=['Admin'], protected_app_role_values={'softwareupdate': ['Admin']})
shell = ShellSetup(folders=[FolderSpec(folder_id=1, name='PRODUCTION', display_name='Production'), FolderSpec(folder_id=2, name='SETUP', display_name='Setup'), FolderSpec(folder_id=3, name='ADMIN', display_name='Administration')], applications=[ApplicationSpec(name='SoftwareUpdate', folder_id=3, icon='fa5s.download', factory=application_wiring._build_software_update_application), ApplicationSpec(name='TwinDashboard', folder_id=1, icon='fa5s.play-circle', factory=application_wiring._build_dashboard_application), ApplicationSpec(name='ChoreographySetup', folder_id=2, icon='fa5s.project-diagram', factory=application_wiring._build_choreography_setup_application), ApplicationSpec(name='NetworkSettings', folder_id=2, icon='fa5s.wifi', factory=application_wiring._build_network_settings_application)])
metadata = SystemMetadata(name='TwinRobotSystem', version='0.1.0', description='Synchronized twin-robot choreography system', author='Platform Team', settings_root=os.path.join('storage', 'settings'))
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self) -> None
```

```python
def set_twin_runtime(self, runtime) -> None
```

Attach the transport/runtime adapter used by both twin applications.

```python
def on_start(self) -> None
```

```python
def on_stop(self) -> None
```
