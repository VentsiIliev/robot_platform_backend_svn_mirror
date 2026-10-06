# Module reference: `src/applications/device_control/dryer`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [application_service.py](#application_servicepy)
- [controller.py](#controllerpy)
- [mapper.py](#mapperpy)
- [model.py](#modelpy)
- [schema.py](#schemapy)
- [service.py](#servicepy)
- [view.py](#viewpy)

## `__init__.py`

Source: [src/applications/device_control/dryer/__init__.py](../../../../src/applications/device_control/dryer/__init__.py).

Dryer-specific panel composed into the shared Device Control application.

Imports (including optional/function-local imports; not a startup dependency list): `.application_service`, `.service`.

Package-level import/export surface:

```python
from .application_service import DryerControlService
from .service import IDryerControlService
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['DryerControlService', 'IDryerControlService']
```

## `application_service.py`

Source: [src/applications/device_control/dryer/application_service.py](../../../../src/applications/device_control/dryer/application_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `enum`, `src.applications.device_control.dryer.service`, `src.engine.hardware.dryer.interfaces.i_dryer_service`, `src.engine.hardware.dryer.models.dryer_config`, `src.engine.repositories.interfaces.i_settings_service`.

### `DryerControlService`

```python
class DryerControlService(IDryerControlService):
```

Persists dryer configuration and updates the live controller.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, settings_service: ISettingsService, dryer_config_key: Enum, live_controller: IDryerService | None=None) -> None
```

```python
def load_config(self) -> DryerConfig
```

```python
def save_config(self, config: DryerConfig) -> None
```

## `controller.py`

Source: [src/applications/device_control/dryer/controller.py](../../../../src/applications/device_control/dryer/controller.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `logging`, `src.applications.base.i_application_controller`, `src.applications.device_control.dryer.model`, `src.applications.device_control.dryer.view`.

### `DryerControlController`

```python
class DryerControlController(IApplicationController):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, model: DryerControlModel, view: DryerControlPanel) -> None
```

```python
def load(self) -> None
```

```python
def stop(self) -> None
```

## `mapper.py`

Source: [src/applications/device_control/dryer/mapper.py](../../../../src/applications/device_control/dryer/mapper.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.engine.hardware.dryer.models.dryer_config`.

### `DryerConfigMapper`

```python
class DryerConfigMapper:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@staticmethod
def to_flat_dict(config: DryerConfig) -> dict
```

```python
@staticmethod
def from_flat_dict(flat: dict, base: DryerConfig) -> DryerConfig
```

## `model.py`

Source: [src/applications/device_control/dryer/model.py](../../../../src/applications/device_control/dryer/model.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `logging`, `src.applications.base.i_application_model`, `src.applications.device_control.dryer.mapper`, `src.applications.device_control.dryer.service`, `src.engine.hardware.dryer.models.dryer_config`.

### `DryerControlModel`

```python
class DryerControlModel(IApplicationModel):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, service: IDryerControlService) -> None
```

```python
def load(self) -> DryerConfig
```

```python
def save(self, flat: dict, **kwargs) -> None
```

```python
def config_from_flat(self, flat: dict) -> DryerConfig
```

## `schema.py`

Source: [src/applications/device_control/dryer/schema.py](../../../../src/applications/device_control/dryer/schema.py).

Imports (including optional/function-local imports; not a startup dependency list): `pl_gui.settings.settings_view.schema`.

Module declarations (expressions are shown without evaluating them):

```python
REGISTER_GROUP = SettingGroup('Servo and Plate Values', [_int_field('pwm_open_vrytka', 'Gate Open PWM', 600), _int_field('pwm_close_vrytka', 'Gate Close PWM', 150), _int_field('pwm_open_izbutvatel', 'Ejector Open PWM', 600), _int_field('pwm_close_izbutvatel', 'Ejector Close PWM', 180), _int_field('rev_minute', 'Revolutions per Minute', 50), SettingField('acceleration', 'Acceleration', 'double_spinbox', default=0.1, min_val=0.0, max_val=6553.5, step=0.1, decimals=1), _int_field('target_position_backword', 'Target Position Backward', 500), _int_field('target_position_forword', 'Target Position Forward', 500)])
TIMING_GROUP = SettingGroup('Timing Values', [_int_field('time_delay_move_servo_up', 'Servo Up Delay', 80), _int_field('time_delay_move_servo_down', 'Servo Down Delay', 50), _int_field('time_delay_move_servo_in', 'Servo In Delay', 30), _int_field('time_delay_move_servo_out', 'Servo Out Delay', 50), _int_field('time_delay_move_plate_in', 'Plate In Delay', 300), _int_field('time_delay_move_plate_out', 'Plate Out Delay', 350), _int_field('time_delay_start_servo_move', 'Servo Start Delay', 50)])
```

### `_int_field`

```python
def _int_field(name: str, label: str, default: int) -> SettingField
```

## `service.py`

Source: [src/applications/device_control/dryer/service.py](../../../../src/applications/device_control/dryer/service.py).

Imports (including optional/function-local imports; not a startup dependency list): `abc`, `src.engine.hardware.dryer.models.dryer_config`.

### `IDryerControlService`

```python
class IDryerControlService(ABC):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def load_config(self) -> DryerConfig
```

```python
@abstractmethod
def save_config(self, config: DryerConfig) -> None
```

## `view.py`

Source: [src/applications/device_control/dryer/view.py](../../../../src/applications/device_control/dryer/view.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtWidgets`, `__future__`, `pl_gui.settings.settings_view.styles`, `src.applications.base.i_application_view`, `src.applications.base.keyboard_settings_view`, `src.applications.base.widgets.custom_virtual_keyboard`, `src.applications.device_control.dryer.mapper`, `src.applications.device_control.dryer.schema`.

### `DryerControlPanel`

```python
class DryerControlPanel(IApplicationView):
```

Declared fields/defaults:

```python
save_requested = pyqtSignal(dict)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, parent=None)
```

```python
def setup_ui(self) -> None
```

```python
def load_config(self, config) -> None
```

```python
def get_values(self) -> dict
```

```python
def set_status(self, message: str) -> None
```

```python
def clean_up(self) -> None
```
