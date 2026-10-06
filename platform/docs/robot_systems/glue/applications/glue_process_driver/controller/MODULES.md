# Module reference: `src/robot_systems/glue/applications/glue_process_driver/controller`

[Package guide](README.md) · [Complete source index](../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [glue_process_driver_controller.py](#glue_process_driver_controllerpy)

## `__init__.py`

Source: [src/robot_systems/glue/applications/glue_process_driver/controller/__init__.py](../../../../../../src/robot_systems/glue/applications/glue_process_driver/controller/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.robot_systems.glue.applications.glue_process_driver.controller.glue_process_driver_controller`.

Package-level import/export surface:

```python
from src.robot_systems.glue.applications.glue_process_driver.controller.glue_process_driver_controller import GlueProcessDriverController
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['GlueProcessDriverController']
```

## `glue_process_driver_controller.py`

Source: [src/robot_systems/glue/applications/glue_process_driver/controller/glue_process_driver_controller.py](../../../../../../src/robot_systems/glue/applications/glue_process_driver/controller/glue_process_driver_controller.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `logging`, `src.applications.base.i_application_controller`, `src.engine.core.i_messaging_service`, `src.robot_systems.glue.applications.glue_process_driver.model.glue_process_driver_model`, `src.robot_systems.glue.applications.glue_process_driver.view.glue_process_driver_view`, `src.robot_systems.glue.component_ids`, `src.shared_contracts.events.glue_process_events`, `src.shared_contracts.events.process_events`.

### `_DriverBridge`

```python
class _DriverBridge(QObject):
```

Declared fields/defaults:

```python
process_snapshot_updated = pyqtSignal(object)
```

### `GlueProcessDriverController`

```python
class GlueProcessDriverController(IApplicationController):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, model: GlueProcessDriverModel, view: GlueProcessDriverView, broker: IMessagingService | None=None)
```

```python
def load(self) -> None
```

```python
def stop(self) -> None
```
