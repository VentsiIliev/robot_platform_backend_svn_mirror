# `src/engine/hardware/peripherals/` — Peripheral Bindings and Device Adapters

Two concerns in one package:

1. **`peripherals.py`** — the settings model that maps logical device names
   ("laser", "dryer", "vacuum_sensor") onto Modbus slave IDs, register labels,
   and command codes, independent of transport protocol.
2. **`device_control_adapters.py`** — adapters that wrap already-constructed
   device services into one uniform shape so the shared Device Control
   application can drive every peripheral through the same code path.

---

## Files

| File | Contents |
|------|----------|
| `peripherals.py` | `PeripheralBinding`, `PeripheralConfig`, `PeripheralConfigSerializer` |
| `device_control_adapters.py` | `BinaryDeviceAdapter`, `VacuumSensorDeviceAdapter`, `PhysicalButtonsDeviceAdapter`, `DryerDeviceAdapter`, `build_device_control_adapters()` |

---

## `peripherals.py` — Settings Model

### `PeripheralBinding`

```python
@dataclass(frozen=True)
class PeripheralBinding:
    slave_id: int
    enabled: bool = True
    inputs:  dict[str, str] = field(default_factory=dict)
    outputs: dict[str, str] = field(default_factory=dict)
    commands: dict[str, int] = field(default_factory=dict)
    statuses: dict[str, int] = field(default_factory=dict)
```

One logical device mapped to one configured Modbus slave. `slave_id` is the only
required field; everything else is empty by default, so a device that only needs
on/off control configures just the slave.

| Field | Meaning |
|-------|---------|
| `slave_id` | Numeric Modbus slave address this device answers on |
| `enabled` | Master switch. A disabled binding is skipped entirely by `get()` |
| `inputs` | Logical name → register label (e.g. `{"vacuum": "X3"}`) |
| `outputs` | Logical name → register label (e.g. `{"pump": "Y0"}`) |
| `commands` | Action name → command code (e.g. `{"eject": 16}`) |
| `statuses` | Status name → status code for interpreting raw status words |

`from_dict` coerces `inputs`/`outputs` values to `str` and `commands`/`statuses`
values to `int`, so JSON numbers and strings both load cleanly.

### `PeripheralConfig`

```python
@dataclass(frozen=True)
class PeripheralConfig:
    peripherals: dict[str, PeripheralBinding] = field(default_factory=dict)

    def get(self, name: str) -> PeripheralBinding | None: ...
```

Serialises as a **flat** dict keyed by device name — the wrapper object does not
appear in JSON:

```json
{
  "laser":  { "enabled": true, "slave_id": 12, "outputs": { "laser": "Y5" } },
  "dryer":  { "enabled": true, "slave_id": 14, "commands": { "eject": 16 } }
}
```

`get(name)` returns `None` when the name is absent **or** when the binding is
disabled — callers get a single "is this usable?" check for free, and disabled
peripherals are never constructed.

### `PeripheralConfigSerializer`

`settings_type = "peripheral_config"`. Register it in the robot system's
`settings_specs` and retrieve it with `settings_service.get("peripheral_config")`.

---

## `device_control_adapters.py` — Adapter Contract

Every adapter exposes the same duck-typed surface, so the Device Control
application can render heterogeneous hardware uniformly without importing any
device type:

| Method | Returns | Purpose |
|--------|---------|---------|
| `key` / `label` | `str` attributes | Stable identifier and display name |
| `set_enabled(enabled)` | `bool` | Enable/disable the peripheral, verifying with a real I/O check and persisting the result |
| `is_enabled()` | `bool` | Current enabled state |
| `last_error()` | `str \| None` | Message from the last failure |
| `actions()` | `Mapping[str, str]` | Action name → button label for configured actions |
| `execute(action)` | `bool` | Run one action; `False` on failure |
| `read_state()` | `Mapping[str, object]` | Current state snapshot |

