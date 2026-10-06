# Module reference: `src/robot_systems/twin_robot/applications/choreography_setup/controller`

[Package guide](README.md) · [Complete source index](../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [choreography_setup_controller.py](#choreography_setup_controllerpy)

## `__init__.py`

Source: [src/robot_systems/twin_robot/applications/choreography_setup/controller/__init__.py](../../../../../../src/robot_systems/twin_robot/applications/choreography_setup/controller/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.robot_systems.twin_robot.applications.choreography_setup.controller.choreography_setup_controller`.

Package-level import/export surface:

```python
from src.robot_systems.twin_robot.applications.choreography_setup.controller.choreography_setup_controller import ChoreographySetupController
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['ChoreographySetupController']
```

## `choreography_setup_controller.py`

Source: [src/robot_systems/twin_robot/applications/choreography_setup/controller/choreography_setup_controller.py](../../../../../../src/robot_systems/twin_robot/applications/choreography_setup/controller/choreography_setup_controller.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `__future__`, `functools`, `logging`, `src.applications.base.background_worker`, `src.applications.base.i_application_controller`, `src.robot_systems.twin_robot.applications.choreography_setup.model.choreography_setup_model`, `src.robot_systems.twin_robot.applications.choreography_setup.view.choreography_setup_view`.

### `ChoreographySetupController`

```python
class ChoreographySetupController(IApplicationController, BackgroundWorker):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, model: ChoreographySetupModel, view: ChoreographySetupView)
```

```python
def load(self) -> None
```

```python
def stop(self) -> None
```
