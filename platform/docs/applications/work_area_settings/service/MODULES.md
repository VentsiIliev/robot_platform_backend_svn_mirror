# Module reference: `src/applications/work_area_settings/service`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [i_work_area_settings_service.py](#i_work_area_settings_servicepy)
- [stub_work_area_settings_service.py](#stub_work_area_settings_servicepy)
- [work_area_settings_application_service.py](#work_area_settings_application_servicepy)

## `__init__.py`

Source: [src/applications/work_area_settings/service/__init__.py](../../../../src/applications/work_area_settings/service/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.work_area_settings.service.i_work_area_settings_service`, `src.applications.work_area_settings.service.stub_work_area_settings_service`, `src.applications.work_area_settings.service.work_area_settings_application_service`.

Package-level import/export surface:

```python
from src.applications.work_area_settings.service.i_work_area_settings_service import IWorkAreaSettingsService
from src.applications.work_area_settings.service.stub_work_area_settings_service import StubWorkAreaSettingsService
from src.applications.work_area_settings.service.work_area_settings_application_service import WorkAreaSettingsApplicationService
```

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `i_work_area_settings_service.py`

Source: [src/applications/work_area_settings/service/i_work_area_settings_service.py](../../../../src/applications/work_area_settings/service/i_work_area_settings_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `abc`, `typing`.

### `IWorkAreaSettingsService`

```python
class IWorkAreaSettingsService(ABC):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def get_active_work_area_id(self) -> str
```

```python
@abstractmethod
def set_active_work_area_id(self, area_id: str) -> None
```

```python
@abstractmethod
def save_work_area(self, area_key: str, normalized_points: List[Tuple[float, float]]) -> tuple[bool, str]
```

```python
@abstractmethod
def get_work_area(self, area_key: str) -> tuple[bool, str, Optional[List[Tuple[float, float]]]]
```

## `stub_work_area_settings_service.py`

Source: [src/applications/work_area_settings/service/stub_work_area_settings_service.py](../../../../src/applications/work_area_settings/service/stub_work_area_settings_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `logging`, `src.applications.work_area_settings.service.i_work_area_settings_service`.

### `StubWorkAreaSettingsService`

```python
class StubWorkAreaSettingsService(IWorkAreaSettingsService):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self) -> None
```

```python
def get_active_work_area_id(self) -> str
```

```python
def set_active_work_area_id(self, area_id: str) -> None
```

```python
def save_work_area(self, area_key: str, normalized_points: list[tuple[float, float]]) -> tuple[bool, str]
```

```python
def get_work_area(self, area_key: str) -> tuple[bool, str, list[tuple[float, float]] | None]
```

## `work_area_settings_application_service.py`

Source: [src/applications/work_area_settings/service/work_area_settings_application_service.py](../../../../src/applications/work_area_settings/service/work_area_settings_application_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.applications.work_area_settings.service.i_work_area_settings_service`, `src.engine.vision.i_vision_service`, `src.engine.work_areas.i_work_area_service`.

### `WorkAreaSettingsApplicationService`

```python
class WorkAreaSettingsApplicationService(IWorkAreaSettingsService):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, work_area_service: IWorkAreaService, vision_service: IVisionService | None=None) -> None
```

```python
def get_active_work_area_id(self) -> str
```

```python
def set_active_work_area_id(self, area_id: str) -> None
```

```python
def save_work_area(self, area_key: str, normalized_points: list[tuple[float, float]]) -> tuple[bool, str]
```

```python
def get_work_area(self, area_key: str) -> tuple[bool, str, list[tuple[float, float]] | None]
```
