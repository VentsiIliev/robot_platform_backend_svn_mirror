# Module reference: `src/applications/calibration_settings/controller`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [calibration_settings_controller.py](#calibration_settings_controllerpy)

## `calibration_settings_controller.py`

Source: [src/applications/calibration_settings/controller/calibration_settings_controller.py](../../../../src/applications/calibration_settings/controller/calibration_settings_controller.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.base.i_application_controller`, `src.applications.calibration_settings.mapper`, `src.applications.calibration_settings.model.calibration_settings_model`, `src.applications.calibration_settings.view.calibration_settings_view`.

### `CalibrationSettingsController`

```python
class CalibrationSettingsController(IApplicationController):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, model: CalibrationSettingsModel, view: CalibrationSettingsView, _messaging=None)
```

```python
def load(self) -> None
```

```python
def stop(self) -> None
```
