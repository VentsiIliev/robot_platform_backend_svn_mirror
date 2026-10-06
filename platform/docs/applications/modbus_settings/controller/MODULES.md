# Module reference: `src/applications/modbus_settings/controller`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [modbus_settings_controller.py](#modbus_settings_controllerpy)

## `__init__.py`

Source: [src/applications/modbus_settings/controller/__init__.py](../../../../src/applications/modbus_settings/controller/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `modbus_settings_controller.py`

Source: [src/applications/modbus_settings/controller/modbus_settings_controller.py](../../../../src/applications/modbus_settings/controller/modbus_settings_controller.py).

Imports (including optional/function-local imports; not a startup dependency list): `logging`, `src.applications.base.background_worker`, `src.applications.base.i_application_controller`, `src.applications.modbus_settings.model.modbus_settings_model`, `src.applications.modbus_settings.view.modbus_settings_view`.

### `ModbusSettingsController`

```python
class ModbusSettingsController(IApplicationController, BackgroundWorker):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, model: ModbusSettingsModel, view: ModbusSettingsView)
```

```python
def load(self) -> None
```

```python
def stop(self) -> None
```
