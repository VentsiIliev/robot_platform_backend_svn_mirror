# Module reference: `src/engine/work_areas`

[Package guide](README.md) · [Complete source index](../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [i_work_area_service.py](#i_work_area_servicepy)
- [work_area_service.py](#work_area_servicepy)
- [work_area_settings.py](#work_area_settingspy)

## `__init__.py`

Source: [src/engine/work_areas/__init__.py](../../../src/engine/work_areas/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.work_areas.i_work_area_service`, `src.engine.work_areas.work_area_service`, `src.engine.work_areas.work_area_settings`, `src.shared_contracts.declarations`.

Package-level import/export surface:

```python
from src.engine.work_areas.i_work_area_service import IWorkAreaService
from src.engine.work_areas.work_area_service import WorkAreaService
from src.engine.work_areas.work_area_settings import WorkAreaConfig, WorkAreaSettings, WorkAreaSettingsSerializer
from src.shared_contracts.declarations import WorkAreaDefinition, WorkAreaObserverBinding
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['IWorkAreaService', 'WorkAreaConfig', 'WorkAreaDefinition', 'WorkAreaObserverBinding', 'WorkAreaService', 'WorkAreaSettings', 'WorkAreaSettingsSerializer']
```

## `i_work_area_service.py`

Source: [src/engine/work_areas/i_work_area_service.py](../../../src/engine/work_areas/i_work_area_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `abc`, `src.engine.work_areas.work_area_settings`, `src.shared_contracts.declarations`, `typing`.

### `IWorkAreaService`

```python
class IWorkAreaService(ABC):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def get_active_area_id(self) -> Optional[str]
```

```python
@abstractmethod
def set_active_area_id(self, area_id: str | None) -> None
```

```python
@abstractmethod
def is_active_area_verified(self) -> bool
```

```python
@abstractmethod
def mark_active_area_verified(self, area_id: str | None=None) -> None
```

```python
@abstractmethod
def get_area_config(self, area_id: str) -> WorkAreaConfig | None
```

```python
@abstractmethod
def get_area_definition(self, area_id: str) -> WorkAreaDefinition | None
```

```python
@abstractmethod
def save_work_area(self, area_key: str, normalized_points: NormalizedPolygon) -> tuple[bool, str]
```

```python
@abstractmethod
def get_work_area(self, area_key: str) -> NormalizedPolygon | None
```

```python
@abstractmethod
def get_detection_roi_pixels(self, area_id: str, width: int, height: int)
```

```python
@abstractmethod
def get_brightness_roi_pixels(self, area_id: str, width: int, height: int)
```

## `work_area_service.py`

Source: [src/engine/work_areas/work_area_service.py](../../../src/engine/work_areas/work_area_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `logging`, `numpy`, `src.engine.common_settings_ids`, `src.engine.repositories.interfaces.i_settings_service`, `src.engine.work_areas.i_work_area_service`, `src.engine.work_areas.work_area_settings`, `src.shared_contracts.declarations`, `typing`.

### `WorkAreaService`

```python
class WorkAreaService(IWorkAreaService):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, settings_service: ISettingsService, definitions: Iterable[WorkAreaDefinition]=(), default_active_area_id: str='') -> None
```

```python
def get_active_area_id(self) -> Optional[str]
```

```python
def set_active_area_id(self, area_id: str | None) -> None
```

```python
def is_active_area_verified(self) -> bool
```

```python
def mark_active_area_verified(self, area_id: str | None=None) -> None
```

```python
def get_area_config(self, area_id: str) -> WorkAreaConfig | None
```

```python
def get_area_definition(self, area_id: str) -> WorkAreaDefinition | None
```

```python
def save_work_area(self, area_key: str, normalized_points: NormalizedPolygon) -> tuple[bool, str]
```

```python
def get_work_area(self, area_key: str) -> NormalizedPolygon | None
```

```python
def get_detection_roi_pixels(self, area_id: str, width: int, height: int)
```

```python
def get_brightness_roi_pixels(self, area_id: str, width: int, height: int)
```

## `work_area_settings.py`

Source: [src/engine/work_areas/work_area_settings.py](../../../src/engine/work_areas/work_area_settings.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`, `src.engine.repositories.interfaces`, `typing`.

Module declarations (expressions are shown without evaluating them):

```python
NormalizedPolygon = List[List[float]]
```

### `WorkAreaConfig`

```python
@dataclass
class WorkAreaConfig:
```

Declared fields/defaults:

```python
detection_roi: NormalizedPolygon = field(default_factory=list)
brightness_roi: NormalizedPolygon = field(default_factory=list)
height_mapping_roi: NormalizedPolygon = field(default_factory=list)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def from_dict(cls, raw: Dict[str, Any]) -> 'WorkAreaConfig'
```

```python
def to_dict(self) -> Dict[str, Any]
```

### `WorkAreaSettings`

```python
@dataclass
class WorkAreaSettings:
```

Declared fields/defaults:

```python
areas: Dict[str, WorkAreaConfig] = field(default_factory=dict)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def from_dict(cls, raw: Dict[str, Any]) -> 'WorkAreaSettings'
```

```python
def to_dict(self) -> Dict[str, Any]
```

### `WorkAreaSettingsSerializer`

```python
class WorkAreaSettingsSerializer(ISettingsSerializer[WorkAreaSettings]):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@property
def settings_type(self) -> str
```

```python
def get_default(self) -> WorkAreaSettings
```

```python
def to_dict(self, data: WorkAreaSettings) -> Dict[str, Any]
```

```python
def from_dict(self, raw: Dict[str, Any]) -> WorkAreaSettings
```

### `_load_polygon`

```python
def _load_polygon(raw: Any) -> NormalizedPolygon
```
