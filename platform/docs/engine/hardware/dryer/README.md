# `src/engine/hardware/dryer/` — Dryer

Controller, service, register map, and transports for the drying/curing unit
(manual plate, servo actuation, indexed rotation). The dryer is the most stateful
peripheral in the engine: it has its own lifecycle (enable/disable), an
asynchronous `NEXT_POSITION` movement, and a firmware register block that is
written as one contiguous FC16 burst.

---

## Files

| File | Contents |
|------|----------|
| `interfaces/i_dryer_service.py` | `IDryerService` |
| `interfaces/i_dryer_controller.py` | `IDryerController` |
| `interfaces/i_dryer_transport.py` | `IDryerTransport` |
| `dryer_service.py` | `DryerService` — lifecycle owner |
| `dryer_controller.py` | `DryerController` — register I/O |
| `models/dryer_commands.py` | `DryerCommand`, `DEFAULT_DRYER_COMMANDS`, `dryer_commands()` |
| `models/dryer_status.py` | `DryerStatus`, `DEFAULT_DRYER_STATUSES`, `dryer_statuses()` |
| `models/dryer_state.py` | `DryerState` |
| `models/dryer_modbus_registers.py` | `DryerModbusRegister`, `DryerRegisterMap`, `DryerDefaults` |
| `models/dryer_config.py` | `DryerConfig`, `DryerConfigSerializer` |
| `models/dryer_write_data.py` | `DryerWriteData` |
| `modbus/modbus_dryer_transport.py` | `ModbusDryerTransport` |
| `modbus/modbus_dryer_factory.py` | `build_modbus_dryer_controller()` |
| `next_position_runner.py` | Standalone cycle-verification CLI |
| `read_registers.py` | Standalone register dump CLI |
| `mock_runner.py` | `MockDryerTransport` + smoke example (no serial port) |

---

## Layering

```
IDryerService  (IDryerController + IHealthCheckable)
      ▲
DryerService   ← owns lifecycle, generation counter, async init thread
      │  controller_factory(config) → IDryerController
      ▼
IDryerController
      ▲
DryerController ← register block writes, status decode, command retry
      │
IDryerTransport (semantic alias of IRegisterTransport)
      ▲
ModbusDryerTransport (ModbusRegisterTransport)
```

`DryerService` does **not** inherit `DryerController`. It holds an
`IDryerController | None` that is created by a factory and destroyed on disable,
so hardware can be cycled while application code keeps a stable service reference.

---

## Interfaces

### `IDryerController`

```python
class IDryerController(ABC):
    def initialize(self) -> bool: ...                 # write defaults + wait for NEXT_POSITION
    def shutdown(self) -> None: ...                   # release transport resources
    def update_config(self, config: DryerConfig) -> None: ...
    def write_data(self, data: DryerWriteData) -> bool: ...
    def get_state(self) -> DryerState: ...
    def execute_command(self, command: int, data: DryerWriteData | None = None) -> bool: ...
    def move_servos(self, data=None) -> bool: ...     # alias for eject()
    def eject(self, data=None) -> bool: ...
    def open_plate(self, data=None) -> bool: ...      # writes CLOSE_PLATE (see note)
    def close_plate(self, data=None) -> bool: ...
    def next_position(self, data=None) -> bool: ...
```

### `IDryerService`

```python
class IDryerService(IDryerController, IHealthCheckable):
    def enable(self) -> bool: ...                     # synchronous init
    def enable_async(self) -> bool: ...               # init on a daemon thread
    def disable(self) -> None: ...
    def is_enabled(self) -> bool: ...                 # includes "initializing"
    def is_healthy(self) -> bool: ...                 # cached, no I/O

    @property
    def last_error(self) -> str | None: ...
```

### `IDryerTransport`

```python
class IDryerTransport(IRegisterTransport):
    """Semantic type alias — constrains injection sites to dryer-specific transports."""
```

---

## `DryerService` — Lifecycle

```python
DryerService(
    controller_factory: Callable[[DryerConfig], IDryerController],
    config: DryerConfig,
)
```

The service is always available; the *controller* is what gets created and
destroyed.

### State held

