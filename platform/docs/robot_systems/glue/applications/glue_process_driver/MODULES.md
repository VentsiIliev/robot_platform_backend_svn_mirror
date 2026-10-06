# Module reference: `src/robot_systems/glue/applications/glue_process_driver`

[Package guide](README.md) · [Complete source index](../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [example_usage.py](#example_usagepy)
- [glue_process_driver_factory.py](#glue_process_driver_factorypy)

## `__init__.py`

Source: [src/robot_systems/glue/applications/glue_process_driver/__init__.py](../../../../../src/robot_systems/glue/applications/glue_process_driver/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.robot_systems.glue.applications.glue_process_driver.controller.glue_process_driver_controller`, `src.robot_systems.glue.applications.glue_process_driver.glue_process_driver_factory`, `src.robot_systems.glue.applications.glue_process_driver.model.glue_process_driver_model`, `src.robot_systems.glue.applications.glue_process_driver.service.glue_process_driver_service`, `src.robot_systems.glue.applications.glue_process_driver.service.i_glue_process_driver_service`, `src.robot_systems.glue.applications.glue_process_driver.service.stub_glue_process_driver_service`, `src.robot_systems.glue.applications.glue_process_driver.view.glue_process_driver_view`.

Package-level import/export surface:

```python
from src.robot_systems.glue.applications.glue_process_driver.service.glue_process_driver_service import GlueProcessDriverService
from src.robot_systems.glue.applications.glue_process_driver.service.i_glue_process_driver_service import IGlueProcessDriverService
from src.robot_systems.glue.applications.glue_process_driver.service.stub_glue_process_driver_service import StubGlueProcessDriverService
from src.robot_systems.glue.applications.glue_process_driver.model.glue_process_driver_model import GlueProcessDriverModel
from src.robot_systems.glue.applications.glue_process_driver.controller.glue_process_driver_controller import GlueProcessDriverController
from src.robot_systems.glue.applications.glue_process_driver.view.glue_process_driver_view import GlueProcessDriverView
from src.robot_systems.glue.applications.glue_process_driver.glue_process_driver_factory import GlueProcessDriverFactory
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['GlueProcessDriverService', 'IGlueProcessDriverService', 'StubGlueProcessDriverService', 'GlueProcessDriverModel', 'GlueProcessDriverController', 'GlueProcessDriverView', 'GlueProcessDriverFactory']
```

## `example_usage.py`

Source: [src/robot_systems/glue/applications/glue_process_driver/example_usage.py](../../../../../src/robot_systems/glue/applications/glue_process_driver/example_usage.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtWidgets`, `pathlib`, `src.engine.core.message_broker`, `src.robot_systems.glue.applications.glue_process_driver.glue_process_driver_factory`, `src.robot_systems.glue.applications.glue_process_driver.service.stub_glue_process_driver_service`, `sys`.

### `run_standalone`

```python
def run_standalone()
```

## `glue_process_driver_factory.py`

Source: [src/robot_systems/glue/applications/glue_process_driver/glue_process_driver_factory.py](../../../../../src/robot_systems/glue/applications/glue_process_driver/glue_process_driver_factory.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.base.application_factory`, `src.applications.base.i_application_controller`, `src.applications.base.i_application_model`, `src.applications.base.i_application_view`, `src.engine.core.i_messaging_service`, `src.robot_systems.glue.applications.glue_process_driver.controller.glue_process_driver_controller`, `src.robot_systems.glue.applications.glue_process_driver.model.glue_process_driver_model`, `src.robot_systems.glue.applications.glue_process_driver.service.i_glue_process_driver_service`, `src.robot_systems.glue.applications.glue_process_driver.view.glue_process_driver_view`.

### `GlueProcessDriverFactory`

```python
class GlueProcessDriverFactory(ApplicationFactory):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, broker: IMessagingService | None=None)
```
