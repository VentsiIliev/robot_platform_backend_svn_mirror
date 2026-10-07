# `src/engine/hardware/vacuum_sensor/` — Vacuum Sensor

Answers a single question: **is vacuum currently detected?**

`IVacuumSensorService` is communication-agnostic, so the same consumer code works
over Modbus RTU, discrete I/O, or a simulated transport.

---

## Files

| File | Contents |
|------|----------|
| `interfaces/i_vacuum_sensor_service.py` | `IVacuumSensorService` |
| `interfaces/i_vacuum_sensor_transport.py` | `IVacuumSensorTransport` |
| `models/vacuum_sensor_config.py` | `VacuumSensorConfig` |
| `vacuum_sensor_service.py` | `VacuumSensorService` |
| `modbus/modbus_vacuum_sensor_transport.py` | `ModbusVacuumSensorTransport` |
| `modbus/modbus_vacuum_sensor_factory.py` | `build_modbus_vacuum_sensor_service()` |
| `dummy_vacuum_sensor_transport.py` | `DummyVacuumSensorTransport` |
| `mock_runner.py` | Standalone simulator runner for manual testing |

---

## Interfaces

### `IVacuumSensorService`

```python
class IVacuumSensorService(IHealthCheckable):
    @abstractmethod
    def is_vacuum_detected(self) -> bool: ...
```

Extends `IHealthCheckable`, so health comes for free. The contract is explicit
about failure:

> A read failure is treated as "no vacuum" (fail-safe). Implementations should
> update the health flag reported by `is_healthy()` on every read.

A broken sensor therefore reports `False` (nothing detected) rather than raising
into the process, and callers distinguish "confirmed empty" from "sensor dead" by
also checking `is_healthy()`.

### `IVacuumSensorTransport`

```python
class IVacuumSensorTransport(IRegisterTransport):
    """Semantic type alias — constrains injection sites to vacuum-sensor transports."""
```

No methods added — it exists so a vacuum-sensor controller cannot be handed a
motor transport by mistake.

Optionally, a transport may implement `read_input(address) -> int` as an
alternative to `read_register`. The service probes for it with `getattr` before
each read; see *Register resolution* below.

---

## `VacuumSensorConfig`

```python
@dataclass(frozen=True)
class VacuumSensorConfig:
    sensor_register: int | str
    detected_value: int = 1
    read_retries: int = 3
```

| Field | Default | Meaning |
|-------|---------|---------|
| `sensor_register` | — (required) | Modbus address **or** Xinje MA point label. Both `3` and `"X3"` are accepted |
| `detected_value` | `1` | Raw value meaning "vacuum present". Active-high: `1`. Active-low: `0` |
| `read_retries` | `3` | Read attempts before the call is reported as failed |

The frozen dataclass keeps configuration immutable across the persistent
connection it configures.

---

## `VacuumSensorService`

```python
class VacuumSensorService(IVacuumSensorService):
    def __init__(self, transport: IVacuumSensorTransport, config: VacuumSensorConfig) -> None: ...
```

### Register resolution

The direction is chosen from the **point name**, not a config flag:

```python
point = config.sensor_register
self._reads_input = isinstance(point, str) and point.strip().upper().startswith("X")
self._sensor_register = (
    XinjeMA8X8YR.resolve_input(point)  if self._reads_input
    else XinjeMA8X8YR.resolve_output(point)
)
```

A label beginning with `X` is a Xinje input point, anything else is resolved as
an output (raw integers fall through the address map unchanged). The flag is
computed **once, in the constructor**, and also decides which read method is
used:

```python
read_input = getattr(self._transport, "read_input", None)
raw = (read_input(self._sensor_register)
       if self._reads_input and read_input is not None
       else self._transport.read_register(self._sensor_register))
```

### `is_vacuum_detected()` — retry loop

```
for attempt in range(config.read_retries):
    try:
        raw = <read via read_input or read_register>
    except Exception:
        failed_attempts += 1
        last_error = "ExcType: message"
        if this was the last attempt:   log the exception
        else:                           _reconnect_transport()
        continue                        ← read failed → not detected (fail-safe)

    health = True
    last_raw_value = raw
    return raw == config.detected_value

# exhausted all retries
health = False
return False
```

Notable properties:

- **Failure is never raised.** Every exception is consumed and converted to
  `False`. The exception is logged only on the **final** attempt, so a transient
  glitch does not spam the log.
- **Intermediate failures trigger `_reconnect_transport()`** —
  `transport.disconnect()` then `connect()`, which reopens the persistent
  session. This is the recovery path for a dropped link.
- **`detected_value` is compared, not truth-tested.** `0` as `detected_value` is a
  valid active-low sensor.

### Retries are logged with detail

Each attempt records its duration in milliseconds, and the overall call records
start/finish monotonic nanoseconds. Diagnostics are always gathered, not only on
failure.

### `get_read_diagnostics()`

Returns a snapshot dict of the last read **without performing I/O** — safe to call
from a UI thread:

| Key | Type | Meaning |
|-----|------|---------|
| `sequence` | `int` | Monotonic read-call counter |
| `started_monotonic_ns` / `finished_monotonic_ns` | `int` | Call timing |
| `duration_ms` | `float` | Whole-call duration |
| `success` | `bool` | Whether the read completed |
| `detected` | `bool` | Result of that read |
| `raw_value` | `int \| None` | Raw register value, `None` on failure |
| `attempts` / `failed_attempts` | `int` | Retry accounting for this call |
| `attempt_durations_ms` | `list[float]` | Per-attempt timing, copied on read |
| `last_error` | `str \| None` | `"ExcType: message"` from the last failure |
| `total_read_calls` / `total_read_attempts` / `total_failed_attempts` / `total_failed_calls` | `int` | Lifetime counters |

