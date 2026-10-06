# `src/engine/hardware/fan/` — Fan Control

Binary on/off control for extraction and tray fans, driven through the shared
register transport stack.

---

## Files

| File | Contents |
|------|----------|
| `interfaces/i_fan_control.py` | `IFanControl` |
| `modbus/modbus_fan_control.py` | `ModbusFanControl` |
| `modbus/modbus_fan_factory.py` | `build_modbus_fan_control()` |

---

## `IFanControl`

```python
class IFanControl(ABC):
    @abstractmethod
    def turn_on(self) -> None: ...
    @abstractmethod
    def turn_off(self) -> None: ...

    def read_state(self) -> bool:
        """Read the configured hardware output without changing it."""
        raise NotImplementedError
```

`turn_on` / `turn_off` are abstract and return `None` — failures are raised, not
reported through a return value.

`read_state()` is **not** abstract but raises `NotImplementedError` by default.
This is deliberate: existing implementations that predate state reading keep
working, while `build_device_control_adapters()` uses `read_state` as the
`enable_check` and will reject an implementation that cannot answer it.

---

## `ModbusFanControl`

```python
class ModbusFanControl(IFanControl, IHealthCheckable):
    def __init__(
        self,
        transport: IRegisterTransport,
        register: int | str = "Y0",
        on_value: int = 1,
        off_value: int = 0,
    ) -> None: ...
```

| Parameter | Default | Meaning |
|-----------|---------|---------|
| `transport` | — | Any `IRegisterTransport`; `DEFAULT_TRANSPORT_REGISTRY` supplies it in production |
| `register` | `"Y0"` | Output point, resolved through `XinjeMA8X8YR.resolve_output()` |
| `on_value` | `1` | Value written by `turn_on()`, and the value `read_state()` compares against |
| `off_value` | `0` | Value written by `turn_off()` |

`on_value` / `off_value` are configurable because some boards use active-low
outputs.

### Methods

| Method | Behaviour |
|--------|-----------|
| `turn_on()` / `turn_off()` | `write_register(register, on_value/off_value)` |
| `read_state()` | `read_register(register)`, returns `True` when the value equals `on_value` |
| `is_healthy()` | Returns the `_last_operation_ok` flag — **no I/O** |

Every I/O method wraps the transport call in `try/except`, setting
`_last_operation_ok = False` before re-raising, and `True` on success. So a
transport exception propagates to the caller *and* leaves `is_healthy()`
reporting `False`.

### Health semantics

`is_healthy()` is a pure flag read with no register access. It answers "did the
last operation succeed", not "is the fan running". Use `read_state()` when the
actual output state matters — that is blocking I/O.

This makes `ModbusFanControl` safe to use as an availability gate, unlike
`IGeneratorController`, whose `is_healthy()` performs a register read.

---

## `build_modbus_fan_control()`

```python
def build_modbus_fan_control(
    modbus_config: ModbusConfig,
    peripheral_config: PeripheralConfig,
    peripheral_key: str = "fan",
) -> IFanControl | None:
```

Builds a fan controller from settings. Returns `None` when the peripheral key is
not configured, so callers can treat absence as "this site has no fan".

### Resolution steps

```
peripheral_config.peripherals["fan"]        → PeripheralBinding (may be disabled)
  └─ binding.slave_id ──find_slave_name()──► slave_name
       └─ DEFAULT_TRANSPORT_REGISTRY.build_for_slave(modbus_config, slave_name)
            └─ ModbusFanControl(
                   register = binding.outputs.get("fan", "Y0"),
                   on_value = binding.commands.get("on", 1),
                   off_value = binding.commands.get("off", 0),
               )
```

`peripheral_key` defaults to `"fan"`; the tray fan is built by calling this
function again with `peripheral_key="tray_fan"` and an `outputs` entry keyed
`"fan"` in that binding.

### Disabled peripherals are still built

The factory reads `peripheral_config.peripherals.get(peripheral_key)` — the raw
dict — **not** `PeripheralConfig.get()`, which filters out disabled bindings.

This is intentional and commented in the source: Device Control needs the
controller object in order to run the enable check and let the user re-enable a
disabled peripheral. Discarding the controller would make a disabled device
permanently unreachable.

> `find_slave_name()` raises `KeyError` when `binding.slave_id` has no matching
> Modbus slave. Configure the slave before the peripheral binding.

---

## Usage

```python
from src.engine.hardware.communication.modbus.modbus import ModbusConfig
from src.engine.hardware.fan.modbus.modbus_fan_factory import build_modbus_fan_control
from src.engine.hardware.peripherals import PeripheralConfig

modbus_config: ModbusConfig = settings_service.get("modbus_config")
peripheral_config: PeripheralConfig = settings_service.get("peripheral_config")

fan = build_modbus_fan_control(modbus_config, peripheral_config)
tray_fan = build_modbus_fan_control(modbus_config, peripheral_config, "tray_fan")

if fan is not None:
    fan.turn_on()
    print(fan.read_state(), fan.is_healthy())
```

---

## Design Notes

- **Not `IHealthCheckable` at the interface level.** `ModbusFanControl` implements
  it, but `IFanControl` does not require it. Callers that need health should
  check `isinstance(device, IHealthCheckable)` — this is exactly what
  `BinaryDeviceAdapter._cached_health()` does.
- **Two fans, one factory.** The tray fan is a separate peripheral binding, not a
  special case in the implementation.
- **Wired through `peripherals`.** Both the register label and the on/off values
  come from `PeripheralBinding`, so hardware differences are settings-only.

<!-- source-navigation:start -->
## Source navigation

[Module reference](MODULES.md) — signatures, fields, imports and source links for every Python file in this directory.

| Source subdirectory | Guide |
|---|---|
| `interfaces/` | [interfaces](interfaces/README.md) |
| `modbus/` | [modbus](modbus/README.md) |

[Complete source index](../../../SOURCE_INDEX.md).
<!-- source-navigation:end -->
