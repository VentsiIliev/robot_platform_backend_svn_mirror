# Module reference: `src/robot_systems/glue/applications/dispense_channel_settings/service`

[Package guide](README.md) · [Complete source index](../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [dispense_channel_settings_service.py](#dispense_channel_settings_servicepy)
- [i_dispense_channel_settings_service.py](#i_dispense_channel_settings_servicepy)

## `dispense_channel_settings_service.py`

Source: [src/robot_systems/glue/applications/dispense_channel_settings/service/dispense_channel_settings_service.py](../../../../../../src/robot_systems/glue/applications/dispense_channel_settings/service/dispense_channel_settings_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`, `logging`, `src.engine.hardware.motor.interfaces.i_motor_service`, `src.engine.hardware.weight.config`, `src.engine.hardware.weight.interfaces.i_weight_cell_service`, `src.engine.repositories.interfaces.i_settings_service`, `src.robot_systems.glue.applications.dispense_channel_settings.service.i_dispense_channel_settings_service`, `src.robot_systems.glue.processes.glue_dispensing.glue_pump_controller`, `src.robot_systems.glue.settings.dispense_channels`, `src.shared_contracts.declarations`, `typing`.

### `DispenseChannelSettingsService`

```python
class DispenseChannelSettingsService(IDispenseChannelSettingsService):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, settings_service: ISettingsService, channel_settings_key, cells_settings_key, catalog_settings_key, glue_settings_key, channel_definitions: List[DispenseChannelDefinition], weight_service: Optional[IWeightCellService]=None, motor_service: Optional[IMotorService]=None) -> None
```

```python
def get_channel_definitions(self) -> List[DispenseChannelDefinition]
```

```python
def get_available_glue_types(self) -> List[str]
```

```python
def get_channel_flat(self, channel_id: str) -> Optional[dict]
```

```python
def save_channel(self, channel_id: str, flat: dict) -> None
```

```python
def tare(self, channel_id: str) -> bool
```

```python
def start_pump_test(self, channel_id: str) -> bool
```

```python
def stop_pump_test(self, channel_id: str) -> bool
```

## `i_dispense_channel_settings_service.py`

Source: [src/robot_systems/glue/applications/dispense_channel_settings/service/i_dispense_channel_settings_service.py](../../../../../../src/robot_systems/glue/applications/dispense_channel_settings/service/i_dispense_channel_settings_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `abc`, `src.shared_contracts.declarations`, `typing`.

### `IDispenseChannelSettingsService`

```python
class IDispenseChannelSettingsService(ABC):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def get_channel_definitions(self) -> List[DispenseChannelDefinition]
```

```python
@abstractmethod
def get_available_glue_types(self) -> List[str]
```

```python
@abstractmethod
def get_channel_flat(self, channel_id: str) -> Optional[dict]
```

```python
@abstractmethod
def save_channel(self, channel_id: str, flat: dict) -> None
```

```python
@abstractmethod
def tare(self, channel_id: str) -> bool
```

```python
@abstractmethod
def start_pump_test(self, channel_id: str) -> bool
```

```python
@abstractmethod
def stop_pump_test(self, channel_id: str) -> bool
```
