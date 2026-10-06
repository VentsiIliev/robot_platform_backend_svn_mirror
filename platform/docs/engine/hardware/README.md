# `src/engine/hardware/` — Hardware Overview

The `hardware` package provides drivers and service abstractions for physical I/O devices connected to the robot platform. All hardware modules publish events through `IMessagingService` rather than exposing direct callbacks to consumers.

---

## Subpackages

```
hardware/
├── communication/           ← Register transport layer (base of every device below)
│   ├── i_register_transport.py   ← IRegisterTransport ABC
│   ├── transport_registry.py     ← TransportRegistry, DEFAULT_TRANSPORT_REGISTRY
│   ├── live_register_transport.py
│   └── modbus/                   ← Serial port detection, Modbus RTU transports
├── xinje/                  ← XinjeMA8X8YR I/O address map (symbolic X/Y point names)
├── peripherals/            ← PeripheralBinding settings + Device Control adapters
├── motor/                  ← Motor controller service (IMotorService, MotorConfig, health checker)
├── weight/
│   ├── interfaces/         ← ICellTransport, ICellCalibrator, IWeightCellService
│   ├── http/               ← HTTP-based transport implementation
│   ├── weight_cell_service.py
│   └── config.py
├── generator/              ← Generator controller service
├── laser/                  ← ILaserControl + ModbusLaserControl
├── vacuum_pump/            ← IVacuumPumpController + VacuumPumpController
├── vacuum_sensor/          ← IVacuumSensorService + VacuumSensorService
├── fan/                    ← IFanControl + ModbusFanControl
├── dryer/                  ← IDryerService + DryerService/DryerController
├── physical_control_buttons/ ← Physical panel inputs and indicator outputs
```

---

## Subsystem Overview

### Register transport (`communication/`)

The protocol-agnostic `IRegisterTransport` contract — `read_register` is the only
abstract method, the other four register operations have working defaults.
`TransportRegistry` selects which concrete transport backs a Modbus slave from
settings, and `LiveRegisterTransport` rebuilds a transport from live settings on
each call.

→ See [communication/README.md](communication/README.md)

### Modbus (`communication/modbus/`)

The RTU implementation of that contract. Handles **serial port enumeration**,
**connection testing**, per-port transaction locking (`serial_bus.py`), and the
shared `ModbusRegisterTransport` base class. `ModbusExceptionType` classifies all
transport-level errors including `SerialException`.

→ See [communication/modbus/README.md](communication/modbus/README.md)

### Xinje address map (`xinje/`)

`XinjeMA8X8YR` maps symbolic point names (`"X3"`, `"Y5"`) to Modbus addresses
(`X0..X7` → 0..7, `Y0..Y7` → 128..135). Used by laser, fan, vacuum pump, vacuum
sensor, and physical control buttons so register numbers never appear in settings.

→ See [xinje/README.md](xinje/README.md)

### Peripherals (`peripherals/`)

Two halves: `PeripheralConfig` — settings mapping logical device names to slave
IDs, register labels, and command codes — and the `Device Control` adapters
(`BinaryDeviceAdapter`, `VacuumSensorDeviceAdapter`,
`PhysicalButtonsDeviceAdapter`, `DryerDeviceAdapter`) that give heterogeneous
devices one uniform surface.

→ See [peripherals/README.md](peripherals/README.md)

### Motor (`motor/`)

Manages motor controller boards over any `IMotorTransport`. Provides `IMotorService` (extends `IHealthCheckable`), `MotorConfig` (register map + motor topology), `MotorHealthChecker`, and a Modbus RTU factory.

- `is_healthy()` — serial connection state (fast, no I/O)
- `health_check(addr)` — per-motor board error query (does I/O)
- `health_check_all_configured()` — all motors declared in `MotorConfig.motor_addresses`

Error code decoding is **not** part of this layer — inject an `IMotorErrorDecoder` from the robot system that owns the board.

→ See [motor/README.md](motor/README.md)

### Weight Cells (`weight/`)

Manages one or more weight measurement cells. Each cell runs an independent daemon thread that connects via HTTP, reads weight values, and publishes them to the messaging bus. Auto-reconnects after errors.

→ See [weight/README.md](weight/README.md)

### Generator (`generator/`)

Provides a relay on/off controller for generator hardware (`IGeneratorController`). Reads back hardware state from a status register and optionally tracks run time with a configurable timeout callback. All transport exceptions are caught internally — callers never receive a raised exception.

