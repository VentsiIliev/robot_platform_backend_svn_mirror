# `src/engine/hardware/communication/` — Register Transport Layer

The protocol-agnostic foundation of every register-mapped device in the platform.
Motors, generators, solenoid boards, fans, dryers, vacuum pumps, vacuum sensors,
and physical control buttons all speak through `IRegisterTransport` — nothing
above this layer knows whether the bytes travel over Modbus RTU, GPIO, or a test
double.

---

## Files

| File | Contents |
|------|----------|
| `i_register_transport.py` | `IRegisterTransport` — the abstract register I/O contract |
| `transport_registry.py` | `TransportRegistry`, `TransportDescriptor`, `DEFAULT_TRANSPORT_REGISTRY` |
| `live_register_transport.py` | `LiveRegisterTransport` — rebuilds a concrete transport per call |
| `modbus/` | Modbus RTU implementation and settings model — see [modbus/README.md](modbus/README.md) |

---

## Stack

```
IRegisterTransport                       ← abstract, only read_register is required
  │
  ├── ModbusRegisterTransport            ← minimalmodbus RTU, overrides all 4 ops
  │     ├── ModbusFc16RegisterTransport   ← FC16 instead of FC6 for single writes
  │     ├── XinjeMA8X8YRTransport         ← FC5/FC15 coil writes on a raw serial port
  │     ├── ModbusMotorTransport          ← + IMotorTransport
  │     ├── ModbusGeneratorTransport      ← + IGeneratorTransport
  │     └── ModbusDryerTransport          ← + IDryerTransport
  │
  ├── LiveRegisterTransport              ← delegates to a freshly built transport
  └── (test doubles in each device package's mock_runner.py)
```

---

## `IRegisterTransport`

**File:** `i_register_transport.py`

```python
class IRegisterTransport(ABC):
    @abstractmethod
    def read_register(self, address: int) -> int: ...

    def read_registers(self, address: int, count: int) -> List[int]:
        return [self.read_register(address + i) for i in range(count)]

    def write_register(self, address: int, value: int) -> None:
        self.write_registers(address, [value])

    def write_registers(self, address: int, values: List[int]) -> None:
        for i, v in enumerate(values):
            self.write_register(address + i, v)

    def connect(self) -> None: ...
    def disconnect(self) -> None: ...
```

### Default method chain

Only `read_register` is abstract — the minimum any implementation must provide.
Everything else has a working default, so an implementation overrides only what
its transport does efficiently:

| Method | Default behaviour | Override when |
|--------|-------------------|---------------|
| `read_register` | **abstract** | always |
| `read_registers` | loops `read_register(address + i)` | the transport supports batch reads (FC3) |
| `write_register` | delegates to `write_registers([value])` | the transport has a cheaper single-write opcode |
| `write_registers` | loops `write_register(address + i, v)` | the transport supports batch writes (FC16/FC15) |
| `connect` | no-op | the transport can hold a persistent session |
| `disconnect` | no-op | the transport can hold a persistent session |

> The default `write_register` → `write_registers` direction is intentional. A
> transport that batches writes natively gets a single-register write for free,
> while a transport that only implements FC6 correctly overrides the other way.

### Adding a new device transport

Subclass `ModbusRegisterTransport` and the device's semantic interface. Add a
docstring only — no method bodies:

```python
class ModbusMyDeviceTransport(ModbusRegisterTransport, IMyDeviceTransport):
    """Modbus RTU transport for my device boards."""
```

`IMotorTransport`, `IGeneratorTransport`, `IDryerTransport`,
`IVacuumPumpTransport`, `IVacuumSensorTransport`, and `IDryerTransport` are all
**semantic type aliases** of `IRegisterTransport` — they add no methods and
exist purely to constrain injection sites so a motor controller cannot be handed
a vacuum-sensor transport by mistake.

---

## `TransportRegistry`

**File:** `transport_registry.py`

Selects which transport implementation backs a given Modbus slave, based on the
`transport_type` string stored in settings.

```python
@dataclass(frozen=True)
class TransportDescriptor:
    key: str                                  # stored in settings
    label: str                                # shown in the UI dropdown
    factory: Callable[[ModbusDeviceConfig], IRegisterTransport]
```

