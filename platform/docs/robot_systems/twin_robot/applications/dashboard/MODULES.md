# Module reference: `src/robot_systems/twin_robot/applications/dashboard`

[Package guide](README.md) · [Complete source index](../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [twin_dashboard_factory.py](#twin_dashboard_factorypy)

## `__init__.py`

Source: [src/robot_systems/twin_robot/applications/dashboard/__init__.py](../../../../../src/robot_systems/twin_robot/applications/dashboard/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.robot_systems.twin_robot.applications.dashboard.twin_dashboard_factory`.

Package-level import/export surface:

```python
from src.robot_systems.twin_robot.applications.dashboard.twin_dashboard_factory import TwinDashboardFactory
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['TwinDashboardFactory']
```

## `twin_dashboard_factory.py`

Source: [src/robot_systems/twin_robot/applications/dashboard/twin_dashboard_factory.py](../../../../../src/robot_systems/twin_robot/applications/dashboard/twin_dashboard_factory.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.applications.base.application_factory`, `src.applications.base.i_application_controller`, `src.applications.base.i_application_model`, `src.applications.base.i_application_view`, `src.robot_systems.twin_robot.applications.dashboard.controller.twin_dashboard_controller`, `src.robot_systems.twin_robot.applications.dashboard.model.twin_dashboard_model`, `src.robot_systems.twin_robot.applications.dashboard.service.i_twin_dashboard_service`, `src.robot_systems.twin_robot.applications.dashboard.view.twin_dashboard_view`.

### `TwinDashboardFactory`

```python
class TwinDashboardFactory(ApplicationFactory):
```
