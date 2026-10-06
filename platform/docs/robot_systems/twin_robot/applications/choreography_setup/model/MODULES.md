# Module reference: `src/robot_systems/twin_robot/applications/choreography_setup/model`

[Package guide](README.md) · [Complete source index](../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [choreography_setup_model.py](#choreography_setup_modelpy)

## `__init__.py`

Source: [src/robot_systems/twin_robot/applications/choreography_setup/model/__init__.py](../../../../../../src/robot_systems/twin_robot/applications/choreography_setup/model/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.robot_systems.twin_robot.applications.choreography_setup.model.choreography_setup_model`.

Package-level import/export surface:

```python
from src.robot_systems.twin_robot.applications.choreography_setup.model.choreography_setup_model import ChoreographySetupModel
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['ChoreographySetupModel']
```

## `choreography_setup_model.py`

Source: [src/robot_systems/twin_robot/applications/choreography_setup/model/choreography_setup_model.py](../../../../../../src/robot_systems/twin_robot/applications/choreography_setup/model/choreography_setup_model.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `copy`, `src.applications.base.i_application_model`, `src.robot_systems.twin_robot.applications.choreography_setup.service.i_choreography_setup_service`, `typing`.

### `ChoreographySetupModel`

```python
class ChoreographySetupModel(IApplicationModel):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, service: IChoreographySetupService)
```

```python
def load(self) -> List[Dict[str, Any]]
```

```python
def load_choreography(self, choreography_id: str) -> Dict[str, Any]
```

```python
def new_choreography(self, choreography_id: str, name: str) -> Dict[str, Any]
```

```python
def current(self) -> Dict[str, Any]
```

```python
def apply_editor(self, *, name: str, loop_count: int, steps: List[Dict[str, Any]]) -> None
```

```python
def add_step(self) -> Dict[str, Any]
```

```python
def delete_step(self, row: int) -> Dict[str, Any]
```

```python
def capture_robot(self, row: int, robot_name: str) -> Dict[str, Any]
```

```python
def capture_both(self, row: int) -> Dict[str, Any]
```

```python
def save(self) -> Dict[str, Any]
```

```python
def robot_states(self) -> Dict[str, Dict[str, Any]]
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
