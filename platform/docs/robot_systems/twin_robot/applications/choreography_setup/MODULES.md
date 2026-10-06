# Module reference: `src/robot_systems/twin_robot/applications/choreography_setup`

[Package guide](README.md) · [Complete source index](../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [choreography_setup_factory.py](#choreography_setup_factorypy)

## `__init__.py`

Source: [src/robot_systems/twin_robot/applications/choreography_setup/__init__.py](../../../../../src/robot_systems/twin_robot/applications/choreography_setup/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.robot_systems.twin_robot.applications.choreography_setup.choreography_setup_factory`.

Package-level import/export surface:

```python
from src.robot_systems.twin_robot.applications.choreography_setup.choreography_setup_factory import ChoreographySetupFactory
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['ChoreographySetupFactory']
```

## `choreography_setup_factory.py`

Source: [src/robot_systems/twin_robot/applications/choreography_setup/choreography_setup_factory.py](../../../../../src/robot_systems/twin_robot/applications/choreography_setup/choreography_setup_factory.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.applications.base.application_factory`, `src.applications.base.i_application_controller`, `src.applications.base.i_application_model`, `src.applications.base.i_application_view`, `src.robot_systems.twin_robot.applications.choreography_setup.controller.choreography_setup_controller`, `src.robot_systems.twin_robot.applications.choreography_setup.model.choreography_setup_model`, `src.robot_systems.twin_robot.applications.choreography_setup.service.i_choreography_setup_service`, `src.robot_systems.twin_robot.applications.choreography_setup.view.choreography_setup_view`.

### `ChoreographySetupFactory`

```python
class ChoreographySetupFactory(ApplicationFactory):
```