| Field | Purpose |
|-------|---------|
| `_controller` | The live, fully initialised controller — `None` when disabled |
| `_initializing_controller` | Controller under construction, kept so `disable()` can shut it down mid-init |
| `_initialization_thread` | The async init thread, cleared when it exits |
| `_lock` | `threading.RLock` guarding every field above |
| `_generation` | Monotonic counter, bumped on each enable **and** disable |
| `_enabled_requested` | True while an enable is wanted (set during initialisation, before success) |
| `_last_error` | Most recent lifecycle or command error |

### The generation counter

Every call to `enable()`, `enable_async()`, and `disable()` calls
`_begin_enable()` / `disable()`, which increments `_generation`. All three
decision points inside `_initialize()` re-check it:

```python
if generation != self._generation or not self._enabled_requested:
    controller.shutdown()   # discard
    return False
```

This makes three races benign: enable→enable, enable→disable during init, and
disable→enable while a stale thread is still running. A superseded initialisation
thread discards its controller instead of publishing a stale one.

`_begin_enable()` also sets `_last_error = "Dryer initialization is in progress"`
before starting, so `last_error` never returns `None` during the window — callers
can always explain why the dryer is not yet responding.

### `enable()` vs `enable_async()`

| | `enable()` | `enable_async()` |
|---|---|---|
| Runs `_initialize` | On the calling thread | On a daemon thread named `DryerInitialization` |
| Blocks | Yes | No |
| Returns | Result of initialisation | `True` when the thread started (re-checked under lock against a superseded generation), `False` otherwise |
| Typical caller | Tests, startup sequences that must wait | GUI enable action |

### Failure handling

`_initialize()` wraps **all** construction and initialisation work in
`try/except Exception`. On failure:

1. `_last_error` is set to `str(exc)` (only if the generation still matches)
2. The half-built controller is shut down, but only if this thread still owns it
   (`_initializing_controller is controller`)
3. `is_healthy()` becomes `False` because `_controller` is still `None`
4. The exception is logged with `logging.exception`

The `owns_controller` check exists so that if `disable()` already adopted and
shut down the controller, the failing thread does not shut it down a second time.

### `disable()`

```python
with self._lock:
    self._generation += 1
    self._enabled_requested = False
    controllers = tuple(...)     # controller and/or initializing_controller
    self._controller = None
    self._initializing_controller = None
for controller in dict.fromkeys(controllers):
    try: controller.shutdown()
    except Exception: self._logger.exception("Dryer shutdown failed")
```

Shutdown happens **outside** the lock so a slow `transport.disconnect()` never
blocks readers of `get_state()`. `dict.fromkeys` de-duplicates when both slots
hold the same object.

### Command delegation

Every command (`write_data`, `eject`, `next_position`, `close_plate`,
`open_plate`, `move_servos`) funnels through `_call(method_name, data)`:

```python
def _call(self, method_name, data) -> bool:
    with self._lock:
        controller = self._controller
    if controller is None:
        error = self._unavailable_error()   # _last_error or "Dryer is disabled or unavailable"
        self._logger.error(error)
        return False
    return bool(getattr(controller, method_name)(data))
```

A disabled dryer **logs and returns `False`**; it never raises.

`execute_command(command, data)` is separate rather than routed through `_call`,
because its first argument is a numeric command code, not a method name.

### `get_state()` when disabled

```python
return DryerState(is_healthy=False, communication_errors=[self._unavailable_error()])
```

Consumers receive a well-formed state rather than `None`, and can distinguish
"disabled" from "hardware fault" by reading `communication_errors[0]`.

### Interface-preserving aliases

`initialize()` → `enable()`, `shutdown()` → `disable()`, `disconnect()` →
`disable()`. These exist so `DryerService` satisfies `IDryerController`
callers that treat the service as a controller.

### Health

```python
def is_healthy(self) -> bool:
    with self._lock:
        return self._controller is not None and self._last_error is None
```

Flag-only, no I/O — safe for availability gating. A configured-but-uninitialised
dryer is not healthy; an initialised one with no recorded error is.

---

## `DryerController`

```python
DryerController(
    transport, config=None, register_map=None,
    commands=None, statuses=None,
    next_position_timeout_s=10.0,
    status_poll_interval_s=0.1,
    command_settle_s=0.03,
    max_retries=0,
)
```

`commands` and `statuses` come from `PeripheralBinding.commands` /
`.statuses`, so command codes and status masks are settings, not code.

