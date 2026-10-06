# `src/engine/hardware/communication/modbus/` — Modbus

This package provides the configuration model, port discovery/connection testing, and the RTU transports themselves for Modbus communication over serial ports. Device-specific read/write operations are left to higher-level code.

---

## Files

| File | Contents |
|------|----------|
| `modbus.py` | `ModbusDeviceConfig`, `ModbusSlaveConfig`, `ModbusConfig`, `ModbusConfigSerializer` |
| `serial_bus.py` | `get_serial_bus_lock()`, `serial_bus_session()` — per-port transaction locking |
| `modbus_register_transport.py` | `ModbusRegisterTransport`, `_Session` |
| `modbus_fc16_register_transport.py` | `ModbusFc16RegisterTransport` |
| `xinje_ma_8x8yr_transport.py` | `XinjeMA8X8YRTransport`, `ModbusExceptionResponse` |
| `modbus_action_service.py` | `ModbusActionService` — port discovery + connection test |
| `i_modbus_action_service.py` | `IModbusActionService` |
| `modbus_exception_type.py` | `ModbusExceptionType` |

Parent package: [../README.md](../README.md) documents `IRegisterTransport`,
`TransportRegistry`, and `LiveRegisterTransport`.

---

## Class Diagram

```
ISettingsSerializer[ModbusConfig]
         │
         └── ModbusConfigSerializer
                   │ serializes ↕
               ModbusConfig           ← dataclass, settings model

IModbusActionService (ABC)
         │
         └── ModbusActionService      ← concrete implementation
```

---

## API Reference

### `ModbusConfig`

**File:** `modbus.py`

Dataclass holding all parameters for a Modbus RTU connection.

```python
@dataclass
class ModbusConfig:
    port: str = 'COM5'
    baudrate: int = 115200
    bytesize: int = 8
    stopbits: int = 1
    parity: str = 'N'
    timeout: float = 0.01
    slave_address: int = 10
    max_retries: int = 30
```

| Method | Signature | Description |
|--------|-----------|-------------|
| `from_dict` | `(data: Dict) → ModbusConfig` | Deserialize from JSON dict |
| `to_dict` | `() → Dict` | Serialize to JSON dict |
| `update_field` | `(field: str, value: Any) → None` | Update a single field by name; raises `ValueError` for unknown fields |

---

### `ModbusConfigSerializer`

**File:** `modbus.py`

Implements `ISettingsSerializer[ModbusConfig]` for JSON persistence.

| Property/Method | Description |
|----------------|-------------|
| `settings_type` | `"modbus_config"` |
| `get_default()` | Returns `ModbusConfig()` with all defaults |
| `to_dict(settings)` | Delegates to `settings.to_dict()` |
| `from_dict(data)` | Delegates to `ModbusConfig.from_dict(data)` |

---

### `IModbusActionService`

**File:** `i_modbus_action_service.py`

Abstract interface for Modbus port operations.

```python
class IModbusActionService(ABC):
    def detect_ports(self) -> List[str]: ...
    def test_connection(self, config: ModbusConfig) -> bool: ...
```

| Method | Returns | Description |
|--------|---------|-------------|
| `detect_ports()` | `List[str]` | Returns available serial port device names (e.g., `["/dev/ttyUSB0"]`) |
| `test_connection(config)` | `bool` | Opens a serial connection with the given config; `True` on success |

---

### `ModbusActionService`

**File:** `modbus_action_service.py`

Concrete implementation using `pyserial`.

```python
class ModbusActionService(IModbusActionService):
    def __init__(self): ...
    def detect_ports(self) -> List[str]: ...
    def test_connection(self, config: ModbusConfig) -> bool: ...
```

- `detect_ports()` calls `serial.tools.list_ports.comports()`. Returns `[]` on failure.
- `test_connection()` opens a `serial.Serial` context manager with the provided config parameters. Returns `False` on any exception.

---

## Multi-Slave Configuration

**File:** `modbus.py`

A single RS-485 port usually carries several slaves. `ModbusConfig` models this
with three layers:

