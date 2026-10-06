# Module reference: `src/robot_systems/glue/domain/dispense_channels`

[Package guide](README.md) · [Complete source index](../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [dispense_channel_service.py](#dispense_channel_servicepy)
- [i_dispense_channel_service.py](#i_dispense_channel_servicepy)

## `dispense_channel_service.py`

Source: [src/robot_systems/glue/domain/dispense_channels/dispense_channel_service.py](../../../../../src/robot_systems/glue/domain/dispense_channels/dispense_channel_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.robot_systems.glue.domain.dispense_channels.i_dispense_channel_service`, `src.robot_systems.glue.processes.glue_dispensing.dispensing_settings`, `src.robot_systems.glue.processes.glue_dispensing.glue_pump_controller`, `src.robot_systems.glue.processes.glue_dispensing.i_glue_type_resolver`.

### `DispenseChannelService`

```python
class DispenseChannelService(IDispenseChannelService):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, pump_controller: GluePumpController, glue_type_resolver: IGlueTypeResolver | None) -> None
```

```python
def resolve_motor_address(self, glue_type: str | None) -> int
```

```python
def start_dispense(self, glue_type: str | None, settings: DispensingSegmentSettings | None=None) -> tuple[bool, int | None]
```

```python
def stop_dispense(self, glue_type: str | None, settings: DispensingSegmentSettings | None=None) -> tuple[bool, int | None]
```

```python
def get_last_exception(self) -> Exception | None
```

## `i_dispense_channel_service.py`

Source: [src/robot_systems/glue/domain/dispense_channels/i_dispense_channel_service.py](../../../../../src/robot_systems/glue/domain/dispense_channels/i_dispense_channel_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `abc`, `src.robot_systems.glue.processes.glue_dispensing.dispensing_settings`.

### `IDispenseChannelService`

```python
class IDispenseChannelService(ABC):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def resolve_motor_address(self, glue_type: str | None) -> int
```

Return motor address for the requested glue type, or -1 if unresolved.

```python
@abstractmethod
def start_dispense(self, glue_type: str | None, settings: DispensingSegmentSettings | None=None) -> tuple[bool, int | None]
```

Start pump flow for the resolved dispense channel.

```python
@abstractmethod
def stop_dispense(self, glue_type: str | None, settings: DispensingSegmentSettings | None=None) -> tuple[bool, int | None]
```

Stop pump flow for the resolved dispense channel.

```python
@abstractmethod
def get_last_exception(self) -> Exception | None
```

Return the last low-level pump-control exception, if any.
