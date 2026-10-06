# Module reference: `src/engine/repositories/interfaces`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [i_settings_service.py](#i_settings_servicepy)
- [settings_repository.py](#settings_repositorypy)
- [settings_serializer.py](#settings_serializerpy)

## `__init__.py`

Source: [src/engine/repositories/interfaces/__init__.py](../../../../src/engine/repositories/interfaces/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `.i_settings_service`, `.settings_repository`, `.settings_serializer`.

Package-level import/export surface:

```python
from .settings_repository import ISettingsRepository, SettingsRepositoryError, SettingsLoadError, SettingsSaveError
from .settings_serializer import ISettingsSerializer
from .i_settings_service import ISettingsService
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['ISettingsRepository', 'ISettingsSerializer', 'SettingsRepositoryError', 'SettingsLoadError', 'SettingsSaveError', 'ISettingsService']
```

## `i_settings_service.py`

Source: [src/engine/repositories/interfaces/i_settings_service.py](../../../../src/engine/repositories/interfaces/i_settings_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `.settings_repository`, `abc`, `enum`, `typing`.

### `ISettingsService`

```python
class ISettingsService(ABC):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def get(self, name: Enum) -> Any
```

```python
@abstractmethod
def get_repo(self, name: Enum) -> ISettingsRepository
```

```python
@abstractmethod
def reload(self, name: Enum) -> Any
```

```python
@abstractmethod
def save(self, name: Enum, settings: Any) -> None
```

## `settings_repository.py`

Source: [src/engine/repositories/interfaces/settings_repository.py](../../../../src/engine/repositories/interfaces/settings_repository.py).

Imports (including optional/function-local imports; not a startup dependency list): `abc`, `typing`.

Module declarations (expressions are shown without evaluating them):

```python
T = TypeVar('T')
```

### `ISettingsRepository`

```python
class ISettingsRepository(ABC, Generic[T]):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, file_path: Optional[str]=None)
```

```python
@abstractmethod
def load(self) -> T
```

```python
@abstractmethod
def save(self, settings: T) -> None
```

```python
@abstractmethod
def exists(self) -> bool
```

### `SettingsRepositoryError`

```python
class SettingsRepositoryError(Exception):
```

### `SettingsLoadError`

```python
class SettingsLoadError(SettingsRepositoryError):
```

### `SettingsSaveError`

```python
class SettingsSaveError(SettingsRepositoryError):
```

## `settings_serializer.py`

Source: [src/engine/repositories/interfaces/settings_serializer.py](../../../../src/engine/repositories/interfaces/settings_serializer.py).

Imports (including optional/function-local imports; not a startup dependency list): `abc`, `typing`.

Module declarations (expressions are shown without evaluating them):

```python
T = TypeVar('T')
```

### `ISettingsSerializer`

```python
class ISettingsSerializer(ABC, Generic[T]):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def to_dict(self, settings: T) -> Dict[str, Any]
```

```python
@abstractmethod
def from_dict(self, data: Dict[str, Any]) -> T
```

```python
@abstractmethod
def get_default(self) -> T
```

```python
@property
@abstractmethod
def settings_type(self) -> str
```