`attempt_durations_ms` is deep-copied in the snapshot so callers cannot mutate
the stored list.

### Connection lifecycle

| Method | Behaviour |
|--------|-----------|
| `__init__` | Calls `_connect_transport()` — opens the persistent session at construction |
| `close()` | `transport.disconnect()` |
| `_reconnect_transport()` | `disconnect()` + `connect()`, called on an intermediate read failure |

The service uses a **persistent** connection (`connect()` once at start) rather
than reopening per read, which is why reconnect-on-failure is the correct
recovery rather than "just try again".

### Logging

Debug output logs at most **once per second** per distinct state:

```python
if state != self._last_logged_state or now - self._last_log_at >= 1.0:
    _logger.debug("Vacuum sensor register=%d raw=%d -> detected=%s", ...)
```

State changes always log; unchanged states rate-limit.

### Health

```python
def is_healthy(self) -> bool:
    """True when the last sensor read succeeded. No I/O."""
    return self._last_read_ok
```

Pure flag read — safe as an availability gate.

`last_raw_value` is exposed as a read-only property returning the most recent
successful raw value, or `None` if there has been none. The Device Control
adapter surfaces it as `"raw"`.

---

## `ModbusVacuumSensorTransport`

```python
class ModbusVacuumSensorTransport(ModbusRegisterTransport, IVacuumSensorTransport):
    def read_register(self, address: int) -> int:
        with self._session() as inst:
            return int(inst.read_bit(address, functioncode=1))
```

One override: the sensor output is read as a **coil (FC1)** rather than a holding
register (FC3). This mirrors the vacuum-pump transport used on the same relay-board
family.

The docstring records the escape hatch: override `read_register` again if the
sensor sits on a discrete input (FC2) or a holding register instead.

---

## `build_modbus_vacuum_sensor_service()`

```python
def build_modbus_vacuum_sensor_service(
    modbus_config: ModbusConfig,
    sensor_config: VacuumSensorConfig,
) -> IVacuumSensorService:
```

Builds `ModbusVacuumSensorTransport` from the **top-level** `modbus_config`
fields (`port`, `slave_address`, `baudrate`, `bytesize`, `stopbits`, `parity`,
`timeout`) and wraps it in a `VacuumSensorService`.

> This factory reads the legacy top-level profile, not
> `DEFAULT_TRANSPORT_REGISTRY.build_for_slave()`. Unlike the fan and
> physical-buttons factories it does not consult `PeripheralBinding`, so it cannot
> express a slave or `transport_type` through peripheral settings.

Always returns a service — it never returns `None`, because the vacuum sensor is
not optional at this call site. Callers decide whether to use it.

---

## `DummyVacuumSensorTransport`

A deterministic double for tests and manual simulation:

```python
class DummyVacuumSensorTransport(IVacuumSensorTransport):
    def __init__(self, simulated_value: int = 0) -> None: ...
```

| Attribute / method | Purpose |
|--------------------|---------|
| `simulated_value: int` | Value returned by `read_register()` |
| `raise_on_read: bool` | `True` → every read raises `IOError`, simulating a dead sensor |
| `call_log: list` | `(method, address, value)` tuples recorded under a lock |
| `set_simulated_value(value)` | Change the returned value |
| `set_vacuum_detected(detected, *, detected_value=1, clear_value=0)` | Convenience: set `simulated_value` to the detected/clear code |

Every read logs `[DUMMY VACUUM SENSOR] read_register(addr=%d) -> %d` (or `-> RAISED`)
so the request stream is observable. `connect()` and `disconnect()` are inherited
no-ops from `IRegisterTransport`.

### `mock_runner.py`

A standalone process for driving the dummy transport outside the GUI — useful for
exercising consumers against simulated vacuum transitions without hardware.

---

## Usage

```python
from src.engine.hardware.vacuum_sensor.modbus.modbus_vacuum_sensor_factory import (
    build_modbus_vacuum_sensor_service,
)
from src.engine.hardware.vacuum_sensor.models.vacuum_sensor_config import VacuumSensorConfig

sensor = build_modbus_vacuum_sensor_service(
    modbus_config,
    VacuumSensorConfig(sensor_register="X3", detected_value=1, read_retries=3),
)

if not sensor.is_vacuum_detected() and not sensor.is_healthy():
    print("Sensor read failed — reporting no vacuum as a safety default")

print(sensor.get_read_diagnostics())
sensor.close()
```

---

## Design Notes

- **Fail-safe by default.** Every failure path yields "not detected"; health is
  reported separately so callers can tell a genuine empty result from a broken
  sensor.
- **Reconnect on intermediate failure, log only on the last.** Recovery is
  automatic, diagnostics are not noisy.
- **Resolution happens once.** Register direction and address are computed in the
  constructor, so a bad point name fails at startup rather than on first use.
- **`detected_value` is compared to the raw reading**, so active-low sensors are
  first-class — set `detected_value=0` and nothing else changes.

<!-- source-navigation:start -->
## Source navigation

[Module reference](MODULES.md) — signatures, fields, imports and source links for every Python file in this directory.

| Source subdirectory | Guide |
|---|---|
| `interfaces/` | [interfaces](interfaces/README.md) |
| `modbus/` | [modbus](modbus/README.md) |
| `models/` | [models](models/README.md) |

[Complete source index](../../../SOURCE_INDEX.md).
<!-- source-navigation:end -->

Sensor binding inputs/outputs support directly constructed integer addresses and string addresses/labels. Sensor selection gives input precedence and falls back to output only when input is absent (`None`); integer zero is preserved. Saved bindings retain existing deserialization into strings, so persisted numeric zero continues to become `"0"`. Paint sensor construction and the sensor runner use the same precedence.