`self._register_map.require_contiguous()` runs in the constructor — a
non-contiguous map would silently corrupt an FC16 block write, so it fails fast.

### `initialize()`

```python
1. self._initialization_cancelled.clear()
2. write_data(DryerWriteData.from_config(config))    # defaults to register block
3. next_position()                                   # command a move
4. _wait_until_next_position_done()                  # verify the cycle
```

### `_wait_until_next_position_done()` — fresh-cycle verification

`DONE` may be stale from the previous cycle, so the wait does not accept it
immediately.

```
fresh_cycle_observed = False
unhealthy_since = None
loop every status_poll_interval_s:
    if _initialization_cancelled.is_set():        → return False   (shutdown path)
    state = get_state()
    if healthy and fresh_cycle_observed and done and not moving:   → return True
    if healthy:
        unhealthy_since = None
        if moving or not done: fresh_cycle_observed = True         # latch
    elif unhealthy_since is None:
        unhealthy_since = now
    if not fresh_cycle_observed and now >= acknowledgement_deadline:
                                                     → return False (never moved)
    if unhealthy_since and now - unhealthy_since >= timeout:
                                                     → return False (status stuck bad)
```

Two independent failure modes are distinguished by the error log:

| Condition | Log |
|-----------|-----|
| Movement never acknowledged within `next_position_timeout_s` | "next-position movement was not acknowledged within %.1f s" |
| Status reported unhealthy continuously for `next_position_timeout_s` | "status remained unhealthy for %.1f s" |

`_initialization_cancelled` is set by `shutdown()`, so disabling the dryer during
initialisation stops the poll loop promptly rather than after the timeout.

### `write_data()` / `get_state()` retries

Both use `max_retries + 1` total attempts, sleeping `status_poll_interval_s`
between them. Warnings log each retry with `error_type` and `error`; the final
failure logs at `ERROR` with `exc_info=True`.

- `write_data()` returns `False` on exhausted retries
- `get_state()` returns `DryerState(is_healthy=False, communication_errors=[str(exc)])`
  rather than raising — a status read failure must not break a poll loop

### Command writes

| Method | Register written | Notes |
|--------|------------------|-------|
| `write_data(data)` | `register_map.status`, all 17 values | FC16 burst of the whole block |
| `eject(data)` | `register_map.status` + `command = eject` | Special retry handling (below) |
| `next_position(data)` | `register_map.command`, `[command]` | **Single-register** FC16 write |
| `_write_command(cmd, data)` | `register_map.status` + `command` | Used by `execute_command`, `open_plate`, `close_plate` |
| `move_servos(data)` | delegates to `eject(data)` | |

On success every path sleeps `command_settle_s` (default 30 ms) before returning,
letting the firmware latch the command.

### Lost-ACK recovery

A Modbus acknowledgement can be lost even when the device accepted the command.
Re-sending `EJECT` or `NEXT_POSITION` would cause a duplicate physical movement.

**`eject()`** on write exception calls
`_eject_command_was_accepted_without_acknowledgement()`:

```
sleep status_poll_interval_s
state = get_state()
return state.is_healthy and state.ejecting
```

If the dryer is reporting "ejecting", the command landed → return `True` instead
of retrying.

**`next_position()`** does the same via `_command_was_accepted_without_acknowledgement()`:

```
return state.is_healthy and (state.next_position_moving or not state.next_position_done)
```

A fresh movement (or a cleared `DONE`) proves acceptance.

Both helpers are documented in-code with the same rationale: *"Avoid repeating …
when only its Modbus acknowledgement was lost."*

### Compatibility aliases

```python
def move_servos(self, data=None): return self.eject(data)
def open_plate(self, data=None):  return self._write_command(self._commands["close_plate"], data)
def close_plage(self, data=None): return self._write_command(self._commands["close_plate"], data)
def close_plate(self, data=None): return self.close_plage(data)
```

`move_servos` / `open_plate` exist for callers still using the former UI names.
`close_plage` is a historical misspelling retained as the implementation, with
`close_plate` added as the corrected public name. **Both plate commands write the
same `close_plate` command code** — there is no distinct "open" firmware command.

---

## Models

### `DryerCommand` / `DryerStatus`

