# Module reference: `src/robot_systems/twin_robot/applications/choreography_setup/service`

[Package guide](README.md) · [Complete source index](../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [choreography_setup_service.py](#choreography_setup_servicepy)
- [i_choreography_setup_service.py](#i_choreography_setup_servicepy)

## `__init__.py`

Source: [src/robot_systems/twin_robot/applications/choreography_setup/service/__init__.py](../../../../../../src/robot_systems/twin_robot/applications/choreography_setup/service/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.robot_systems.twin_robot.applications.choreography_setup.service.choreography_setup_service`, `src.robot_systems.twin_robot.applications.choreography_setup.service.i_choreography_setup_service`.

Package-level import/export surface:

```python
from src.robot_systems.twin_robot.applications.choreography_setup.service.choreography_setup_service import ChoreographySetupService
from src.robot_systems.twin_robot.applications.choreography_setup.service.i_choreography_setup_service import IChoreographySetupService
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['ChoreographySetupService', 'IChoreographySetupService']
```

## `choreography_setup_service.py`

Source: [src/robot_systems/twin_robot/applications/choreography_setup/service/choreography_setup_service.py](../../../../../../src/robot_systems/twin_robot/applications/choreography_setup/service/choreography_setup_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.robot_systems.twin_robot.applications.choreography_setup.service.i_choreography_setup_service`, `src.robot_systems.twin_robot.domain`, `src.robot_systems.twin_robot.storage`, `typing`.

### `ChoreographySetupService`

```python
class ChoreographySetupService(IChoreographySetupService):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, repository: ChoreographyRepository, runtime: Any | None=None)
```

```python
def set_runtime(self, runtime: Any | None) -> None
```

```python
def list_choreographies(self) -> List[Dict[str, Any]]
```

```python
def load_choreography(self, choreography_id: str) -> Dict[str, Any]
```

```python
def new_choreography(self, choreography_id: str, name: str) -> Dict[str, Any]
```

```python
def save_choreography(self, payload: Dict[str, Any]) -> Dict[str, Any]
```

```python
def capture_robot(self, robot_name: str) -> Dict[str, Any]
```

```python
def robot_state(self, robot_name: str) -> Dict[str, Any]
```

```python
def jog(self, robot_name: str, command: str, axis: str, direction: str, step: float) -> int
```

```python
def stop_servo_jog(self, robot_name: str) -> int
```

```python
def joint_jog(self, robot_name: str, command: str, joint: str, direction: str, step: float) -> int
```

## `i_choreography_setup_service.py`

Source: [src/robot_systems/twin_robot/applications/choreography_setup/service/i_choreography_setup_service.py](../../../../../../src/robot_systems/twin_robot/applications/choreography_setup/service/i_choreography_setup_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `abc`, `typing`.

### `IChoreographySetupService`

```python
class IChoreographySetupService(ABC):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def list_choreographies(self) -> List[Dict[str, Any]]
```

```python
@abstractmethod
def load_choreography(self, choreography_id: str) -> Dict[str, Any]
```

```python
@abstractmethod
def new_choreography(self, choreography_id: str, name: str) -> Dict[str, Any]
```

```python
@abstractmethod
def save_choreography(self, payload: Dict[str, Any]) -> Dict[str, Any]
```

```python
@abstractmethod
def capture_robot(self, robot_name: str) -> Dict[str, Any]
```

```python
@abstractmethod
def robot_state(self, robot_name: str) -> Dict[str, Any]
```

```python
@abstractmethod
def jog(self, robot_name: str, command: str, axis: str, direction: str, step: float) -> int
```

```python
@abstractmethod
def stop_servo_jog(self, robot_name: str) -> int
```

```python
@abstractmethod
def joint_jog(self, robot_name: str, command: str, joint: str, direction: str, step: float) -> int
```
