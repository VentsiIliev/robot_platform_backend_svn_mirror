# `src/engine/robot/safety/` — Safety Checker

The `safety` package implements workspace bounds enforcement plus opt-in motion corridors. `SafetyChecker` is the concrete implementation of `ISafetyChecker` and is called by `MotionService` for PTP, LIN, standard/custom sequences, step jog and Fast LIN admission; `MotionCorridor` / `MotionCorridorRegistry` provide a narrower, per-move constraint used by `MotionService.move_linear_in_corridor()`.

---

## Class Diagram

```
ISafetyChecker (ABC)
       │
       └── SafetyChecker
                 │
                 │ reads from (required)
                 └── ISettingsService → RobotSettings.safety_limits

MotionCorridor (frozen dataclass)  ← validate() / contains_xy() / contains_xyz()
MotionCorridorRegistry             ← thread-safe id → MotionCorridor map (RLock)
       ▲ held by
MotionService._motion_corridors     ← register_motion_corridor() / move_linear_in_corridor()
```

**Files:** `safety_checker.py`, `motion_corridor.py` (both re-exported from `src/engine/robot/safety/__init__.py`).

---

## API Reference

### `SafetyChecker`

**File:** `safety_checker.py`

```python
class SafetyChecker(ISafetyChecker):
    def __init__(self, settings_key, settings_service=None): ...
    def get_violations(self, position: List[float]) -> List[str]: ...
    def is_within_safety_limits(self, position: List[float]) -> bool: ...
    def is_escape_move(self, current: List[float], target: List[float]) -> bool: ...
```

`settings_key` must be an Enum. Missing settings service raises at construction.
Each admission reads the current settings and validates finite numeric XYZ bounds,
with minimum ≤ maximum. Missing limits, invalid bounds, malformed/nonfinite poses,
and settings read failures raise; they never mean that a command is allowed.
All supplied pose coordinates must be finite numbers, but only XYZ is compared
against configured bounds. Rotation bounds are not enforced here.

`get_violations()` returns an empty list only after a successful check; ordinary
out-of-bounds positions return human-readable violations. `is_within_safety_limits()`
uses the same check and propagates errors. `is_escape_move()` returns False:
this checker does not authorize generic escapes. Explicit recovery policies live
in `MotionService`.

---

## `MotionCorridor` / `MotionCorridorRegistry` — Constrained Linear Motion

**File:** `motion_corridor.py`

While `SafetyChecker` answers "is this pose anywhere inside the workspace?", a corridor answers "may this LIN move pass through this specific tunnel?" — a narrower, explicitly declared constraint used for moves that cross a machine opening (e.g. the paint dropoff passage).

### `MotionCorridor` (frozen dataclass)

```python
@dataclass(frozen=True)
class MotionCorridor:
    corridor_id: str
    x_min: float
    x_max: float
    y_min: float
    y_max: float
    z_min: float            # deepest allowed Z — typically negative (below the opening)
    entry_z_max: float      # upper Z bound — at or above zero
    maximum_velocity: float
    maximum_acceleration: float
    allow_planar_transit: bool = False
```

| Method | Contract |
|---|---|
| `validate()` | raises `ValueError` unless: non-empty `corridor_id`; XY bounds have positive area; `z_min < 0` unless `allow_planar_transit`; `z_min < entry_z_max`; `entry_z_max >= 0`; velocity and acceleration > 0 |
| `contains_xy(pose)` | `len(pose) >= 2` and X/Y inside bounds |
| `contains_xyz(pose)` | `contains_xy` and `z_min <= z <= entry_z_max` |

### `MotionCorridorRegistry`

```python
class MotionCorridorRegistry:
    def register(self, corridor: MotionCorridor) -> None: ...   # validates, then stores by corridor_id (replaces existing)
    def get(self, corridor_id: str) -> MotionCorridor | None: ...  # strip()'d lookup
```

Thread-safe via `RLock`; `register()` overwrites an existing entry with the same id (used for live settings refresh).

### How `MotionService` uses corridors

```python
motion.register_motion_corridor(corridor)                       # → registry.register()
motion.move_linear_in_corridor(corridor_id, position, tool, user,
                               velocity, acceleration,
                               blendR=0.0, wait_to_reach=False)  # → bool
```