```python
class DryerCommand(IntFlag):
    NEXT_POSITION = 1
    EJECT         = 2
    CLOSE_PLATE   = 4
    MOVE_SERVOS   = EJECT      # compatibility alias
    OPEN_PLATE    = CLOSE_PLATE

class DryerStatus(IntFlag):
    READY           = 0x01
    EJECT           = 0x08
    EJECT_DONE      = 0x10
    NEXT_POS_MOVING = 0x20
    NEXT_POS_DONE   = 0x40
```

`dryer_commands(overrides)` and `dryer_statuses(overrides)` return
`{**DEFAULT_*, **dict(overrides or {})}` — robot-system settings override
firmware defaults per key.

### `DryerState`

```python
@dataclass(frozen=True)
class DryerState:
    raw_status: int = 0
    is_ready: bool = False
    ejecting: bool = False
    eject_done: bool = False
    next_position_moving: bool = False
    next_position_done: bool = False
    is_healthy: bool = False
    communication_errors: List[str] = field(default_factory=list)
```

`from_raw_status(raw, statuses)` ANDs each mask. It sets `is_healthy=True`
because reaching it means the read succeeded — `is_healthy=False` on a
`DryerState` only ever comes from a constructor that also fills
`communication_errors`.

Compatibility properties: `servos_moving` (`ejecting or next_position_moving`),
`plate_on_position` (`next_position_done`), `has_errors`.

### `DryerRegisterMap` / `DryerModbusRegister`

A 17-register firmware block, `STATUS` at `0` through
`TARGET_POSITION_FORWORD` at `16`:

| Address | Register | Address | Register |
|--------:|----------|--------:|----------|
| 0 | `status` | 9 | `time_delay_move_servo_out` |
| 1 | `command` | 10 | `time_delay_move_plate_in` |
| 2 | `pwm_open_vrytka` | 11 | `time_delay_move_plate_out` |
| 3 | `pwm_close_vrytka` | 12 | `time_delay_start_servo_move` |
| 4 | `pwm_open_izbutvatel` | 13 | `rev_minute` |
| 5 | `pwm_close_izbutvatel` | 14 | `acceleration` |
| 6 | `time_delay_move_servo_up` | 15 | `target_position_backword` |
| 7 | `time_delay_move_servo_down` | 16 | `target_position_forword` |
| 8 | `time_delay_move_servo_in` | | |

| Method | Description |
|--------|-------------|
| `from_mapping(mapping)` | Fills any field present in `mapping`, else keeps the default. This is how `PeripheralBinding.inputs` / `.outputs` supply a site-specific map |
| `addresses` | Tuple of every address, in dataclass field order |
| `require_contiguous()` | Raises `ValueError` unless addresses are exactly `range(status, status + 17)` |

`require_contiguous()` is called by the controller constructor and by
`read_registers.py`. The constraint exists because `write_data()` issues a single
FC16 burst starting at `status`.

### `DryerConfig` / `DryerConfigSerializer`

Frozen dataclass of 15 editable values (4 PWM duty pairs, 6 servo/plate time
delays, `rev_minute`, `acceleration`, 2 target positions). Defaults come from
`DryerDefaults`.

`from_dict` iterates `__dataclass_fields__`, coercing `acceleration` to `float`
and everything else to `int`, falling back to the default when a key is absent —
so settings files written for an older firmware load without error.

`DryerConfigSerializer.settings_type = "dryer_config"`.

### `DryerWriteData`

```python
@dataclass(frozen=True)
class DryerWriteData:
    status: int = DryerDefaults.status
    command: int | DryerCommand = DryerDefaults.command
    ...   # same 15 fields as DryerConfig

    @classmethod
    def from_config(cls, config, command=0) -> DryerWriteData:
        return cls(command=command, **config.to_dict())

    def to_register_values(self) -> list[int]: ...
```

`to_register_values()` returns exactly **17 integers** in register order.
`acceleration` is converted from the float in settings to integer **tenths**:

```python
acceleration_tenths = round(float(self.acceleration) * 10)   # 0.1 → 1
```

`rev_minute` is already a raw word and passes through unchanged.

---

## Modbus Wiring

### `ModbusDryerTransport`

```python
class ModbusDryerTransport(ModbusRegisterTransport, IDryerTransport):
    """Modbus RTU transport for dryer boards."""
```

Docstring-only subclass, as required by the platform rule for new device
transports.

