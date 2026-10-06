# Module reference: `src/robot_systems/glue/applications/glue_process_driver/service`

[Package guide](README.md) · [Complete source index](../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [glue_process_driver_service.py](#glue_process_driver_servicepy)
- [i_glue_process_driver_service.py](#i_glue_process_driver_servicepy)
- [stub_glue_process_driver_service.py](#stub_glue_process_driver_servicepy)

## `__init__.py`

Source: [src/robot_systems/glue/applications/glue_process_driver/service/__init__.py](../../../../../../src/robot_systems/glue/applications/glue_process_driver/service/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.robot_systems.glue.applications.glue_process_driver.service.glue_process_driver_service`, `src.robot_systems.glue.applications.glue_process_driver.service.i_glue_process_driver_service`, `src.robot_systems.glue.applications.glue_process_driver.service.stub_glue_process_driver_service`.

Package-level import/export surface:

```python
from src.robot_systems.glue.applications.glue_process_driver.service.glue_process_driver_service import GlueProcessDriverService
from src.robot_systems.glue.applications.glue_process_driver.service.i_glue_process_driver_service import IGlueProcessDriverService
from src.robot_systems.glue.applications.glue_process_driver.service.stub_glue_process_driver_service import StubGlueProcessDriverService
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['GlueProcessDriverService', 'IGlueProcessDriverService', 'StubGlueProcessDriverService']
```

## `glue_process_driver_service.py`

Source: [src/robot_systems/glue/applications/glue_process_driver/service/glue_process_driver_service.py](../../../../../../src/robot_systems/glue/applications/glue_process_driver/service/glue_process_driver_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.robot_systems.glue.applications.glue_process_driver.service.i_glue_process_driver_service`.

### `GlueProcessDriverService`

```python
class GlueProcessDriverService(IGlueProcessDriverService):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, matching_service, job_builder, glue_process, execution_service=None) -> None
```

```python
def capture_and_match(self) -> dict
```

```python
def get_latest_matched_workpieces(self) -> list
```

```python
def get_latest_match_summary(self) -> dict
```

```python
def select_matched_workpieces(self, indexes: list[int]) -> None
```

```python
def build_job_from_latest_match(self)
```

```python
def load_latest_job(self, spray_on: bool) -> None
```

```python
def prepare_and_load(self, spray_on: bool)
```

```python
def prepare_load_and_start(self, spray_on: bool)
```

```python
def get_latest_job(self)
```

```python
def get_latest_job_summary(self)
```

```python
def get_process_snapshot(self)
```

```python
def set_manual_mode(self, enabled: bool) -> None
```

```python
def is_manual_mode_enabled(self) -> bool
```

```python
def step_once(self)
```

```python
def start(self) -> None
```

```python
def pause(self) -> None
```

```python
def resume(self) -> None
```

```python
def stop(self) -> None
```

```python
def reset_errors(self) -> None
```

## `i_glue_process_driver_service.py`

Source: [src/robot_systems/glue/applications/glue_process_driver/service/i_glue_process_driver_service.py](../../../../../../src/robot_systems/glue/applications/glue_process_driver/service/i_glue_process_driver_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `abc`.

### `IGlueProcessDriverService`

```python
class IGlueProcessDriverService(ABC):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def capture_and_match(self) -> dict
```

```python
@abstractmethod
def get_latest_matched_workpieces(self) -> list
```

```python
@abstractmethod
def get_latest_match_summary(self) -> dict
```

```python
@abstractmethod
def select_matched_workpieces(self, indexes: list[int]) -> None
```

```python
@abstractmethod
def build_job_from_latest_match(self)
```

```python
@abstractmethod
def get_latest_job(self)
```

```python
@abstractmethod
def get_latest_job_summary(self)
```

```python
@abstractmethod
def load_latest_job(self, spray_on: bool) -> None
```

```python
@abstractmethod
def prepare_and_load(self, spray_on: bool)
```

```python
@abstractmethod
def prepare_load_and_start(self, spray_on: bool)
```

```python
@abstractmethod
def get_process_snapshot(self)
```

```python
@abstractmethod
def set_manual_mode(self, enabled: bool) -> None
```

```python
@abstractmethod
def is_manual_mode_enabled(self) -> bool
```

```python
@abstractmethod
def step_once(self)
```

```python
@abstractmethod
def start(self) -> None
```

```python
@abstractmethod
def pause(self) -> None
```

```python
@abstractmethod
def resume(self) -> None
```

```python
@abstractmethod
def stop(self) -> None
```

```python
@abstractmethod
def reset_errors(self) -> None
```

## `stub_glue_process_driver_service.py`

Source: [src/robot_systems/glue/applications/glue_process_driver/service/stub_glue_process_driver_service.py](../../../../../../src/robot_systems/glue/applications/glue_process_driver/service/stub_glue_process_driver_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.robot_systems.glue.applications.glue_process_driver.service.i_glue_process_driver_service`.

### `StubGlueProcessDriverService`

```python
class StubGlueProcessDriverService(IGlueProcessDriverService):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self)
```

```python
def capture_and_match(self) -> dict
```

```python
def get_latest_match_summary(self) -> dict
```

```python
def get_latest_matched_workpieces(self) -> list
```

```python
def select_matched_workpieces(self, indexes: list[int]) -> None
```

```python
def build_job_from_latest_match(self)
```

```python
def get_latest_job(self)
```

```python
def get_latest_job_summary(self)
```

```python
def load_latest_job(self, spray_on: bool) -> None
```

```python
def prepare_and_load(self, spray_on: bool)
```

```python
def prepare_load_and_start(self, spray_on: bool)
```

```python
def get_process_snapshot(self)
```

```python
def set_manual_mode(self, enabled: bool) -> None
```

```python
def is_manual_mode_enabled(self) -> bool
```

```python
def step_once(self)
```

```python
def start(self) -> None
```

```python
def pause(self) -> None
```

```python
def resume(self) -> None
```

```python
def stop(self) -> None
```

```python
def reset_errors(self) -> None
```
