# Module reference: `src/robot_systems/glue/applications/glue_settings/controller`

[Package guide](README.md) · [Complete source index](../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [glue_settings_controller.py](#glue_settings_controllerpy)

## `__init__.py`

Source: [src/robot_systems/glue/applications/glue_settings/controller/__init__.py](../../../../../../src/robot_systems/glue/applications/glue_settings/controller/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `glue_settings_controller.py`

Source: [src/robot_systems/glue/applications/glue_settings/controller/glue_settings_controller.py](../../../../../../src/robot_systems/glue/applications/glue_settings/controller/glue_settings_controller.py).

Imports (including optional/function-local imports; not a startup dependency list): `logging`, `src.applications.base.i_application_controller`, `src.robot_systems.glue.applications.glue_settings.model.glue_settings_model`, `src.robot_systems.glue.applications.glue_settings.view.glue_settings_view`.

### `GlueSettingsController`

```python
class GlueSettingsController(IApplicationController):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, model: GlueSettingsModel, view: GlueSettingsView)
```

```python
def load(self) -> None
```

```python
def stop(self) -> None
```