### `build_modbus_dryer_controller()`

```python
def build_modbus_dryer_controller(
    modbus_config: ModbusConfig,
    dryer_config: DryerConfig | None = None,
) -> IDryerController:
```

Builds `ModbusDryerTransport` from the **top-level** `modbus_config` fields and
passes `modbus_config.max_retries` through as the controller's retry count.

> Like the vacuum-sensor factory, this reads the legacy top-level profile rather
> than `DEFAULT_TRANSPORT_REGISTRY.build_for_slave()`, and it does not consult
> `PeripheralBinding`. The `next_position_runner.py` and `read_registers.py` CLIs
> *do* resolve the slave and register map from peripheral settings — see below.

---

## Standalone Tools

All three run without the GUI and without a robot.

### `next_position_runner.py` — cycle verification

Runs consecutive real `NEXT_POSITION` cycles against the hardware.

```bash
python src/engine/hardware/dryer/next_position_runner.py \
    --modbus-config src/robot_systems/paint/storage/settings/hardware/modbus.json \
    --peripherals-config src/robot_systems/paint/storage/settings/hardware/peripherals.json \
    --dryer-settings src/robot_systems/paint/storage/settings/dryer/settings.json \
    --cycles 3 --cycle-delay 0.5 --ack-timeout 10.0 --poll-interval 0.1
```

Defaults point at the **paint** system's settings root. It:

1. Resolves `peripherals["dryer"]` → `slave_id` → slave name
2. Builds `DryerRegisterMap.from_mapping({**binding.inputs, **binding.outputs})`
3. Builds a `DryerController` with `commands=binding.commands` and
   `statuses=binding.statuses`
4. For each cycle: read status → `next_position()` →
   `_wait_until_next_position_done()` → verify final `healthy && done && !moving`

Requires a **fresh movement cycle** before accepting `DONE`, so a stale flag from
the previous cycle cannot pass. `EJECT` is never sent by this runner. Ctrl-C
stops the wait; exit codes are `0` (all cycles passed), `1` (failure), `130`
(interrupted).

It calls the private `controller._wait_until_next_position_done()` directly —
this is the same code path the runtime uses.

### `read_registers.py` — register dump

```bash
python src/engine/hardware/dryer/read_registers.py \
    [--modbus-config PATH] [--peripherals-config PATH]
```

Resolves the dryer slave and register map from peripheral settings, prints the
resolved connection, writes the command register block (code as written: value
`600` to address `2`, then `0` to address `1`), reads all 17 holding registers,
then prints a table of `ADDRESS / REGISTER / DECIMAL / HEX` plus the decoded
`DryerStatus` flag names.

> The module docstring says "Write diagnostic value 2 to address 2", but the code
> writes `600` to address `2`. The code is authoritative.

### `mock_runner.py` — no-hardware smoke test

```bash
python src/engine/hardware/dryer/mock_runner.py
```

`MockDryerTransport` implements `IDryerTransport` in memory: `registers: dict`,
`writes: list[tuple[int, List[int]]]`, and a `connected` flag. It intercepts all
register I/O while the controller is built with the same config objects as real
wiring, then prints sections describing config, write data, and status decoding.

---

## Device Control Integration

`DryerDeviceAdapter` in
[../peripherals/README.md](../peripherals/README.md#dryerdeviceadapter) wraps an
`IDryerService`. Because the service itself owns enabled state, the adapter has no
local flag and delegates `is_enabled()` / `last_error()` to the service. Its
`next_position` action polls `get_state()` for a fresh moving→done cycle with a
10 s deadline.

---

## Design Notes

- **Two objects, one interface.** `DryerService` keeps `IDryerService` call sites
  valid across enable/disable cycles; only the controller is rebuilt.
- **Generation counter over locks-as-mutexes.** Correctness under concurrent
  enable/disable comes from re-validating a generation number at every publish
  point, not from holding the lock across long operations.
- **Never repeat a movement command.** Lost-ACK recovery re-reads status instead
  of retrying blindly, so physical motion is never duplicated.
- **Contiguity is a hard precondition**, checked at construction because an FC16
  burst to a non-contiguous map would write the wrong registers.
- **Failure is data, not exceptions.** Disabled service, dead transport, and
  exhausted retries all surface as `DryerState(is_healthy=False, …)` or `False`.
