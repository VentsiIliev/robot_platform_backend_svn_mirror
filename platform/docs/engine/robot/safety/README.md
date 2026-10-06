# `src/engine/robot/safety/` — Safety Checker

The `safety` package implements workspace bounds enforcement plus opt-in motion corridors. `SafetyChecker` is the concrete implementation of `ISafetyChecker` and is called by `MotionService` before forwarding any position to the robot SDK; `MotionCorridor` / `MotionCorridorRegistry` provide a narrower, per-move constraint used by `MotionService.move_linear_in_corridor()`.

---

## Class Diagram

```
ISafetyChecker (ABC)
       │
       └── SafetyChecker
                 │
                 │ reads from (optional)
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
    def __init__(self, settings_service=None): ...
    def is_within_safety_limits(self, position: List[float]) -> bool: ...
```

#### `is_within_safety_limits(position) → bool`

Checks whether the target Cartesian position is within the configured workspace bounds.

**Logic:**

```
if position is empty or has fewer than 3 elements:
    return False            ← invalid position

if settings_service is None:
    return True             ← no settings → fail-safe (motion allowed)

config = settings_service.get("robot_config")
limits = config.safety_limits

if limits is None:
    return True             ← no limits configured → motion allowed

x, y, z = position[0], position[1], position[2]
return (
    limits.x_min <= x <= limits.x_max and
    limits.y_min <= y <= limits.y_max and
    limits.z_min <= z <= limits.z_max
)

on any exception:
    log warning → return True   ← exception → fail-safe (motion allowed)
```

Only the translational axes (x, y, z) are checked. Rotation axes (rx, ry, rz) are not checked even if `SafetyLimits` contains rotation bounds.

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

```
MotionService.move_ptp(position, ...)
        │
        │  safety.is_within_safety_limits(position)
        ▼
SafetyChecker
        │
        ├─ settings_service is None? → return True (motion allowed)
        │
        ├─ settings_service.get("robot_config") → RobotSettings
        │       └─ .safety_limits → SafetyLimits
        │
        ├─ x_min ≤ x ≤ x_max?
        ├─ y_min ≤ y ≤ y_max?
        └─ z_min ≤ z ≤ z_max?
                │
                ├─ all True → return True (motion allowed)
                └─ any False → return False (motion blocked)

MotionService (on False):
    log warning "move_ptp blocked by safety limits"
    return False                        ← no motion command sent to robot
```

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
from src.engine.robot.safety.safety_checker import SafetyChecker

# Without settings (fail-safe mode — all positions allowed)
checker = SafetyChecker()
print(checker.is_within_safety_limits([0.0, 0.0, 300.0, 180.0, 0.0, 0.0]))  # True

# With settings
checker = SafetyChecker(settings_service=settings_service)
print(checker.is_within_safety_limits([0.0, 0.0, 50.0, 0.0, 0.0, 0.0]))   # False (z < 100)
print(checker.is_within_safety_limits([0.0, 0.0, 300.0, 0.0, 0.0, 0.0]))  # True
```

---

## Design Notes

### Fail-Safe Behavior

`SafetyChecker` is intentionally **permissive** when configuration is unavailable:

- No `settings_service` → **motion allowed** (useful for test environments and standalone runners)
- `safety_limits` attribute missing → **motion allowed**
- Exception during limit check → **motion allowed** (logs a warning)

This is the correct fail-safe for a development platform where the safety system is optional and the physical robot is not always connected.

### What Is Not Checked

- **Rotation bounds** (rx, ry, rz): `SafetyLimits` stores rotation min/max values, but `SafetyChecker` only validates x, y, z.
- **Joint limits**: These are enforced by the robot firmware (FairinoRobot SDK), not by this layer.
- **Velocity/acceleration limits**: `GlobalMotionSettings` has these values, but they are not enforced here.

### Two independent safety layers

- `SafetyChecker` is the **global** gate: one workspace box applied to every position by `MotionService`.
- `MotionCorridor` is the **per-move** gate: an opt-in tunnel declared by the robot system for a specific constrained passage, plus motion-class and lid control rules. Registering nothing changes nothing — corridors never replace the global check.

### Singleton-Free

`SafetyChecker` has no singleton or class-level state. Each `MotionService` receives its own instance, configured with (or without) a settings service.
