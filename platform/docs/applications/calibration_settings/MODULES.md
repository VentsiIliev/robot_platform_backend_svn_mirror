# Module reference: `src/applications/calibration_settings`

[Package guide](README.md) · [Complete source index](../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [calibration_settings_data.py](#calibration_settings_datapy)
- [calibration_settings_factory.py](#calibration_settings_factorypy)
- [mapper.py](#mapperpy)

## `__init__.py`

Source: [src/applications/calibration_settings/__init__.py](../../../src/applications/calibration_settings/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.calibration_settings.calibration_settings_factory`, `src.applications.calibration_settings.service.calibration_settings_application_service`, `src.applications.calibration_settings.service.i_calibration_settings_service`.

Package-level import/export surface:

```python
from src.applications.calibration_settings.calibration_settings_factory import CalibrationSettingsFactory
from src.applications.calibration_settings.service.calibration_settings_application_service import CalibrationSettingsApplicationService
from src.applications.calibration_settings.service.i_calibration_settings_service import ICalibrationSettingsService
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['CalibrationSettingsApplicationService', 'CalibrationSettingsFactory', 'ICalibrationSettingsService']
```

## `calibration_settings_data.py`

Source: [src/applications/calibration_settings/calibration_settings_data.py](../../../src/applications/calibration_settings/calibration_settings_data.py).

Imports (including optional/function-local imports; not a startup dependency list): `dataclasses`, `src.engine.robot.configuration`, `src.engine.robot.height_measuring.settings`, `src.engine.vision.calibration_vision_settings`.

### `CalibrationSettingsData`

```python
@dataclass
class CalibrationSettingsData:
```

Declared fields/defaults:

```python
vision: CalibrationVisionSettings
robot: RobotCalibrationSettings
height: HeightMeasuringModuleSettings | None = None
```

## `calibration_settings_factory.py`

Source: [src/applications/calibration_settings/calibration_settings_factory.py](../../../src/applications/calibration_settings/calibration_settings_factory.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.base.application_factory`, `src.applications.base.i_application_controller`, `src.applications.base.i_application_model`, `src.applications.base.i_application_view`, `src.applications.calibration_settings.controller.calibration_settings_controller`, `src.applications.calibration_settings.model.calibration_settings_model`, `src.applications.calibration_settings.service.i_calibration_settings_service`, `src.applications.calibration_settings.view.calibration_settings_view`.

### `CalibrationSettingsFactory`

```python
class CalibrationSettingsFactory(ApplicationFactory):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, work_area_definitions=None)
```

## `mapper.py`

Source: [src/applications/calibration_settings/mapper.py](../../../src/applications/calibration_settings/mapper.py).

Imports (including optional/function-local imports; not a startup dependency list): `copy`, `json`, `src.applications.calibration_settings.calibration_settings_data`, `src.applications.robot_settings.model.mapper`, `src.engine.robot.height_measuring.settings`, `src.engine.vision.calibration_vision_settings`.

### `CalibrationSettingsMapper`

```python
class CalibrationSettingsMapper:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@staticmethod
def to_flat_dict(data: CalibrationSettingsData) -> dict
```

```python
@staticmethod
def from_flat_dict(flat: dict, base: CalibrationSettingsData) -> CalibrationSettingsData
```