All four constructors accept an optional `persist_enabled: Callable[[str, bool], None]`
callback, invoked whenever the enabled state changes so the robot system can write
it back to settings. When `None`, the state is memory-only.

Every `set_enabled(True)` path performs a **real I/O verification** before
committing, and on failure sets `enabled = False`, records a message, and
persists the `False`. A peripheral that cannot be reached is never left marked as
enabled.

---

## `BinaryDeviceAdapter`

```python
BinaryDeviceAdapter(
    key: str, label: str, device: Any, *,
    enabled: bool = True,
    persist_enabled: Callable[[str, bool], None] | None = None,
    enable_check: Callable[[], object] | None = None,
    commands: Mapping[str, int] | None = None,
)
```

Wraps any device exposing `turn_on()` / `turn_off()`. `device` is typed `Any`
because it may be a laser, fan, vacuum pump, or tray fan.

- **`enable_check`** — the device's `read_state()` method, when present. Calling
  it is what proves the device answers. A failure disables the peripheral and
  records `f"{label} register read failed"` if the exception has no message.
- **`set_enabled(False)`** calls `device.turn_off()` first — disabling means
  *turn the hardware off*, not just hide the control. If that fails, the enabled
  flag is left untouched and `False` is returned.
- **`actions()`** returns only `on` and `off`, labelled `"ON"` / `"OFF"` by
  upper-casing. Other configured commands are filtered out.
- **`execute(action)`** treats a `None` return from `turn_on`/`turn_off` as
  success (devices that return `None` raise on failure instead). `_active`
  tracks the last known output state.
- **`read_state()`** returns `{"enabled", "active", "healthy", "error"}`. `healthy`
  comes from `_cached_health()`, which calls `device.is_healthy()` **only if the
  device implements `IHealthCheckable`**, otherwise `None`.

> `read_state()` calls `is_healthy()`, which for some devices such as
> `IGeneratorController` performs blocking I/O. Do not invoke it on a timer from
> the GUI thread.

---

## `VacuumSensorDeviceAdapter`

`key = "vacuum_sensor"`, `label = "Vacuum Sensor"`. Read-only — `actions()`
returns an empty mapping and `execute()` always returns `False` with a warning.

- **`set_enabled(True)`** calls `is_vacuum_detected()` first, because that call
  performs the real register read and updates communication health
  independently of the detected value. It then checks `is_healthy()` and disables
  the peripheral with `"Vacuum sensor register read failed"` on failure.
- **`read_state()`** returns `{"detected", "raw", "healthy"}` when enabled, or
  `{"enabled": False, "healthy": False, "error": …}` when not. `raw` comes from
  the device's `last_raw_value` property.

---

## `PhysicalButtonsDeviceAdapter`

`key = "physical_control_buttons"`, `label = "Physical Control Buttons"`.
Exposes an input/output button panel.

- **`output_names`** comes from `PeripheralBinding.outputs` and defines which
  logical buttons exist.
- **`set_enabled(True)`** calls `device.read_states()` as the I/O verification.
- **`actions()`** derives labels from command names of the form
  `"<button>_on"` / `"<button>_off"`, where `<button>` must exist in
  `output_names`. `_button_command()` splits on the **last** underscore via
  `rpartition`, so multi-word button names work. Labels are title-cased
  (`"Eject On"`).
- **`execute(action)`** calls `device.set_button(name, bool(commands[action]))`.
  A missing output raises `KeyError` inside the device and is logged.
- **`read_state()`** returns `{"inputs", "outputs", "healthy"}`, reading both
  sides. `healthy` is `None` for devices not implementing `IHealthCheckable`.

---

## `DryerDeviceAdapter`

`key = "dryer"`, `label = "Dryer"`. The dryer is **stateful and asynchronous**, so
this adapter differs from the others in two ways:

