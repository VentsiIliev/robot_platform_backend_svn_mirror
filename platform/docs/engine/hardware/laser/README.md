# `src/engine/hardware/laser/` — Laser Control

Binary on/off control for a hardware laser, with a Modbus implementation.

---

## Files

| File | Contents |
|------|----------|
| `i_laser_control.py` | `ILaserControl` ABC |
| `modbus_laser_control.py` | `ModbusLaserControl` — register/coil implementation |
| `__init__.py` | Exports `ILaserControl`, `ModbusLaserControl` |

---

## `ILaserControl`

```python
class ILaserControl(ABC):
    @abstractmethod
    def turn_on(self) -> None: ...
    @abstractmethod
    def turn_off(self) -> None: ...
```

Hardware-agnostic contract for activating and deactivating the laser. Consumed
by `LaserDetectionService` in `src/engine/robot/height_measuring/`.

The interface is intentionally minimal — no state query, no intensity control —
because all known robot systems require only binary on/off.

---

## `ModbusLaserControl`

```python
class ModbusLaserControl(ILaserControl, IHealthCheckable):
    def __init__(
        self,
        transport: IRegisterTransport,
        register: int | str = "Y5",
        on_value: int = 1,
        off_value: int = 0,
    ) -> None: ...
```

> Laser control through a register/coil transport.

- The register is resolved through `XinjeMA8X8YR.resolve_output(register)`, so a
  symbolic name such as `"Y5"` and a raw address both work
- `turn_on()` / `turn_off()` write `on_value` / `off_value` and return nothing
- `read_state() -> bool` reads the register back and compares against `on_value`
- Both write and read set `_last_operation_ok` — set on success, cleared (and the
  exception re-raised) on failure — and that flag backs
  `is_healthy() -> bool`

`is_healthy()` therefore reflects **the last operation**, not live I/O: it does
not poll the device.

---

## Injection Point

`RobotSystemHeightMeasuringProvider.build_laser_control()` is where the interface
is normally constructed; see `docs/engine/robot/height_measuring/README.md`.
Concrete robot systems may still supply their own `ILaserControl` instead —
`ModbusLaserControl` is the shared default, not a forced choice.

`tests/robot_systems/paint/test_paint_runtime_services.py::TestModbusLaserControl`
covers it with a stub transport.

---

## Design Notes

- **Transport in, no protocol here.** The class only calls
  `IRegisterTransport.read_register` / `write_register`; the Modbus framing lives
  in `hardware/communication/`.
- **Two interfaces, two roles.** `ILaserControl` is what consumers see;
  `IHealthCheckable` is what `ServiceHealthRegistry` detects automatically.
- **Semantic alias transports** (`IMotorTransport`, `IGeneratorTransport`,
  `IVacuumPumpTransport`) exist for other devices; the laser deliberately takes
  the base `IRegisterTransport` because it needs nothing more than one write.
