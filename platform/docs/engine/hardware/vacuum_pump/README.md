# `src/engine/hardware/vacuum_pump/` — Vacuum Pump

Interface contracts **and** a full Modbus implementation for vacuum-pump control,
including the optional blow-off pulse.

---

## Files

| File | Contents |
|------|----------|
| `interfaces/i_vacuum_pump_controller.py` | `IVacuumPumpController` ABC |
| `interfaces/i_vacuum_pump_transport.py` | `IVacuumPumpTransport` semantic alias |
| `models/vacuum_pump_config.py` | `VacuumPumpConfig` frozen dataclass |
| `vacuum_pump_controller.py` | `VacuumPumpController` — engine-level concrete controller |
| `modbus/modbus_vacuum_pump_transport.py` | `ModbusVacuumPumpTransport` |
| `modbus/modbus_vacuum_pump_factory.py` | `build_modbus_vacuum_pump_controller()` |
| `mock_runner.py` | `MockVacuumPumpTransport` + three CLI scenarios |
| `__init__.py` | Exports the two interfaces, `VacuumPumpConfig`, `VacuumPumpController` |

---

## Interfaces

### `IVacuumPumpController`

```python
class IVacuumPumpController(ABC):
    @abstractmethod
    def turn_on(self) -> bool: ...
    @abstractmethod
    def turn_off(self) -> bool: ...

    def turn_off_nonblocking(self) -> bool:
        """Turn the pump off without waiting for an optional blow-off pulse.

        Controllers without asynchronous pulse support retain the safe,
        blocking behavior."""
        return self.turn_off()

    def read_state(self) -> bool:
        """Read the configured hardware output without changing it."""
        raise NotImplementedError

    def close(self) -> None:
        """Release any transport resources held by the controller."""
```

High-level controller interface. Commands return `True` on success, `False` on
failure. Consumed by `IDeviceControlService` in the `device_control` application
and by the paint/glue production services.

| Method | Contract |
|--------|----------|
| `turn_off()` | Waits for the configured blow-off pulse to finish |
| `turn_off_nonblocking()` | Returns after vacuum is disabled and blow-off is activated; supporting controllers close the blow-off valve in the background. **Default implementation falls back to `turn_off()`** — safe, blocking behaviour for controllers without async support |
| `read_state()` | Base raises `NotImplementedError`; override only when the hardware can answer |
| `close()` | Releases transport resources; calling it safely cancels a pending background pulse |
| `turn_on()` | Cancels a pending background pulse first |

### `IVacuumPumpTransport`

```python
class IVacuumPumpTransport(IRegisterTransport):
    """Semantic type alias — constrains injection sites to vacuum-pump-specific
    transports. All register I/O contract is inherited from IRegisterTransport."""
```

Adds no methods. It exists so injection sites are typed to vacuum-pump transports
rather than any register transport.

---

## `VacuumPumpConfig` (frozen)

```python
pump_register: int | str = "Y0"
on_value: int = 1
off_value: int = 0
blow_off_register: int | str | None = None   # None → no blow-off
blow_off_on_value: int = 1
blow_off_off_value: int = 0
blow_off_pulse_seconds: float = 0.0          # 0 → close immediately, no Timer
```

---

## `VacuumPumpController`

> High-level vacuum-pump controller. Implements turn-on/turn-off commands with
> optional blow-off pulse. Writes to a single coil/register via the injected
> transport.

```python
VacuumPumpController(
    transport: IVacuumPumpTransport,
    config: VacuumPumpConfig | None = None,   # defaults to VacuumPumpConfig()
)
```

Also implements `IHealthCheckable`.

Register names are resolved at construction through
`XinjeMA8X8YR.resolve_output(...)`; `blow_off_register=None` stays `None`.

### Synchronisation

| Member | Role |
|--------|------|
| `_blow_off_lock: threading.RLock` | Guards pump + blow-off register writes and timer state |
| `_blow_off_timer: threading.Timer \| None` | Pending background pulse |
| `_blow_off_generation: int` | Generation counter — every cancel increments it |

`_finish_blow_off_async(register, generation)` takes the lock and **returns
immediately if `generation != _blow_off_generation`**, so a cancelled timer that
still fires cannot close a valve that a newer `turn_on()` just re-opened.

### Commands

