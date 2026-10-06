# Module reference: `src/applications/work_area_settings/model`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [work_area_settings_model.py](#work_area_settings_modelpy)

## `__init__.py`

Source: [src/applications/work_area_settings/model/__init__.py](../../../../src/applications/work_area_settings/model/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.work_area_settings.model.work_area_settings_model`.

Package-level import/export surface:

```python
from src.applications.work_area_settings.model.work_area_settings_model import WorkAreaSettingsModel
```

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `work_area_settings_model.py`

Source: [src/applications/work_area_settings/model/work_area_settings_model.py](../../../../src/applications/work_area_settings/model/work_area_settings_model.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.applications.base.i_application_model`, `src.applications.work_area_settings.service.i_work_area_settings_service`.

### `WorkAreaSettingsModel`

```python
class WorkAreaSettingsModel(IApplicationModel):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, service: IWorkAreaSettingsService)
```

```python
def load(self) -> str
```

```python
def save(self, area_id: str) -> None
```

```python
def get_active_work_area_id(self) -> str
```

```python
def set_active_work_area_id(self, area_id: str) -> None
```

```python
def save_work_area(self, area_key: str, normalized_points: list) -> tuple[bool, str]
```

```python
def get_work_area(self, area_key: str) -> list[tuple[float, float]]
```
