# Module reference: `src/engine/repositories`

[Package guide](README.md) · [Complete source index](../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [settings_service.py](#settings_servicepy)
- [settings_service_factory.py](#settings_service_factorypy)

## `settings_service.py`

Source: [src/engine/repositories/settings_service.py](../../../src/engine/repositories/settings_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `enum`, `logging`, `src.engine.repositories.interfaces.i_settings_service`, `src.engine.repositories.interfaces.settings_repository`, `typing`.

### `SettingsService`

```python
class SettingsService(ISettingsService):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, repos: Dict[Enum, ISettingsRepository])
```

```python
def get(self, name: Enum) -> Any
```

```python
def get_repo(self, name: Enum) -> ISettingsRepository
```

```python
def reload(self, name: Enum) -> Any
```

```python
def save(self, name: Enum, settings: Any) -> None
```

## `settings_service_factory.py`

Source: [src/engine/repositories/settings_service_factory.py](../../../src/engine/repositories/settings_service_factory.py).

Imports (including optional/function-local imports; not a startup dependency list): `inspect`, `os`, `src.engine.repositories.interfaces.i_settings_service`, `src.engine.repositories.json.base_json_settings_repository`, `src.engine.repositories.settings_service`, `src.engine.updates.paths`, `src.shared_contracts.declarations`, `typing`.

### `build_from_specs`

```python
def build_from_specs(specs: List[SettingsSpec], settings_root: str, system_class: Type) -> ISettingsService
```