`move_linear_in_corridor()` rejects (returns `False`, logs the violations) when any of:

| Check | Rule |
|---|---|
| unknown id | `corridor_id` not registered |
| pose shape | current or target pose has fewer than 3 elements |
| XY containment | either pose outside `x/y` bounds |
| move class | must be **descending** (current Z in `[0, entry_z_max]`, target Z `< 0`), **retracting** (current Z `< 0`, target Z in `[0, entry_z_max]`), or **planar transit** (both poses inside `contains_xyz` *and* `allow_planar_transit`) |
| speed | requested `velocity` / `acceleration` above corridor limits |

For descending/retracting moves the robot driver must expose `set_motion_passage_closed(passage_id, closed)` (planning-scene passage lid):

1. **Descending** → lid opened before the move; re-closed on failure or exception (best effort).
2. **Retracting** → lid closed after a successful move; a failed close fails the whole call.
3. Missing `set_motion_passage_closed` → the move is rejected before any command is sent.

Optional blocking: with `wait_to_reach=True` the success flag additionally requires `_wait_for_position(target)`.

### Consumers

| Consumer | Use |
|---|---|
| `MotionService` (`_motion_corridors`) | owns the registry; implements `IMotionService.register_motion_corridor` / `move_linear_in_corridor` |
| `RobotService.register_motion_corridor` | delegates to `MotionService` |
| `PaintRobotSystem._refresh_dropoff_motion_corridor` | builds the `workpiece_drop_opening` corridor from the `Dropoff` movement-group pose + tolerance and re-registers it when settings change |
| `DropoffExecutor` / `dropoff_handlers` (`src/robot_systems/paint/processes/paint/`) | pass `_dropoff_motion_corridor_id` and issue corridor LIN moves through the opening |
| `tests/engine/robot/test_motion_service.py` | direct corridor registration + rejection cases |
| `tests/robot_systems/paint/test_dropoff_motion_corridor.py` | paint dropoff corridor build/refresh/pass-through behaviour |

---

## Data Flow

`MotionService._motion_violations()` distinguishes an unavailable check (`None`)
from a completed check (a list of violations). It logs exceptions and rejects
malformed checker results. Every caller rejects `None` before any recovery
filter or bypass can run:

| Caller | Unavailable-check result |
|---|---|
| `move_ptp`, `move_linear` | `False` |
| `move_sequence`, `move_custom_sequence` | `False`, before tool selection or sequence submission |
| `start_jog` | `-1`; also rejects missing current position |
| `move_fast_linear` | `success=False`, `accepted=False`, `result=-1`, `error="platform_safety_unavailable"` |

Recovery exceptions can still apply to known violations after a successful check.
They cannot authorize a command when the checker is unavailable or its inputs are invalid.

---

## Default Safety Limits

From `SafetyLimits` defaults in `robot_settings.py`:

| Axis | Min (mm) | Max (mm) |
|------|---------|---------|
| X | −500 | 500 |
| Y | −500 | 500 |
| Z | 100 | 800 |

---

## Usage Example

```python
from src.engine.common_settings_ids import CommonSettingsID
from src.engine.robot.safety.safety_checker import SafetyChecker

checker = SafetyChecker(CommonSettingsID.ROBOT_CONFIG, settings_service)
# Direct callers must reject the operation if either query raises.
violations = checker.get_violations([0.0, 0.0, 300.0, 180.0, 0.0, 0.0])
```

## Scope and verification

This change covers the existing checker callers. Corridor LIN uses its explicit
corridor policy; trajectories, ordered chains and continuous Servo do not gain
this workspace checker through this change. Backend constraints remain separate.
Rotation bounds, joint limits and velocity/acceleration limits are not checked by
`SafetyChecker`. Bounds are validated on admission, not by the settings serializer.

Run `tests.engine.robot.test_safety_checker`,
`tests.engine.robot.test_safety_admission_failures`, and
`tests.engine.robot.test_motion_service` for boundary checks, injected settings and
checker failures, zero driver submissions, and existing valid/recovery behavior.

<!-- source-navigation:start -->
## Source navigation

[Module reference](MODULES.md) — signatures, fields, imports and source links for every Python file in this directory.

[Complete source index](../../../SOURCE_INDEX.md).
<!-- source-navigation:end -->