- `turn_on()` / `turn_off()` — write to relay register; return `bool` success
- `get_state()` → `GeneratorState` — `is_on`, `is_healthy`, `elapsed_seconds`, `communication_errors`
- `GeneratorTimer` — background daemon thread; fires `on_timeout` when `timeout_minutes` elapses
- `NullGeneratorTimer` — no-op used when timeout tracking is not needed

→ See [generator/README.md](generator/README.md)

### Laser (`laser/`)

`ILaserControl` (`turn_on()` / `turn_off()`) plus the engine-level
`ModbusLaserControl`, which resolves an output point through `XinjeMA8X8YR`
(default `"Y5"`) and implements `IHealthCheckable`. Robot systems may supply their
own implementation via `RobotSystemHeightMeasuringProvider.build_laser_control()`.
Used by `LaserDetectionService` in the height-measuring subsystem.

→ See [laser/README.md](laser/README.md)

### Vacuum Pump (`vacuum_pump/`)

`IVacuumPumpController` (`turn_on() -> bool`, `turn_off() -> bool`) for high-level
vacuum control with an optional blow-off pulse, and `IVacuumPumpTransport`
(semantic subtype of `IRegisterTransport`) for the hardware transport layer. The
engine ships `VacuumPumpController`, `ModbusVacuumPumpTransport`, and
`build_modbus_vacuum_pump_controller()`.

→ See [vacuum_pump/README.md](vacuum_pump/README.md)

### Vacuum Sensor (`vacuum_sensor/`)

`IVacuumSensorService.is_vacuum_detected()` — one question, fail-safe: a read
failure reports "no vacuum" and sets `is_healthy() = False`. Retries with
automatic transport reconnect, exposes `get_read_diagnostics()`.

→ See [vacuum_sensor/README.md](vacuum_sensor/README.md)

### Fan (`fan/`)

`IFanControl` / `ModbusFanControl` — binary fan control through a configured
peripheral binding. `is_healthy()` is a pure flag (no I/O); `read_state()` does
the register read. The Modbus factory defaults to the `fan` binding and accepts a
different peripheral key when a robot system has multiple independently
addressed fans (`tray_fan`).

→ See [fan/README.md](fan/README.md)

### Dryer (`dryer/`)

The most stateful peripheral: `IDryerService` owns an enable/disable lifecycle
(generation counter, optional async init thread) while `DryerController` writes a
contiguous 17-register FC16 block. `NEXT_POSITION` and `EJECT` verify command
acceptance from status instead of retrying blindly, so physical motion is never
duplicated.

→ See [dryer/README.md](dryer/README.md)

### Physical Control Buttons (`physical_control_buttons/`)

`IPhysicalControlButtons` reads panel inputs and drives indicator outputs by
symbolic name. `ModbusPhysicalControlButtons` implements it (with an `IHealthCheckable`
flag), and `build_modbus_physical_control_buttons()` wires it from a peripheral
binding.

→ See [physical_control_buttons/README.md](physical_control_buttons/README.md)

---

## Integration Pattern

Hardware services are registered via `ServiceSpec` in `BaseRobotSystem.services` with a `builder` function. If a hardware device is unavailable at startup, the platform continues running — `is_healthy()` returns `False` and the health registry tracks it.

```python
# In GlueRobotSystem:
services = [
    ServiceSpec(
        name         = "motor",
        service_type = IMotorService,
        required     = True,
        description  = "Glue pump motor service",
        builder      = _build_motor_service,
    ),
    ServiceSpec(
        name         = "weight",
        service_type = IWeightCellService,
        required     = True,
        builder      = _build_weight_cell_service,
    ),
]
```

<!-- source-navigation:start -->
## Source navigation

[Module reference](MODULES.md) — signatures, fields, imports and source links for every Python file in this directory.

| Source subdirectory | Guide |
|---|---|
| `communication/` | [communication](communication/README.md) |
| `dryer/` | [dryer](dryer/README.md) |
| `fan/` | [fan](fan/README.md) |
| `generator/` | [generator](generator/README.md) |
| `laser/` | [laser](laser/README.md) |
| `motor/` | [motor](motor/README.md) |
| `peripherals/` | [peripherals](peripherals/README.md) |
| `physical_control_buttons/` | [physical_control_buttons](physical_control_buttons/README.md) |
| `vacuum_pump/` | [vacuum_pump](vacuum_pump/README.md) |
| `vacuum_sensor/` | [vacuum_sensor](vacuum_sensor/README.md) |
| `weight/` | [weight](weight/README.md) |
| `xinje/` | [xinje](xinje/README.md) |

[Complete source index](../../SOURCE_INDEX.md).
<!-- source-navigation:end -->