| Layer | Type | Purpose |
|-------|------|---------|
| Default profile | inherited `ModbusConfig` fields | Legacy single-device configuration (`port`, `baudrate`, `slave_address`, …) |
| Connection profiles | `devices: Dict[str, ModbusDeviceConfig]` / `profiles: Dict[str, ModbusDeviceConfig]` | Named serial settings: port + baudrate + framing |
| Slaves | `slaves: Dict[str, ModbusSlaveConfig]` | Slave address + assigned profile + `transport_type` + retry count |

```python
@dataclass
class ModbusSlaveConfig:
    slave_address: int = 10
    profile_name: str = 'default'
    transport_type: str = 'modbus_register'
    max_retries: int = 30
```

`transport_type` is the key into `DEFAULT_TRANSPORT_REGISTRY` — see
[../README.md](../README.md#transportregistry).

### `ModbusConfig` methods

| Method | Signature | Description |
|--------|-----------|-------------|
| `get_profile` | `(name='default', fallback_to_default=False) → ModbusDeviceConfig` | Returns a **copy**, so callers cannot mutate settings. Falls back to `devices` when the name is absent from `profiles`. `name='default'` returns the legacy top-level fields |
| `set_profile` | `(name: str, profile: ModbusDeviceConfig) → None` | Writes to top-level fields for `'default'`, otherwise into `profiles[name]` (deep-copied) |
| `profile_names` | `() → list[str]` | `['default', *names]` — prefers `profiles`, falls back to `devices` |
| `slave_names` | `() → list[str]` | `['default', *names]` — prefers `slaves`, falls back to `devices` |
| `get_slave` | `(name='default') → ModbusSlaveConfig` | Synthesises a default `ModbusSlaveConfig` from top-level fields when `slaves` is empty. Legacy `devices` entries map to `transport_type='xinje_ma_8x8yr'` when the device is named `xinje_ma`, otherwise `'modbus_register'` |
| `set_slave` | `(name: str, slave: ModbusSlaveConfig) → None` | For `'default'` also mirrors `slave_address`/`max_retries` onto the top-level fields |
| `find_slave_name` | `(slave_address: int) → str` | Reverse lookup by numeric address; raises `KeyError` if unconfigured |
| `get_connection` | `(slave_name='default') → ModbusDeviceConfig` | **The resolution step used by transports** — merges the slave's address with its profile's serial settings |
| `update_field` | `(field: str, value: Any) → None` | Updates a top-level field; raises `ValueError` for unknown fields |

---

## `serial_bus.py` — Port Transaction Locking

**File:** `serial_bus.py`

Several configured peripherals may share one RS-485 port. Without
synchronisation, two transports can interleave a request and its response and
corrupt both. This module provides the process-wide lock.

```python
def get_serial_bus_lock(port: str) -> threading.RLock: ...

@contextmanager
def serial_bus_session(port: str, timeout: float): ...
```

- Locks are keyed by **port name** and cached in a module-level dict guarded by
  `_LOCKS_GUARD`; `RLock` is used so re-entrant acquisition from the same thread
  is safe.
- `serial_bus_session` waits up to `max(1.0, timeout * 4.0)` seconds, then
  raises `TimeoutError`.
- `_Session.__enter__` in `modbus_register_transport.py` acquires this session
  around **every** register operation, so per-call transports get atomicity for
  free. Persistent transports take the same lock on each operation.

---

## `ModbusFc16RegisterTransport`

**File:** `modbus_fc16_register_transport.py`

```python
class ModbusFc16RegisterTransport(ModbusRegisterTransport):
    """Standard Modbus RTU registers with FC16 for single-register writes."""

    def write_register(self, address: int, value: int) -> None:
        self.write_registers(address, [value])
```

The whole class body is that one method. The base class defaults
`write_register` → FC6 (write single register); this subclass routes it through
`write_registers` (FC16) instead, for devices whose firmware mishandles FC6.
Registered as `modbus_register_fc16`.

---

## `XinjeMA8X8YRTransport`

**File:** `xinje_ma_8x8yr_transport.py`

Modbus RTU transport for Xinje MA-8X8YR relay / digital I/O modules. Registered
as `xinje_ma_8x8yr`. Inherits `ModbusRegisterTransport` but overrides most write
paths, because the MA module's coil semantics do not match plain registers.

### Address windows

| Window | Function | Notes |
|--------|----------|-------|
| `K128`–`K143` (`_MA_OUTPUT_START`, `_MA_OUTPUT_COUNT = 16`) | **FC15** block write | The whole Y output image is written as one block, guarded by a shadow copy |
| Any other coil address | **FC5** | Single-coil write |
| Explicit `write_register_fc6` | FC6 | Available but not used by `write_register` |
| `read_register` / `read_registers` / `read_input` | **FC1** | MA-8X8YR firmware exposes the X image through FC1; FC2 returns exception code 1 on this module |

### Methods

| Method | Description |
|--------|-------------|
| `write_register(address, value)` | Dispatches to FC15 shadow write inside the MA window, else FC5 |
| `write_registers(address, values)` | Always `write_coils_fc15(address, [1 if v else 0 …])` |
| `write_coil_fc5(address, value)` | Raw single-coil write, bypassing the MA shadow logic |
| `write_coils_fc15(address, values)` | Raw FC15 block write |
| `write_register_fc6(address, value)` | Raw FC6 single-register write |
| `write_registers_fc16(address, values)` | Raw FC16 multi-register write |
| `read_input(address)` | FC1 read of one X point |

### Shadow register state

`_MA_OUTPUT_SHADOWS` is a **module-level dict shared across all transport
instances**, keyed by `(port, slave_address, baudrate, bytesize, parity, stopbits)`.
Each entry is a 16-element list initialised to zeros.

`write_registers` on the base class would otherwise overwrite only part of the
block and switch the other outputs off. Instead `_write_ma_output`:

1. Acquires the port lock
2. Copies the current shadow
3. Applies the single-bit change
4. Writes **all 16** bits as one FC15 block
5. On exception, restores the previous shadow before re-raising

The shadow is intentionally process-global so two separate transport objects for
the same slave still see each other's writes.

### Raw-frame write path

`_write_raw_frame()` builds the PDU by hand, appends a CRC-16 (poly `0xA001`,
init `0xFFFF`), and sends it via `_raw_send()`. This bypasses
`minimalmodbus` for writes because **some USB-RS485 adapters do not reliably
preserve serial line settings through `minimalmodbus`**.

- Up to **3 attempts**, with `write_retry_delay_s` (default `0.02`) between them.
- A `ModbusExceptionResponse` is **not** retried — the slave rejected the
  request, so retrying would be pointless.
- `_write_fd_bounded()` temporarily sets the file descriptor non-blocking and
  uses `select` to bound each partial write by `timeout`, raising
  `SerialTimeoutException` when the deadline passes.
- `_raw_send()` sets `termios` attributes directly: `CLOCAL | CREAD` set,
  `CRTSCTS` cleared, `IGNPAR`/`IXON`/`IXOFF` (`tty_attrs[0]`/`[3]`) cleared, and
  `rts`/`dtr` forced `False`.
- `pyserial.flush()` is deliberately **not** called — on some USB-RS485 drivers
  `tcdrain()` waits indefinitely when the adapter loses line state.
  `write_timeout` already bounds `write()`.
- A fixed `20 ms` settle delay precedes the 8-byte response read.

Response validation (`_validate_response`):

| Check | Result |
|-------|--------|
| Empty response | Accepted silently |
| `response[1] == request[1] \| 0x80` and `response[0] == request[0]` | Raises `ModbusExceptionResponse` with the exception code |
| Fewer than 8 bytes | Raises `RuntimeError("Short Modbus response: …")` |
| Trailing CRC mismatch | Raises `RuntimeError("Bad Modbus response CRC: …")` |

`_normalize_response()` first scans for a 5-byte exception frame at any offset and
re-anchors the buffer to it, since adapters can prepend or append noise bytes.

### `ModbusExceptionResponse`

```python
class ModbusExceptionResponse(RuntimeError):
    """Raised when the Xinje slave returns a Modbus exception response."""
```

Separate from `ModbusExceptionType` — that enum classifies exceptions for
reporting, this is the raw rejection signal used to skip retries.

---

## Data Flow

```
ModbusSettingsApplication
    │
    │  detect_ports()
    │─────────────────────────────► ModbusActionService
    │                                      │
    │                                      │  serial.tools.list_ports.comports()
    │                                      │
    │◄─────────────────────────────────────│  List[str]
    │
    │  test_connection(config)
    │─────────────────────────────► ModbusActionService
    │                                      │
    │                                      │  serial.Serial(port, baudrate, …)
    │                                      │
    │◄─────────────────────────────────────│  bool
```

---

## Usage Example

```python
from src.engine.hardware.communication.modbus.modbus import ModbusConfig
from src.engine.hardware.communication.modbus.modbus_action_service import ModbusActionService

service = ModbusActionService()

# Discover ports
ports = service.detect_ports()   # e.g., ["/dev/ttyUSB0", "/dev/ttyUSB1"]

# Test a specific config
config = ModbusConfig(port="/dev/ttyUSB0", baudrate=115200)
ok = service.test_connection(config)
print("Connected:", ok)
```

---

## Design Notes

- **`pyserial` is a soft dependency** — `detect_ports()` and `test_connection()` each import `serial` inside the function body, so the rest of the platform loads without it installed.
- **No persistent connection** — `test_connection` opens and immediately closes the port. Persistent sessions are managed by application-level Modbus libraries.
- **`ModbusConfigSerializer.settings_type = "modbus_config"`** — this string is the key used when registering the serializer in `SettingsSpec` and retrieving it via `settings_service.get("modbus_config")`.

---

## `ModbusRegisterTransport`

**File:** `modbus_register_transport.py`

Shared Modbus RTU implementation of `IRegisterTransport` via `minimalmodbus`. Used as a base class by device-specific transports:

```python
class ModbusMotorTransport(ModbusRegisterTransport, IMotorTransport): pass
class ModbusGeneratorTransport(ModbusRegisterTransport, IGeneratorTransport): pass
```

Supports both **per-call** (auto-open/close) and **persistent** connections:

| Method | Description |
|--------|-------------|
| `connect()` | Opens persistent session. Logs `DEBUG` with port+slave before attempting, `INFO` on success. |
| `disconnect()` | Closes persistent session. |
| `read_register(address)` | Single register read (functioncode 3). |
| `read_registers(address, count)` | Batch register read. |
| `write_register(address, value)` | Single register write (functioncode 6). |
| `write_registers(address, values)` | Batch register write. |

If `connect()` is not called, each read/write opens and immediately closes a connection via `_session()`.

---

## `ModbusExceptionType`

**File:** `modbus_exception_type.py`

Classifies all Modbus and serial-layer exceptions into a single enum for consistent error handling.

```python
class ModbusExceptionType(Enum):
    MODBUS_EXCEPTION       = "ModbusException"
    INVALID_RESPONSE_ERROR = "InvalidResponseError"
    NO_RESPONSE_ERROR      = "NoResponseError"
    LOCAL_ECHO_ERROR       = "LocalEchoError"
    ILLEGAL_REQUEST_ERROR  = "IllegalRequestError"
    IO_ERROR               = "IOError"
    SERIAL_ERROR           = "SerialException"   ← physical port unavailable/misconfigured
    TIMEOUT_ERROR          = "timeout"
    CONNECTION_ERROR       = "connection"
    CHECKSUM_ERROR         = "Checksum error in rtu mode"
```

`from_exception(exc)` classifies any exception automatically:
- String matches: `"timeout"`, `"connection"`, `"Checksum error in rtu mode"`
- Class name matches: all other enum values are matched against `type(exc).__name__`
- `SERIAL_ERROR` catches `serial.serialutil.SerialException` (port unavailable, errno 5 EIO, etc.)
- Default fallback: `MODBUS_EXCEPTION`

```python
exc_type = ModbusExceptionType.from_exception(exc)
print(exc_type.description())   # "Serial port error — port unavailable or misconfigured"
```
