# Module reference: `src/robot_systems/glue/applications/glue_process_driver/model`

[Package guide](README.md) · [Complete source index](../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [glue_process_driver_model.py](#glue_process_driver_modelpy)

## `__init__.py`

Source: [src/robot_systems/glue/applications/glue_process_driver/model/__init__.py](../../../../../../src/robot_systems/glue/applications/glue_process_driver/model/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.robot_systems.glue.applications.glue_process_driver.model.glue_process_driver_model`.

Package-level import/export surface:

```python
from src.robot_systems.glue.applications.glue_process_driver.model.glue_process_driver_model import GlueProcessDriverModel
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['GlueProcessDriverModel']
```

## `glue_process_driver_model.py`

Source: [src/robot_systems/glue/applications/glue_process_driver/model/glue_process_driver_model.py](../../../../../../src/robot_systems/glue/applications/glue_process_driver/model/glue_process_driver_model.py).

Imports (including optional/function-local imports; not a startup dependency list): `logging`, `src.applications.base.i_application_model`, `src.robot_systems.glue.applications.glue_process_driver.service.i_glue_process_driver_service`.

### `GlueProcessDriverModel`

```python
class GlueProcessDriverModel(IApplicationModel):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, service: IGlueProcessDriverService)
```

```python
def load(self)
```

```python
def save(self, *args, **kwargs) -> None
```

```python
def capture_and_match(self) -> dict
```

```python
def get_latest_matched_workpieces(self) -> list
```

```python
def get_match_summary(self)
```

```python
def build_job(self, selected_indexes: list[int] | None=None)
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
def refresh_process_snapshot(self)
```

```python
def load_job(self, spray_on: bool) -> None
```

```python
def set_manual_mode(self, enabled: bool) -> None
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
