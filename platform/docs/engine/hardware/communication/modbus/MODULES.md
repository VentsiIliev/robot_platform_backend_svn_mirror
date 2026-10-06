# Module reference: `src/engine/hardware/communication/modbus`

[Package guide](README.md) · [Complete source index](../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [i_modbus_action_service.py](#i_modbus_action_servicepy)
- [modbus.py](#modbuspy)
- [modbus_action_service.py](#modbus_action_servicepy)
- [modbus_exception_type.py](#modbus_exception_typepy)
- [modbus_fc16_register_transport.py](#modbus_fc16_register_transportpy)
- [modbus_register_transport.py](#modbus_register_transportpy)
- [serial_bus.py](#serial_buspy)
- [xinje_ma_8x8yr_transport.py](#xinje_ma_8x8yr_transportpy)

## `__init__.py`

Source: [src/engine/hardware/communication/modbus/__init__.py](../../../../../src/engine/hardware/communication/modbus/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.hardware.communication.modbus.xinje_ma_8x8yr_transport`.

Package-level import/export surface:

```python
from src.engine.hardware.communication.modbus.xinje_ma_8x8yr_transport import XinjeMA8X8YRTransport
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['XinjeMA8X8YRTransport']
```

## `i_modbus_action_service.py`

Source: [src/engine/hardware/communication/modbus/i_modbus_action_service.py](../../../../../src/engine/hardware/communication/modbus/i_modbus_action_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `abc`, `src.engine.hardware.communication.modbus.modbus`, `typing`.

### `IModbusActionService`

```python
class IModbusActionService(ABC):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def detect_ports(self) -> List[str]
```

Return available serial port names that have a modbus device.

```python
@abstractmethod
def test_connection(self, config: ModbusConfig) -> bool
```

Attempt a connection with the given config. Return True on success.

```python
@abstractmethod
def grant_serial_port_permissions(self) -> List[str]
```

Grant user read/write access to detected USB serial ports. Return changed port names.

```python
@abstractmethod
def set_serial_port_low_latency(self) -> List[str]
```

Set supported USB serial ports to 1 ms latency and return verified ports.

## `modbus.py`

Source: [src/engine/hardware/communication/modbus/modbus.py](../../../../../src/engine/hardware/communication/modbus/modbus.py).

Imports (including optional/function-local imports; not a startup dependency list): `copy`, `dataclasses`, `src.engine.repositories.interfaces.settings_serializer`, `typing`.

### `ModbusDeviceConfig`

```python
@dataclass
class ModbusDeviceConfig:
```

Complete serial and slave configuration for one Modbus device.

Declared fields/defaults:

```python
port: str = 'COM5'
baudrate: int = 115200
bytesize: int = 8
stopbits: int = 1
parity: str = 'N'
timeout: float = 0.01
slave_address: int = 10
max_retries: int = 30
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def from_dict(cls, data: Dict[str, Any]) -> 'ModbusDeviceConfig'
```

```python
def to_dict(self) -> Dict[str, Any]
```

### `ModbusSlaveConfig`

```python
@dataclass
class ModbusSlaveConfig:
```

A Modbus slave ID assigned to a serial connection profile.

Declared fields/defaults:

```python
slave_address: int = 10
profile_name: str = 'default'
transport_type: str = 'modbus_register'
max_retries: int = 30
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def from_dict(cls, data: Dict[str, Any]) -> 'ModbusSlaveConfig'
```

```python
def to_dict(self) -> Dict[str, Any]
```

### `ModbusConfig`

```python
@dataclass
class ModbusConfig(ModbusDeviceConfig):
```

Legacy default profile plus optional named device profiles. The inherited fields remain the default profile for existing consumers. ``devices`` contains additional profiles keyed by a stable device name.

Declared fields/defaults:

```python
devices: Dict[str, ModbusDeviceConfig] = field(default_factory=dict)
profiles: Dict[str, ModbusDeviceConfig] = field(default_factory=dict)
slaves: Dict[str, ModbusSlaveConfig] = field(default_factory=dict)
port: str = 'COM5'
baudrate: int = 115200
bytesize: int = 8
stopbits: int = 1
parity: str = 'N'
timeout: float = 0.01
slave_address: int = 10
max_retries: int = 30
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def from_dict(cls, data: Dict[str, Any]) -> 'ModbusConfig'
```

```python
def to_dict(self) -> Dict[str, Any]
```

```python
def get_profile(self, name: str='default', fallback_to_default: bool=False) -> ModbusDeviceConfig
```

Return a copy so callers cannot mutate settings accidentally.

```python
def set_profile(self, name: str, profile: ModbusDeviceConfig) -> None
```

```python
def profile_names(self) -> list[str]
```

```python
def slave_names(self) -> list[str]
```

```python
def get_slave(self, name: str='default') -> ModbusSlaveConfig
```

```python
def set_slave(self, name: str, slave: ModbusSlaveConfig) -> None
```

```python
def find_slave_name(self, slave_address: int) -> str
```

Return the configured slave name for a numeric slave address.

```python
def get_connection(self, slave_name: str='default') -> ModbusDeviceConfig
```

Resolve a slave ID and its assigned serial profile.

```python
def update_field(self, field: str, value: Any) -> None
```

### `ModbusConfigSerializer`

```python
class ModbusConfigSerializer(ISettingsSerializer[ModbusConfig]):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@property
def settings_type(self) -> str
```

```python
def get_default(self) -> ModbusConfig
```

```python
def to_dict(self, settings: ModbusConfig) -> Dict[str, Any]
```

```python
def from_dict(self, data: Dict[str, Any]) -> ModbusConfig
```

## `modbus_action_service.py`

Source: [src/engine/hardware/communication/modbus/modbus_action_service.py](../../../../../src/engine/hardware/communication/modbus/modbus_action_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `logging`, `os`, `pathlib`, `serial`, `serial.tools.list_ports`, `src.engine.hardware.communication.modbus.i_modbus_action_service`, `src.engine.hardware.communication.modbus.modbus`, `subprocess`, `typing`.

### `ModbusActionService`

```python
class ModbusActionService(IModbusActionService):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self)
```

```python
def detect_ports(self) -> List[str]
```

```python
def test_connection(self, config: ModbusConfig) -> bool
```

```python
def grant_serial_port_permissions(self) -> List[str]
```

```python
def set_serial_port_low_latency(self) -> List[str]
```

## `modbus_exception_type.py`

Source: [src/engine/hardware/communication/modbus/modbus_exception_type.py](../../../../../src/engine/hardware/communication/modbus/modbus_exception_type.py).

Imports (including optional/function-local imports; not a startup dependency list): `enum`.

### `ModbusExceptionType`

```python
class ModbusExceptionType(Enum):
```

Declared fields/defaults:

```python
MODBUS_EXCEPTION = 'ModbusException'
INVALID_RESPONSE_ERROR = 'InvalidResponseError'
NO_RESPONSE_ERROR = 'NoResponseError'
LOCAL_ECHO_ERROR = 'LocalEchoError'
ILLEGAL_REQUEST_ERROR = 'IllegalRequestError'
IO_ERROR = 'IOError'
SERIAL_ERROR = 'SerialException'
TIMEOUT_ERROR = 'timeout'
CONNECTION_ERROR = 'connection'
CHECKSUM_ERROR = 'Checksum error in rtu mode'
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def description(self) -> str
```

```python
@classmethod
def from_exception(cls, exc: Exception) -> 'ModbusExceptionType'
```

## `modbus_fc16_register_transport.py`

Source: [src/engine/hardware/communication/modbus/modbus_fc16_register_transport.py](../../../../../src/engine/hardware/communication/modbus/modbus_fc16_register_transport.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.engine.hardware.communication.modbus.modbus_register_transport`.

### `ModbusFc16RegisterTransport`

```python
class ModbusFc16RegisterTransport(ModbusRegisterTransport):
```

Standard Modbus RTU registers with FC16 for single-register writes.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def write_register(self, address: int, value: int) -> None
```

## `modbus_register_transport.py`

Source: [src/engine/hardware/communication/modbus/modbus_register_transport.py](../../../../../src/engine/hardware/communication/modbus/modbus_register_transport.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `logging`, `minimalmodbus`, `src.engine.hardware.communication.i_register_transport`, `src.engine.hardware.communication.modbus.serial_bus`, `typing`.

### `_Session`

```python
class _Session:
```

Per-call or persistent Modbus instrument session.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, transport: ModbusRegisterTransport) -> None
```

### `ModbusRegisterTransport`

```python
class ModbusRegisterTransport(IRegisterTransport):
```

Shared Modbus RTU implementation of IRegisterTransport via minimalmodbus. All four register operations are overridden for native batch efficiency. Supports both per-call and persistent connections — call connect() / disconnect() to keep a session open for hot-path callers. Do not instantiate directly — subclass for your device: class ModbusMotorTransport(ModbusRegisterTransport, IMotorTransport): pass class ModbusGeneratorTransport(ModbusRegisterTransport, IGeneratorTransport): pass

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, port: str, slave_address: int, baudrate: int=115200, bytesize: int=8, stopbits: int=1, parity: str='N', timeout: float=0.03) -> None
```

```python
def read_register(self, address: int) -> int
```

```python
def read_registers(self, address: int, count: int) -> List[int]
```

```python
def write_register(self, address: int, value: int) -> None
```

```python
def write_registers(self, address: int, values: List[int]) -> None
```

```python
def connect(self) -> None
```

```python
def disconnect(self) -> None
```

## `serial_bus.py`

Source: [src/engine/hardware/communication/modbus/serial_bus.py](../../../../../src/engine/hardware/communication/modbus/serial_bus.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `contextlib`, `threading`.

### `get_serial_bus_lock`

```python
def get_serial_bus_lock(port: str) -> threading.RLock
```

Return the process-wide transaction lock for one physical serial port.

### `serial_bus_session`

```python
def serial_bus_session(port: str, timeout: float)
```

Keep one complete request/response exchange atomic on a serial port.

## `xinje_ma_8x8yr_transport.py`

Source: [src/engine/hardware/communication/modbus/xinje_ma_8x8yr_transport.py](../../../../../src/engine/hardware/communication/modbus/xinje_ma_8x8yr_transport.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `logging`, `minimalmodbus`, `os`, `select`, `serial`, `src.engine.hardware.communication.modbus.modbus_register_transport`, `src.engine.hardware.communication.modbus.serial_bus`, `struct`, `termios`, `time`, `typing`.

### `_write_fd_bounded`

```python
def _write_fd_bounded(fd: int, data: bytes, timeout: float) -> None
```

Write a complete RTU frame without allowing the driver to block.

### `ModbusExceptionResponse`

```python
class ModbusExceptionResponse(RuntimeError):
```

Raised when the Xinje slave returns a Modbus exception response.

### `_crc16`

```python
def _crc16(data: bytes) -> int
```

### `XinjeMA8X8YRTransport`

```python
class XinjeMA8X8YRTransport(ModbusRegisterTransport):
```

Modbus RTU transport for Xinje MA-8X8YR relay/I/O modules. The MA output image is written as one FC15 block at addresses K128-K143. Other coil addresses use FC5. Raw writes use a directly configured serial port because some USB-RS485 adapters do not reliably preserve the serial line settings through minimalmodbus.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, *args, write_retry_delay_s: float=0.02, **kwargs) -> None
```

```python
def write_register(self, address: int, value: int) -> None
```

```python
def write_registers(self, address: int, values: List[int]) -> None
```

```python
def write_coil_fc5(self, address: int, value: bool) -> None
```

```python
def write_coils_fc15(self, address: int, values: List[int]) -> None
```

```python
def write_register_fc6(self, address: int, value: int) -> None
```

```python
def write_registers_fc16(self, address: int, values: List[int]) -> None
```

```python
def read_register(self, address: int) -> int
```

```python
def read_registers(self, address: int, count: int) -> List[int]
```

```python
def read_input(self, address: int) -> int
```

Read one Xinje X point through the MA coil-read function. MA-8X8YR firmware exposes the X image through FC1; FC2 returns exception code 1 (illegal function) on this module.