- It has **no local `enabled` flag**. `is_enabled()` delegates to
  `device.is_enabled()` and `last_error()` returns the device's `last_error`
  property, because `IDryerService` owns that state itself.
- `set_enabled()` calls `device.enable()` / `device.disable()`, then verifies
  against `device.is_enabled()`, and persists the **actual** state.

### `execute()` dispatch

Three action shapes, resolved in order:

1. `next_position` — routed to `_execute_next_position()`
2. Any other method name matching the action on the device (`eject`,
   `close_plate`) — called directly
3. Otherwise `device.execute_command(commands[action])` with the configured code

Labels are a fixed map: `eject` → `"Eject"`, `close_plate` → `"Close Plate"`,
`next_position` → `"Next Position"`. Any other configured command is not offered.

### `_execute_next_position()` — completion detection

Sending `NEXT_POSITION` and reporting success immediately would be wrong, because
the movement happens asynchronously. The adapter instead waits for a **fresh
moving→done status cycle**:

```
1. initial = get_state()
   movement_observed = initial.is_healthy and not initial.next_position_done
2. send the command; return False if it is rejected
3. poll get_state() every 100 ms up to a 10 s deadline:
     if healthy and (moving or not done): movement_observed = True
     if healthy and movement_observed and done and not moving: return True
4. deadline exceeded → return False
```

The `movement_observed` latch matters: if the dryer was already settled when the
command was sent, the first poll could see `done` immediately, which would be a
false success. Requiring that movement was seen at least once guarantees the
reported completion belongs to this command.

`read_state()` surfaces `healthy`, `ready`, `ejecting`, `eject_done`,
`next_position_moving`, `next_position_done`, `raw`, and the first
communication error if any.

---

## `build_device_control_adapters()`

```python
def build_device_control_adapters(
    peripheral_config: PeripheralConfig,
    services: Mapping[str, object],
    persist_enabled: Callable[[str, bool], None] | None = None,
) -> list[object]:
```

Builds adapters for **configured and already-constructed** devices. A peripheral
is skipped when it has no binding **or** when its service is absent from
`services`, so missing hardware degrades to a shorter list rather than an error.

| Order | Key | Adapter | Label |
|-------|-----|---------|-------|
| 1 | `vacuum_pump` | `BinaryDeviceAdapter` | Vacuum Pump |
| 1 | `fan` | `BinaryDeviceAdapter` | Fan |
| 1 | `tray_fan` | `BinaryDeviceAdapter` | Tray Fan |
| 1 | `laser` | `BinaryDeviceAdapter` | Laser |
| 2 | `vacuum_sensor` | `VacuumSensorDeviceAdapter` | Vacuum Sensor |
| 3 | `physical_control_buttons` | `PhysicalButtonsDeviceAdapter` | Physical Control Buttons |
| 4 | `dryer` | `DryerDeviceAdapter` | Dryer |

The four binary devices share one loop; the `enable_check` is taken from the
device's own `read_state()` when callable.

> The `services` mapping is keyed by the same names as `peripheral_config`.
> Robot systems build it in `on_start()` after constructing the device services.

---

## Design Notes

- **Bindings are frozen.** `PeripheralBinding` and `PeripheralConfig` are
  immutable, so a settings reload replaces the object rather than mutating one
  that another thread may be reading.
- **Adapters depend on duck typing, not device types.** `device: Any` keeps this
  package free of imports from every device package, which would otherwise create
  a dependency cycle.
- **Verification on enable is deliberate.** Marking a peripheral enabled is a
  claim about hardware reachability, so every adapter proves it with I/O before
  committing.
- **Command codes are data, not code.** `commands` maps action names to numeric
  codes, so new device commands can be added through settings without changing
  this module.

<!-- source-navigation:start -->
## Source navigation

[Module reference](MODULES.md) — signatures, fields, imports and source links for every Python file in this directory.

[Complete source index](../../../SOURCE_INDEX.md).
<!-- source-navigation:end -->
