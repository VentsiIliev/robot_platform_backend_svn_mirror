# Module reference: `src/engine/hardware/communication`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [i_register_transport.py](#i_register_transportpy)
- [live_register_transport.py](#live_register_transportpy)
- [transport_registry.py](#transport_registrypy)

## `__init__.py`

Source: [src/engine/hardware/communication/__init__.py](../../../../src/engine/hardware/communication/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.hardware.communication.i_register_transport`, `src.engine.hardware.communication.live_register_transport`.

Package-level import/export surface:

```python
from src.engine.hardware.communication.i_register_transport import IRegisterTransport
from src.engine.hardware.communication.live_register_transport import LiveRegisterTransport
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['IRegisterTransport', 'LiveRegisterTransport']
```

## `i_register_transport.py`

Source: [src/engine/hardware/communication/i_register_transport.py](../../../../src/engine/hardware/communication/i_register_transport.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `abc`, `typing`.

### `IRegisterTransport`

```python
class IRegisterTransport(ABC):
```

Protocol-agnostic register I/O for any register-mapped device (motor controller, generator relay, solenoid board, etc.). Only read_register() is abstract — the minimum any implementation must provide. write_register → defaults to write_registers([value]) write_registers → defaults to looping write_register read_registers → defaults to looping read_register Implementations override whichever is most efficient for their transport (Modbus overrides all four; a simple GPIO driver might only override read_register and write_register). connect/disconnect — no-ops by default; override for persistent connections.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def read_register(self, address: int) -> int
```

Read a single register. Raises on failure.

```python
def read_registers(self, address: int, count: int) -> List[int]
```

Read count registers. Default: loop. Override for batch efficiency.

```python
def write_register(self, address: int, value: int) -> None
```

Write one register. Default: delegates to write_registers.

```python
def write_registers(self, address: int, values: List[int]) -> None
```

Write consecutive registers. Default: loop. Override for batch efficiency.

```python
def connect(self) -> None
```

Open a persistent connection. No-op by default.

```python
def disconnect(self) -> None
```

Close the persistent connection. No-op by default.

## `live_register_transport.py`

Source: [src/engine/hardware/communication/live_register_transport.py](../../../../src/engine/hardware/communication/live_register_transport.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.engine.hardware.communication.i_register_transport`, `typing`.

### `LiveRegisterTransport`

```python
class LiveRegisterTransport(IRegisterTransport):
```

Build a fresh concrete register transport from live settings on each call. This is useful when transport configuration is persisted in settings and may change at runtime. Instead of snapshotting Modbus parameters at construction time, callers provide a factory that reads the current settings and returns a concrete `IRegisterTransport` for each operation.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, build_transport: Callable[[], IRegisterTransport]) -> None
```

```python
def write_register(self, address: int, value: int) -> None
```

```python
def read_register(self, address: int) -> int
```

```python
def write_registers(self, address: int, values: list) -> None
```

```python
def read_registers(self, address: int, count: int) -> list
```

## `transport_registry.py`

Source: [src/engine/hardware/communication/transport_registry.py](../../../../src/engine/hardware/communication/transport_registry.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`, `src.engine.hardware.communication.i_register_transport`, `src.engine.hardware.communication.modbus.modbus`, `src.engine.hardware.communication.modbus.modbus_fc16_register_transport`, `src.engine.hardware.communication.modbus.modbus_register_transport`, `src.engine.hardware.communication.modbus.xinje_ma_8x8yr_transport`, `typing`.

Module declarations (expressions are shown without evaluating them):

```python
TransportFactory = Callable[[ModbusDeviceConfig], IRegisterTransport]
DEFAULT_TRANSPORT_REGISTRY = build_default_transport_registry()
```

### `TransportDescriptor`

```python
@dataclass(frozen=True)
class TransportDescriptor:
```

Declared fields/defaults:

```python
key: str
label: str
factory: TransportFactory
```

### `TransportRegistry`

```python
class TransportRegistry:
```

Engine-level registry of selectable hardware transport factories.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self) -> None
```

```python
def register(self, descriptor: TransportDescriptor) -> None
```

```python
def get(self, key: str) -> TransportDescriptor
```

```python
def descriptors(self) -> tuple[TransportDescriptor, ...]
```

```python
def keys(self) -> tuple[str, ...]
```

```python
def build_for_slave(self, config: ModbusConfig, slave_name: str) -> IRegisterTransport
```

```python
def build_for_slave_id(self, config: ModbusConfig, slave_id: int) -> IRegisterTransport
```

### `build_default_transport_registry`

```python
def build_default_transport_registry() -> TransportRegistry
```
