# Module reference: `src/applications/device_control/service`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [device_control_application_service.py](#device_control_application_servicepy)
- [i_device_control_service.py](#i_device_control_servicepy)
- [stub_device_control_service.py](#stub_device_control_servicepy)

## `__init__.py`

Source: [src/applications/device_control/service/__init__.py](../../../../src/applications/device_control/service/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.device_control.service.i_device_control_service`, `src.applications.device_control.service.stub_device_control_service`.

Package-level import/export surface:

```python
from src.applications.device_control.service.i_device_control_service import IDeviceControlService
from src.applications.device_control.service.stub_device_control_service import StubDeviceControlService
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['IDeviceControlService', 'StubDeviceControlService']
```

## `device_control_application_service.py`

Source: [src/applications/device_control/service/device_control_application_service.py](../../../../src/applications/device_control/service/device_control_application_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `logging`, `src.applications.device_control.service.i_device_control_service`, `src.engine.hardware.generator.interfaces.i_generator_controller`, `src.engine.hardware.laser.i_laser_control`, `src.engine.hardware.motor.interfaces.i_motor_service`, `src.engine.hardware.vacuum_pump.interfaces.i_vacuum_pump_controller`, `threading`, `typing`.

### `DeviceControlApplicationService`

```python
class DeviceControlApplicationService(IDeviceControlService):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, motors: List[MotorEntry], motor_service: Optional[IMotorService]=None, generator: Optional[IGeneratorController]=None, laser: Optional[ILaserControl]=None, vacuum_pump: Optional[IVacuumPumpController]=None, devices: Optional[Sequence[IDeviceControlDevice]]=None) -> None
```

```python
def get_devices(self) -> List[IDeviceControlDevice]
```

```python
def execute_device_action(self, device_key: str, action: str) -> bool
```

```python
def read_device_state(self, device_key: str) -> Mapping[str, object]
```

```python
def set_device_enabled(self, device_key: str, enabled: bool) -> bool
```

```python
def is_device_enabled(self, device_key: str) -> bool
```

```python
def get_motors(self) -> List[MotorEntry]
```

```python
def get_motor_health_snapshot(self) -> Dict[int, bool]
```

```python
def laser_on(self) -> None
```

```python
def laser_off(self) -> None
```

```python
def vacuum_pump_on(self) -> bool
```

```python
def vacuum_pump_off(self) -> bool
```

```python
def motor_on(self, address: int) -> bool
```

```python
def motor_off(self, address: int) -> bool
```

```python
def generator_on(self) -> bool
```

```python
def generator_off(self) -> bool
```

```python
def is_laser_available(self) -> bool
```

```python
def is_vacuum_pump_available(self) -> bool
```

```python
def is_motor_available(self) -> bool
```

```python
def is_generator_available(self) -> bool
```

## `i_device_control_service.py`

Source: [src/applications/device_control/service/i_device_control_service.py](../../../../src/applications/device_control/service/i_device_control_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `abc`, `dataclasses`, `typing`.

### `MotorEntry`

```python
@dataclass
class MotorEntry:
```

Declared fields/defaults:

```python
name: str
address: int
```

### `IDeviceControlDevice`

```python
class IDeviceControlDevice(Protocol):
```

Configuration-driven device surface consumed by the shared app.

Declared fields/defaults:

```python
key: str
label: str
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def actions(self) -> Mapping[str, str]
```

```python
def execute(self, action: str) -> bool
```

```python
def read_state(self) -> Mapping[str, object]
```

```python
def set_enabled(self, enabled: bool) -> bool
```

```python
def is_enabled(self) -> bool
```

```python
def last_error(self) -> str | None
```

### `IDeviceControlService`

```python
class IDeviceControlService(ABC):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def get_devices(self) -> List[IDeviceControlDevice]
```

```python
@abstractmethod
def execute_device_action(self, device_key: str, action: str) -> bool
```

```python
@abstractmethod
def read_device_state(self, device_key: str) -> Mapping[str, object]
```

```python
@abstractmethod
def set_device_enabled(self, device_key: str, enabled: bool) -> bool
```

```python
@abstractmethod
def is_device_enabled(self, device_key: str) -> bool
```

```python
@abstractmethod
def get_motors(self) -> List[MotorEntry]
```

```python
@abstractmethod
def get_motor_health_snapshot(self) -> Dict[int, bool]
```

Returns {address: is_healthy} for every configured motor. Does board I/O — call from a background thread.

```python
@abstractmethod
def laser_on(self) -> None
```

```python
@abstractmethod
def laser_off(self) -> None
```

```python
@abstractmethod
def vacuum_pump_on(self) -> bool
```

```python
@abstractmethod
def vacuum_pump_off(self) -> bool
```

```python
@abstractmethod
def motor_on(self, address: int) -> bool
```

```python
@abstractmethod
def motor_off(self, address: int) -> bool
```

```python
@abstractmethod
def generator_on(self) -> bool
```

```python
@abstractmethod
def generator_off(self) -> bool
```

```python
@abstractmethod
def is_laser_available(self) -> bool
```

```python
@abstractmethod
def is_vacuum_pump_available(self) -> bool
```

```python
@abstractmethod
def is_motor_available(self) -> bool
```

```python
@abstractmethod
def is_generator_available(self) -> bool
```

## `stub_device_control_service.py`

Source: [src/applications/device_control/service/stub_device_control_service.py](../../../../src/applications/device_control/service/stub_device_control_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.device_control.service.i_device_control_service`, `typing`.

### `StubDeviceControlService`

```python
class StubDeviceControlService(IDeviceControlService):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def get_devices(self)
```

```python
def execute_device_action(self, device_key: str, action: str) -> bool
```

```python
def read_device_state(self, device_key: str) -> Mapping[str, object]
```

```python
def set_device_enabled(self, device_key: str, enabled: bool) -> bool
```

```python
def is_device_enabled(self, device_key: str) -> bool
```

```python
def get_motors(self) -> List[MotorEntry]
```

```python
def get_motor_health_snapshot(self) -> Dict[int, bool]
```

```python
def laser_on(self) -> None
```

```python
def laser_off(self) -> None
```

```python
def vacuum_pump_on(self) -> bool
```

```python
def vacuum_pump_off(self) -> bool
```

```python
def motor_on(self, address: int) -> bool
```

```python
def motor_off(self, address: int) -> bool
```

```python
def generator_on(self) -> bool
```

```python
def generator_off(self) -> bool
```

```python
def is_laser_available(self) -> bool
```

```python
def is_vacuum_pump_available(self) -> bool
```

```python
def is_motor_available(self) -> bool
```

```python
def is_generator_available(self) -> bool
```
