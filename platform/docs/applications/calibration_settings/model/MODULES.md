# Module reference: `src/applications/calibration_settings/model`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [calibration_settings_model.py](#calibration_settings_modelpy)

## `calibration_settings_model.py`

Source: [src/applications/calibration_settings/model/calibration_settings_model.py](../../../../src/applications/calibration_settings/model/calibration_settings_model.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.base.i_application_model`, `src.applications.calibration_settings.calibration_settings_data`, `src.applications.calibration_settings.service.i_calibration_settings_service`.

### `CalibrationSettingsModel`

```python
class CalibrationSettingsModel(IApplicationModel):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, service: ICalibrationSettingsService)
```

```python
def load(self) -> CalibrationSettingsData
```

```python
def save(self, settings: CalibrationSettingsData) -> None
```

```python
def capture_workobject_point(self, point_name: str) -> tuple[bool, str, dict]
```

```python
def solve_workobject(self, user_id: int, name: str='') -> tuple[bool, str, dict]
```

```python
def save_workobject(self, user_id: int, name: str='', persist: bool=True) -> tuple[bool, str, dict]
```

```python
@property
def current_settings(self) -> CalibrationSettingsData
```
