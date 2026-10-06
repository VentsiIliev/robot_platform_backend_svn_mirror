# Module reference: `src/robot_systems/glue/applications/glue_settings/service`

[Package guide](README.md) · [Complete source index](../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [glue_settings_application_service.py](#glue_settings_application_servicepy)
- [i_glue_settings_service.py](#i_glue_settings_servicepy)
- [stub_glue_settings_service.py](#stub_glue_settings_servicepy)

## `__init__.py`

Source: [src/robot_systems/glue/applications/glue_settings/service/__init__.py](../../../../../../src/robot_systems/glue/applications/glue_settings/service/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `glue_settings_application_service.py`

Source: [src/robot_systems/glue/applications/glue_settings/service/glue_settings_application_service.py](../../../../../../src/robot_systems/glue/applications/glue_settings/service/glue_settings_application_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.repositories.interfaces.i_settings_service`, `src.robot_systems.glue.applications.glue_settings`, `src.robot_systems.glue.component_ids`, `src.robot_systems.glue.settings.glue`, `src.robot_systems.glue.settings.glue_types`, `typing`.

### `GlueSettingsApplicationService`

```python
class GlueSettingsApplicationService(IGlueSettingsService):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, settings_service: ISettingsService)
```

```python
def load_settings(self) -> GlueSettings
```

```python
def save_settings(self, settings: GlueSettings) -> None
```

```python
def load_glue_types(self) -> List[Glue]
```

```python
def add_glue_type(self, name: str, description: str) -> Glue
```

```python
def update_glue_type(self, id_: str, name: str, description: str) -> Glue
```

```python
def remove_glue_type(self, id_: str) -> None
```

## `i_glue_settings_service.py`

Source: [src/robot_systems/glue/applications/glue_settings/service/i_glue_settings_service.py](../../../../../../src/robot_systems/glue/applications/glue_settings/service/i_glue_settings_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `abc`, `src.robot_systems.glue.settings.glue`, `src.robot_systems.glue.settings.glue_types`, `typing`.

### `IGlueSettingsService`

```python
class IGlueSettingsService(ABC):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def load_settings(self) -> GlueSettings
```

```python
@abstractmethod
def save_settings(self, settings: GlueSettings) -> None
```

```python
@abstractmethod
def load_glue_types(self) -> List[Glue]
```

```python
@abstractmethod
def add_glue_type(self, name: str, description: str) -> Glue
```

```python
@abstractmethod
def update_glue_type(self, id_: str, name: str, description: str) -> Glue
```

```python
@abstractmethod
def remove_glue_type(self, id_: str) -> None
```

## `stub_glue_settings_service.py`

Source: [src/robot_systems/glue/applications/glue_settings/service/stub_glue_settings_service.py](../../../../../../src/robot_systems/glue/applications/glue_settings/service/stub_glue_settings_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.robot_systems.glue.applications.glue_settings.service.i_glue_settings_service`, `src.robot_systems.glue.settings.glue`, `src.robot_systems.glue.settings.glue_types`, `typing`.

### `StubGlueSettingsService`

```python
class StubGlueSettingsService(IGlueSettingsService):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self)
```

```python
def load_settings(self) -> GlueSettings
```

```python
def save_settings(self, settings: GlueSettings) -> None
```

```python
def load_glue_types(self) -> List[Glue]
```

```python
def add_glue_type(self, name: str, description: str) -> Glue
```

```python
def update_glue_type(self, id_: str, name: str, description: str) -> Glue
```

```python
def remove_glue_type(self, id_: str) -> None
```
