# Module reference: `src/robot_systems/glue/applications/glue_settings/model`

[Package guide](README.md) · [Complete source index](../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [glue_settings_model.py](#glue_settings_modelpy)
- [mapper.py](#mapperpy)

## `__init__.py`

Source: [src/robot_systems/glue/applications/glue_settings/model/__init__.py](../../../../../../src/robot_systems/glue/applications/glue_settings/model/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `glue_settings_model.py`

Source: [src/robot_systems/glue/applications/glue_settings/model/glue_settings_model.py](../../../../../../src/robot_systems/glue/applications/glue_settings/model/glue_settings_model.py).

Imports (including optional/function-local imports; not a startup dependency list): `logging`, `src.applications.base.i_application_model`, `src.robot_systems.glue.applications.glue_settings`, `src.robot_systems.glue.applications.glue_settings.model.mapper`, `src.robot_systems.glue.settings.glue`, `src.robot_systems.glue.settings.glue_types`, `typing`.

### `GlueSettingsModel`

```python
class GlueSettingsModel(IApplicationModel):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, service: IGlueSettingsService)
```

```python
def load(self) -> GlueSettings
```

```python
def save(self, flat: dict, **kwargs) -> None
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

## `mapper.py`

Source: [src/robot_systems/glue/applications/glue_settings/model/mapper.py](../../../../../../src/robot_systems/glue/applications/glue_settings/model/mapper.py).

Imports (including optional/function-local imports; not a startup dependency list): `copy`, `src.robot_systems.glue.settings.glue`.

### `GlueSettingsMapper`

```python
class GlueSettingsMapper:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@staticmethod
def to_flat_dict(settings: GlueSettings) -> dict
```

```python
@staticmethod
def from_flat_dict(flat: dict, base: GlueSettings) -> GlueSettings
```