| Method | Description |
|--------|-------------|
| `register(descriptor)` | Adds a transport. Raises `ValueError` if `key` already exists |
| `get(key)` | Returns the descriptor; raises `ValueError` for an unknown key |
| `descriptors()` | Tuple of all registered descriptors, for UI population |
| `keys()` | Tuple of registered keys |
| `build_for_slave(config, slave_name)` | Resolves `slave_name` → slave → profile → concrete transport |
| `build_for_slave_id(config, slave_id)` | Same, resolving the numeric address back to a name via `config.find_slave_name` |

`build_for_slave` performs a two-step resolution:

```
slave_name ──get_slave()──► ModbusSlaveConfig(slave_address, profile_name, transport_type)
                                                       │
profile_name ──get_profile()─► ModbusDeviceConfig(port, baudrate, …, slave_address)
                                                       │
transport_type ──get()──────► TransportDescriptor.factory(connection)
                                                       │
                                                       ▼
                                            IRegisterTransport
```

### Registered transports

`DEFAULT_TRANSPORT_REGISTRY` is built at import time by
`build_default_transport_registry()`:

| Key | Label | Implementation |
|-----|-------|----------------|
| `modbus_register` | Standard Modbus Registers | `ModbusRegisterTransport` |
| `modbus_register_fc16` | Standard Modbus Registers (FC16 writes) | `ModbusFc16RegisterTransport` |
| `xinje_ma_8x8yr` | Xinje MA-8X8YR | `XinjeMA8X8YRTransport` |

Device factories use it to honour the configured transport type:

```python
from src.engine.hardware.communication.transport_registry import DEFAULT_TRANSPORT_REGISTRY

transport = DEFAULT_TRANSPORT_REGISTRY.build_for_slave(modbus_config, "motor")
# → resolves transport_type from settings and builds the matching transport
```

Robot systems may register additional descriptors on their own registry instance
to support site-specific hardware, without changing engine code.

---

## `LiveRegisterTransport`

**File:** `live_register_transport.py`

Wraps a *factory* instead of a transport instance, so serial parameters are
re-read from settings on every operation:

```python
class LiveRegisterTransport(IRegisterTransport):
    def __init__(self, build_transport: Callable[[], IRegisterTransport]) -> None:
        self._build_transport = build_transport
```

Each of the four register operations calls `_fresh()`, invokes the injected
callable, and performs one operation on the returned transport. The intermediate
transport is not kept.

Use it when transport configuration is persisted in settings and may change while
the application is running — for example after the user edits the Modbus port or
baudrate in a settings screen. A normally constructed transport snapshots its
parameters at construction time and would keep using the old values until
restart.

> Cost: this trades connection reuse for freshness. It is intended for
> low-frequency configuration-driven paths, not hot polling loops.

---

## Design Notes

- **`minimalmodbus` is an implementation detail.** It is imported inside
  `ModbusRegisterTransport._make_instrument()` and nowhere else, so the platform
  loads even when the library is absent, and only real register I/O fails.
- **Device semantics live above this layer.** Transports move integers; they do
  not know that address `128` means "vacuum pump on".
- **One port, one lock.** Every Modbus exchange runs inside `serial_bus_session()`
  (see [modbus/README.md](modbus/README.md#serial_buspy--port-transaction-locking)) so that multiple
  peripherals sharing one RS-485 adapter cannot interleave frames.

## Default write-method limitation

`IRegisterTransport` makes only `read_register()` abstract. Its default single and batch writes delegate to each other, so an implementation must override at least one write method to support writing. A subclass implementing only the abstract read operation can instantiate but gets `RecursionError` on a nonempty write. Existing Modbus implementations override writes. See [code issues](../../../CODE_ISSUES.md).

<!-- source-navigation:start -->
## Source navigation

[Module reference](MODULES.md) — signatures, fields, imports and source links for every Python file in this directory.

| Source subdirectory | Guide |
|---|---|
| `modbus/` | [modbus](modbus/README.md) |

[Complete source index](../../../SOURCE_INDEX.md).
<!-- source-navigation:end -->
