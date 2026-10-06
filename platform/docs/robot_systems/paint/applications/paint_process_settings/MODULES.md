# Module reference: `src/robot_systems/paint/applications/paint_process_settings`

[Package guide](README.md) · [Complete source index](../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [example_usage.py](#example_usagepy)
- [mapper.py](#mapperpy)
- [paint_process_settings_factory.py](#paint_process_settings_factorypy)

## `__init__.py`

Source: [src/robot_systems/paint/applications/paint_process_settings/__init__.py](../../../../../src/robot_systems/paint/applications/paint_process_settings/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.robot_systems.paint.applications.paint_process_settings.paint_process_settings_factory`, `src.robot_systems.paint.applications.paint_process_settings.service.i_paint_process_settings_service`, `src.robot_systems.paint.applications.paint_process_settings.service.stub_paint_process_settings_service`.

Package-level import/export surface:

```python
from src.robot_systems.paint.applications.paint_process_settings.paint_process_settings_factory import PaintProcessSettingsFactory
from src.robot_systems.paint.applications.paint_process_settings.service.i_paint_process_settings_service import IPaintProcessSettingsService
from src.robot_systems.paint.applications.paint_process_settings.service.stub_paint_process_settings_service import StubPaintProcessSettingsService
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['IPaintProcessSettingsService', 'PaintProcessSettingsFactory', 'StubPaintProcessSettingsService']
```

## `example_usage.py`

Source: [src/robot_systems/paint/applications/paint_process_settings/example_usage.py](../../../../../src/robot_systems/paint/applications/paint_process_settings/example_usage.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtWidgets`, `pathlib`, `src.robot_systems.paint.applications.paint_process_settings.paint_process_settings_factory`, `src.robot_systems.paint.applications.paint_process_settings.service.stub_paint_process_settings_service`, `sys`.

### `run_standalone`

```python
def run_standalone() -> None
```

## `mapper.py`

Source: [src/robot_systems/paint/applications/paint_process_settings/mapper.py](../../../../../src/robot_systems/paint/applications/paint_process_settings/mapper.py).

Imports (including optional/function-local imports; not a startup dependency list): `dataclasses`, `src.robot_systems.paint.processes.paint.config`.

### `PaintProcessSettingsMapper`

```python
class PaintProcessSettingsMapper:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@staticmethod
def to_flat_dict(settings: PaintProcessConfig) -> dict
```

```python
@staticmethod
def from_flat_dict(flat: dict, base: PaintProcessConfig) -> PaintProcessConfig
```

## `paint_process_settings_factory.py`

Source: [src/robot_systems/paint/applications/paint_process_settings/paint_process_settings_factory.py](../../../../../src/robot_systems/paint/applications/paint_process_settings/paint_process_settings_factory.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.base.application_factory`, `src.robot_systems.paint.applications.paint_process_settings.controller.paint_process_settings_controller`, `src.robot_systems.paint.applications.paint_process_settings.model.paint_process_settings_model`, `src.robot_systems.paint.applications.paint_process_settings.service.i_paint_process_settings_service`, `src.robot_systems.paint.applications.paint_process_settings.view.paint_process_settings_view`.

### `PaintProcessSettingsFactory`

```python
class PaintProcessSettingsFactory(ApplicationFactory):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, dropoff_strategies: tuple[str, ...]=('movement_group', 'plate_layout'))
```

```python
def build(self, service: IPaintProcessSettingsService, messaging=None, jog_service=None)
```
