# `src/applications/robot_settings/` — Robot Settings Application

The `robot_settings` application provides a GUI for editing robot configuration, declared movement groups, calibration parameters, and the live ZeroErr sensorless-collision configuration. It now also exposes:
- the standalone camera-TCP offset calibration routine settings
- the optional camera-TCP offset capture settings used inside the main robot calibration pipeline
- optional robot-system-specific targeting definitions such as named points and named frames
- an optional `Sensorless Collision` tab when the injected robot service supports the ZeroErr collision-monitor REST contract

This is intended to be the shared robot-settings application for any robot system that adopts the common platform contracts:
- `CommonSettingsID.ROBOT_CONFIG`
- `CommonSettingsID.MOVEMENT_GROUPS`
- `CommonSettingsID.ROBOT_CALIBRATION`
- `NavigationService`

Optional integrations:
- `CommonSettingsID.TOOL_CHANGER_CONFIG` for slot/tool display
- robot-system-specific targeting load/save adapters for the `Targeting` tab
- live collision-monitor configuration for ROS2/ZeroErr robots

The shared `CameraSettings` application follows the same model:
- `CommonServiceID.VISION`
- `CommonSettingsID.VISION_CAMERA_SETTINGS`

---

## Architecture

```
RobotSettingsApplication(IApplication)
  └─ RobotSettingsFactory(ApplicationFactory).build(settings_service)
       ├─ RobotSettingsModel          ← load/save RobotSettings + MovementGroupSettings + RobotCalibrationSettings
       ├─ RobotSettingsView           ← multi-tab SettingsView + raw tabs for movement groups and targeting definitions
       └─ RobotSettingsController     ← save_requested → model.save(flat, movement_groups, targeting_definitions)
```

One service interface:

```
IRobotSettingsService   ← load_config / save_config / load_movement_groups / save_movement_groups / load_calibration / save_calibration / optional targeting-definition callbacks
```

---

## Class Summary

| Class | Role |
|-------|------|
| `RobotSettingsApplication(IApplication)` | Bootstrap entry point; constructs `RobotSettingsApplicationService` + factory |
| `RobotSettingsFactory(ApplicationFactory)` | Standard 3-method override |
| `IRobotSettingsService` | ABC: load/save `RobotSettings`, `MovementGroupSettings`, and `RobotCalibrationSettings` |
| `RobotSettingsApplicationService` | Wraps `ISettingsService`; handles robot config, movement groups, calibration, and optional targeting-definition adapters |
| `RobotSettingsModel` | Holds robot config, movement groups, calibration, and optional targeting-definition editor data; `save()` writes all active sections |
| `RobotSettingsMapper` | `to_flat_dict / from_flat_dict` for `RobotSettings` |
| `RobotCalibrationMapper` | `to_flat_dict / from_flat_dict` for `RobotCalibrationSettings` |
| `RobotSettingsView` | schema-driven tabs + raw tabs for movement groups, targeting definitions, and optional sensorless-collision controls; schema groups are collapsible and collapsed by default |
| `RobotSettingsController` | `save_requested` → reads view flat + movement groups + targeting definitions → `model.save()` |

---

## Data Flow

### Load

```
controller.load()
  → config, calibration, targeting_definitions = model.load()
  → view.load_config(config)            ← SettingsView populates all tabs
  → view.load_movement_groups(model.get_expected_movement_groups())
  → view.load_targeting_definitions(targeting_definitions)
```

### Save

```
User clicks Save
  → RobotSettingsView.save_requested.emit(values_dict)
  → RobotSettingsController._on_save(_values)
  → flat = view.get_values()
  → movement_groups = view.get_movement_groups()
  → targeting_definitions = view.get_targeting_definitions()
  → model.save(flat, movement_groups, targeting_definitions)
       ├─ RobotSettingsMapper.from_flat_dict(flat, _config) → updated RobotSettings
       │    settings_service.save("robot_config", updated)
       ├─ settings_service.save("movement_groups", MovementGroupSettings(...))
       └─ RobotCalibrationMapper.from_flat_dict(flat, _calibration) → updated RobotCalibrationSettings
            settings_service.save("robot_calibration", updated_calib)
```

---

## View Tabs

