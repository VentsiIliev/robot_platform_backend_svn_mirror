# Module reference: `src/engine/repositories/json`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [base_json_settings_repository.py](#base_json_settings_repositorypy)

## `__init__.py`

Source: [src/engine/repositories/json/__init__.py](../../../../src/engine/repositories/json/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `.base_json_settings_repository`.

Package-level import/export surface:

```python
from .base_json_settings_repository import BaseJsonSettingsRepository
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['BaseJsonSettingsRepository']
```

## `base_json_settings_repository.py`

Source: [src/engine/repositories/json/base_json_settings_repository.py](../../../../src/engine/repositories/json/base_json_settings_repository.py).

Imports (including optional/function-local imports; not a startup dependency list): `..interfaces.settings_repository`, `..interfaces.settings_serializer`, `json`, `logging`, `os`, `typing`.

Module declarations (expressions are shown without evaluating them):

```python
T = TypeVar('T')
```

### `BaseJsonSettingsRepository`

```python
class BaseJsonSettingsRepository(ISettingsRepository[T], Generic[T]):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, serializer: ISettingsSerializer[T], file_path: Optional[str]=None)
```

```python
def load(self) -> T
```

```python
def save(self, settings: T) -> None
```

```python
def exists(self) -> bool
```