| Method | Behaviour |
|--------|-----------|
| `turn_on() -> bool` | Cancels any pending pulse (`_cancel_pending_blow_off_locked`), closes the blow-off register first if configured (`_close_blow_off`), then writes `on_value` |
| `turn_off() -> bool` | Writes `off_value`, then `_pulse_blow_off()` — writes `blow_off_on_value`, sleeps `blow_off_pulse_seconds`, writes `blow_off_off_value`. Returns `False` if either step fails |
| `turn_off_nonblocking() -> bool` | Cancels pending pulse, writes `off_value`, writes `blow_off_on_value`. With `pulse_seconds == 0` it closes immediately; otherwise starts a **daemon** `threading.Timer` and returns |
| `read_state() -> bool` | Reads the pump register, compares to `on_value`; exceptions set `_last_operation_ok = False` and re-raise |
| `close()` | Cancels a pending pulse (closing the valve if one was pending), then `transport.disconnect()`, and clears `_last_operation_ok` |
| `is_healthy() -> bool` | Backed by `_last_operation_ok` — the **last operation** result, no I/O |

Helpers: `_write_pump(value, label)` (catch-all → `False`), `_pulse_blow_off()`,
`_close_blow_off()`, `_cancel_pending_blow_off_locked()`,
`_finish_blow_off_locked(register)`.

---

## `modbus/`

### `ModbusVacuumPumpTransport`

```python
class ModbusVacuumPumpTransport(XinjeMA8X8YRTransport, IVacuumPumpTransport):
    """Backward-compatible vacuum-pump view of the Xinje MA transport.

    The protocol implementation belongs to the shared communication layer;
    this name remains for existing vacuum-pump callers and integrations."""
```

**No method bodies** — it is exactly the pattern required by the platform rule
for new Modbus device transports: inherit `ModbusRegisterTransport` (via
`XinjeMA8X8YRTransport`) and the semantic device interface, docstring only.

The module re-exports `ModbusExceptionResponse` and `_crc16` for existing
callers.

### `build_modbus_vacuum_pump_controller(modbus_config, vacuum_config=None, profile_name="default")`

Returns `IVacuumPumpController`.

```
if modbus_config has get_slave:                       # multi-slave / registry path
    transport = DEFAULT_TRANSPORT_REGISTRY.build_for_slave(modbus_config, profile_name)
else:                                                # legacy single-port path
    transport = ModbusVacuumPumpTransport(port, slave_address, baudrate,
                                          bytesize, stopbits, parity, timeout)
return VacuumPumpController(transport, vacuum_config or VacuumPumpConfig())
```

The registry branch supports `ModbusSlaveConfig`; the fallback keeps legacy
single-port `ModbusConfig` objects working. Import of
`DEFAULT_TRANSPORT_REGISTRY` is deferred inside the function.

---

## `mock_runner.py`

`MockVacuumPumpTransport` implements `read_register` / `write_register` in memory,
plus three runnable scenarios:

| Scenario | What it exercises |
|----------|-------------------|
| `scenario_turn_on_off()` | Basic ON/OFF writes |
| `scenario_blow_off_pulse()` | The blow-off pulse sequence |
| `scenario_transport_failure()` | A raising transport, confirming `False` rather than an exception |

It is not referenced by production code — a local verification tool, in the same
spirit as `hardware/generator/mock_runner.py` and `hardware/motor/mock_runner.py`.

---

## Consumers

| Consumer | Usage |
|----------|-------|
| `src/robot_systems/paint/service_builders.py` | Calls `build_modbus_vacuum_pump_controller(...)` |
| `src/robot_systems/paint/paint_robot_system.py` | Declares `service_type=IVacuumPumpController` |
| `src/robot_systems/paint/processes/paint/paint_production_service.py` | Optional `vacuum_pump` dependency |
| `src/robot_systems/glue/glue_robot_system.py` | Declares `service_type=IVacuumPumpController` |
| `src/robot_systems/glue/service_builders.py` | Wires **glue's own** `src.robot_systems.glue.domain.vacuum_pump.VacuumPumpController` — a different class implementing the same interface |
| `src/robot_systems/glue/processes/pick_and_place*` | Consumes the interface |

---

## Design Notes

- **Interface + shared implementation.** Unlike the laser (interface only), this
  package ships a usable `VacuumPumpController`; robot systems may still provide
  their own (glue does).
- **Blocking vs non-blocking is a controller capability, not a caller choice.**
  The base class defaults `turn_off_nonblocking()` to the blocking `turn_off()`,
  so an implementation that cannot do async keeps the safe behaviour.
- **Generation counter over timer identity.** Comparing `_blow_off_generation`
  is cheaper and safer than reasoning about `Timer` objects that may already be
  firing on another thread.
- **Health is "last operation", not a probe.** Same semantics as
  `ModbusLaserControl` — neither performs I/O from `is_healthy()`.