| Tab | Schema Groups | Fields |
|-----|--------------|--------|
| General | `ROBOT_INFO_GROUP`, `GLOBAL_MOTION_GROUP`, `TCP_STEP_GROUP`, `OFFSET_DIRECTION_GROUP` | IP, tool, user, global vel/acc, jog step, TCP steps, direction map |
| Safety | `SAFETY_LIMITS_GROUP` | x/y/z/rx/ry/rz min+max bounds |
| Movement Groups | `MovementGroupsTab` (raw) | Named positions: name, position string, vel, acc |
| Targeting | `TargetingDefinitionsTab` (raw) | Generic named points and frames supplied by the active robot system |
| Sensorless Collision | `SensorlessCollisionTab` (optional raw tab) | Detection enable, active/passive response, primary sensitivity, confirmation cycles, dynamic threshold controls, per-joint observer thresholds, and optional secondary effort/following-error thresholds |

The Targeting tab uses the shared `KeyboardNumberField` for editable camera-to-TCP X/Y offsets, including read-only inherited area values.
| Calibration | `CALIBRATION_ADAPTIVE_GROUP`, `CALIBRATION_MARKER_GROUP`, `CALIBRATION_AXIS_MAPPING_GROUP`, `CALIBRATION_CAMERA_TCP_GROUP` | Adaptive movement params, marker/z settings, axis-mapping settings, standalone camera-TCP settings, and optional in-main-calibration TCP capture settings |

---

## Usage Example

```python
from src.applications.robot_settings.robot_settings_application import RobotSettingsApplication


# In robot vision_service wiring:
def _build_robot_settings(robot_system):
    return RobotSettingsApplication(robot_system._settings_service)


# Standalone (requires ISettingsService stub):
widget = RobotSettingsFactory().build(RobotSettingsApplicationService(settings_service))
```

---

## Design Notes

- **Movement groups are a separate settings domain**: `robot/config.json` stays robot-oriented; named positions and trajectories persist in `robot/movement_groups.json`.
- **Two mappers plus movement-group persistence**: `RobotSettings` and `RobotCalibrationSettings` still use their own flat mappers, while movement groups are saved separately in the same user action.
- **`movement_groups` is not in the flat dict**: `MovementGroupsTab` has its own `get_values() → Dict[str, MovementGroup]` method. The controller reads both `get_values()` and `get_movement_groups()` separately and passes them to `model.save()`.
- **Declaration-driven movement groups**: the robot system declares ids and semantics; the UI renders those declarations and the JSON file stores only values.
- **Collapsed-by-default schema groups**: tabbed schema sections are rendered with the shared `CollapsibleSettingsView`, so every group starts collapsed and can be expanded independently.
- **Declared slot pickup/dropoff groups**: slot pickup/dropoff trajectories should be declared in `movement_groups`, not synthesized from saved tool assignments. Slot declarations bind each slot to the relevant pickup/dropoff group ids, and the shared tool runtime resolves through those bindings.
- **Reusable app, robot-system adapters**: The application remains generic. Robot-system-specific targeting structures are converted to and from the editor payload in the wiring/service layer.
- **Standard shared app**: If a robot system uses the shared `RobotSettings` and `RobotCalibrationSettings` engine models, it should reuse this application rather than creating a robot-system-specific copy.
- **No broker subscriptions**: `RobotSettingsController.stop()` is a no-op. The application does not receive live data.
- **Backend-confirmed collision settings**: the collision tab loads the live monitor configuration and saves through the robot service. The backend is authoritative and must echo the applied state; the UI does not treat a local field change as applied until the request succeeds.
- **Primary and secondary detectors are separate**: the external-torque observer is the primary detector. The effort-plus-following-error detector is optional and has its own enable switch and per-joint thresholds.

→ Subpackages: [service/](service/README.md) · [model/](model/README.md) · [view/](view/README.md) · [controller/](controller/README.md)

<!-- source-navigation:start -->
## Source navigation

[Module reference](MODULES.md) — signatures, fields, imports and source links for every Python file in this directory.

| Source subdirectory | Guide |
|---|---|
| `controller/` | [controller](controller/README.md) |
| `localization/` | [localization](localization/README.md) |
| `model/` | [model](model/README.md) |
| `service/` | [service](service/README.md) |
| `view/` | [view](view/README.md) |

[Complete source index](../../SOURCE_INDEX.md).
<!-- source-navigation:end -->
