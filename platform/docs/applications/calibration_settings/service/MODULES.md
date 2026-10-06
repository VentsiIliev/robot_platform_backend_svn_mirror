# Module reference: `src/applications/calibration_settings/service`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [calibration_settings_application_service.py](#calibration_settings_application_servicepy)
- [i_calibration_settings_service.py](#i_calibration_settings_servicepy)

## `calibration_settings_application_service.py`

Source: [src/applications/calibration_settings/service/calibration_settings_application_service.py](../../../../src/applications/calibration_settings/service/calibration_settings_application_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `datetime`, `math`, `src.applications.calibration_settings.calibration_settings_data`, `src.applications.calibration_settings.service.i_calibration_settings_service`, `src.engine.common_settings_ids`, `src.engine.repositories.interfaces.i_settings_service`, `src.engine.vision.camera_settings_serializer`, `src.engine.vision.i_vision_service`, `src.shared_contracts.events.robot_events`.

### `CalibrationSettingsApplicationService`

```python
class CalibrationSettingsApplicationService(ICalibrationSettingsService):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, settings_service: ISettingsService, vision_service: IVisionService | None=None, robot_service=None, messaging=None, *, include_height_settings: bool=True)
```

```python
def load_settings(self) -> CalibrationSettingsData
```

```python
def save_settings(self, settings: CalibrationSettingsData) -> None
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

## `i_calibration_settings_service.py`

Source: [src/applications/calibration_settings/service/i_calibration_settings_service.py](../../../../src/applications/calibration_settings/service/i_calibration_settings_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `abc`, `src.applications.calibration_settings.calibration_settings_data`.

### `ICalibrationSettingsService`

```python
class ICalibrationSettingsService(ABC):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def load_settings(self) -> CalibrationSettingsData
```

```python
@abstractmethod
def save_settings(self, settings: CalibrationSettingsData) -> None
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
