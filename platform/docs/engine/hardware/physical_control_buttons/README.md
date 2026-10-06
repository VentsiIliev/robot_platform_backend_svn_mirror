# `src/engine/hardware/physical_control_buttons/` — Physical Control Buttons

Reads and drives the physical buttons on the machine — start, stop, reset, and
similar panel controls wired to digital I/O.

Buttons are **bidirectional**. Inputs report what the operator pressed; outputs
let software drive indicator lamps or emulate a press, which is how a GUI button
can light the same LED the physical button does.

---

## Files

| File | Contents |
|------|----------|
| `interfaces/i_physical_control_buttons.py` | `IPhysicalControlButtons` |
| `modbus/modbus_physical_control_buttons.py` | `ModbusPhysicalControlButtons` |
| `modbus/modbus_physical_control_buttons_factory.py` | `build_modbus_physical_control_buttons()` |

---

## `IPhysicalControlButtons`

```python
class IPhysicalControlButtons(ABC):
    """Read the state of physical machine control buttons."""

    @abstractmethod
    def read_states(self) -> Mapping[str, bool]: ...

    @abstractmethod
    def is_pressed(self, button: str) -> bool: ...

    @abstractmethod
    def set_button(self, button: str, pressed: bool) -> None: ...

    @abstractmethod
    def read_output_states(self) -> Mapping[str, bool]: ...
```

| Method | Returns | Purpose |
|--------|---------|---------|
| `read_states()` | `Mapping[str, bool]` | All configured **inputs**, one read each |
| `is_pressed(button)` | `bool` | One named input |
| `set_button(button, pressed)` | `None` | Drive the **output** paired with `button` |
| `read_output_states()` | `Mapping[str, bool]` | All configured outputs |

`read_states` reads each input individually rather than as a block, so button
count stays small and register layout stays simple.

---

## `ModbusPhysicalControlButtons`

```python
class ModbusPhysicalControlButtons(IPhysicalControlButtons, IHealthCheckable):
    def __init__(
        self,
        transport: IRegisterTransport,
        inputs: dict[str, int | str],
        outputs: dict[str, int | str] | None = None,
    ) -> None: ...
```

Addresses are resolved eagerly in the constructor:

```python
self._inputs  = {name: XinjeMA8X8YR.resolve_input(address)  for name, address in inputs.items()}
self._outputs = {name: XinjeMA8X8YR.resolve_output(address) for name, address in (outputs or {}).items()}
```

An unknown point name raises `ValueError` from the address map at construction
time rather than on the first button press.

### Methods

| Method | Behaviour |
|--------|-----------|
| `read_states()` | `{name: self._read_input(addr)}` for every configured input |
| `is_pressed(button)` | Reads one input. `KeyError` → `f"Unknown physical control button: {button}"` |
| `set_button(button, pressed)` | Writes `1`/`0` to the paired output. `KeyError` → `f"No output configured for physical control button: {button}"` |
| `read_output_states()` | Reads every configured output, logging each read |
| `is_healthy()` | Returns `_last_operation_ok` — **no I/O** |

`set_button()` logs at `INFO` before writing (`"Writing physical button output %s
address=%d value=%d"`), because panel output changes are a common source of
support questions and the log is the only record of which side moved what.

`read_output_states()` also logs each read at `INFO`. This is noisier than typical
engine code, but the input/output asymmetry is hard to debug without it.

### Input read fallback

```python
def _read_input(self, address: int) -> bool:
    read_input = getattr(self._transport, "read_input", None)
    return bool(read_input(address) if read_input else self._transport.read_register(address))
```

Some transports — notably `XinjeMA8X8YRTransport` — expose `read_input()` because
the module serves its X image over FC1 while plain `read_register()` would use
FC3. The `getattr` probe keeps this class working with any `IRegisterTransport`,
including plain Modbus registers and test doubles.

### Health semantics

Every I/O method sets `_last_operation_ok = False` before re-raising, and `True`
on success. `is_healthy()` is a pure flag read.

---

## `build_modbus_physical_control_buttons()`

```python
def build_modbus_physical_control_buttons(
    modbus_config: ModbusConfig,
    peripheral_config: PeripheralConfig,
) -> IPhysicalControlButtons | None:
```

Returns `None` when the `physical_control_buttons` binding is missing **or** has
no `inputs` — a binding with only outputs describes nothing readable, so there is
no point constructing a controller.

Resolution:

```
peripheral_config.peripherals["physical_control_buttons"]
  ├─ binding.inputs must be non-empty, else None
  └─ binding.slave_id ──find_slave_name()──► slave_name
       └─ DEFAULT_TRANSPORT_REGISTRY.build_for_slave(...) ──► transport
            └─ ModbusPhysicalControlButtons(transport, binding.inputs, binding.outputs)
```

### Disabled peripherals are still built

Like the fan factory, this reads the raw `peripherals` dict rather than
`PeripheralConfig.get()`. The source comment is explicit: *"Disabled is a runtime
lifecycle state, not an instruction to discard the controller needed to test and
re-enable the device."*

`PhysicalButtonsDeviceAdapter.set_enabled(True)` calls `read_states()` as its I/O
verification, which requires the controller to exist.

---

## Device Control integration

`PhysicalButtonsDeviceAdapter` (see
[../peripherals/README.md](../peripherals/README.md)) wraps this service:

| Aspect | Behaviour |
|--------|-----------|
| `key` / `label` | `"physical_control_buttons"` / `"Physical Control Buttons"` |
| `output_names` | `binding.outputs` — defines which logical buttons exist |
| Actions | Command names shaped `"<button>_on"` / `"<button>_off"`, split on the last underscore so multi-word names work |
| Labels | Title-cased, e.g. `"Eject On"` |
| `execute(action)` | `device.set_button(name, bool(commands[action]))` |
| `read_state()` | `{"inputs", "outputs", "healthy"}` |

---

## Usage

```python
from src.engine.hardware.physical_control_buttons.modbus.modbus_physical_control_buttons_factory import (
    build_modbus_physical_control_buttons,
)

buttons = build_modbus_physical_control_buttons(modbus_config, peripheral_config)

if buttons is not None:
    print(buttons.read_states())        # {"start": True, "stop": False, "reset": False}
    if buttons.is_pressed("reset"):
        buttons.set_button("reset_lamp", True)
```

---

## Design Notes

- **Output-only buttons are valid.** `outputs` is optional; a read-only panel
  passes nothing and only `read_states()` / `is_pressed()` are meaningful.
- **`KeyError` messages name the missing side.** "Unknown physical control
  button" means the input is absent; "No output configured" means the input exists
  but has no paired output.
- **Health is flag-based.** Safe to call on a timer; use `read_states()` when the
  actual button positions matter.

<!-- source-navigation:start -->
## Source navigation

[Module reference](MODULES.md) — signatures, fields, imports and source links for every Python file in this directory.

| Source subdirectory | Guide |
|---|---|
| `interfaces/` | [interfaces](interfaces/README.md) |
| `modbus/` | [modbus](modbus/README.md) |

[Complete source index](../../../SOURCE_INDEX.md).
<!-- source-navigation:end -->
