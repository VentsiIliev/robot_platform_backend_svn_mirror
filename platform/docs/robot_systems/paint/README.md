# `src/robot_systems/paint/` — Paint Robot System

`PaintRobotSystem` is the concrete robot-system package for automated edge painting. It combines:

- a declaration-heavy robot-system class in `paint_robot_system.py`
- robot-system-specific application wiring in `application_wiring.py`
- paint-domain process logic under `processes/paint/`
- supporting paint-domain adapters for workpieces, DXF import, targeting, calibration, and vacuum control

This document is the entry point for the paint system. Use it together with:

- [DIAGNOSTICS.md](DIAGNOSTICS.md)
- [applications/README.md](applications/README.md)
- [processes/README.md](processes/README.md)
- [processes/paint/ALIGNMENT.md](processes/paint/ALIGNMENT.md)
- [processes/paint/TRAJECTORY_AND_EXECUTION.md](processes/paint/TRAJECTORY_AND_EXECUTION.md)
- [../../pivot_painting_reference.md](../../pivot_painting_reference.md)

---

## Package Map

```text
src/robot_systems/paint/
├── paint_robot_system.py              # robot-system declaration + runtime composition
├── application_wiring.py             # lazy builders for apps and paint runtime services
├── navigation.py                     # paint-specific navigation facade
├── calibration/                      # calibration provider + coordinator adapter
├── targeting/                        # targeting provider + frame/point builders
├── domain/                           # paint-specific schemas, adapters, repositories
├── processes/
│   └── paint/                        # paint production process package
├── applications/dashboard/           # paint dashboard MVC package
├── service_builders.py               # paint-only service builders (vacuum pump)
└── storage/                          # default paint system data and translation catalogs
```

### System-owned configuration and storage

The dryer variants reuse `PaintRobotSystem` through subclasses defined in their
own packages. Each bootstrap provider applies its package's
`paint_system_config.py` overrides without changing shared defaults.

| System | Concrete class module | Source storage root |
|--------|-----------------------|---------------------|
| Default paint | `paint/paint_robot_system.py` | `src/robot_systems/paint/storage/` |
| Automatic dryer | `paint_auto_dry/paint_robot_system.py` | `src/robot_systems/paint_auto_dry/storage/` |
| Tray dryer | `paint_tray_dry/paint_robot_system.py` | `src/robot_systems/paint_tray_dry/storage/` |

Each root owns settings, users, permissions, workpieces, targeting data, and
translation catalogs. Shared process and application code remains under `paint`.
`metadata.settings_root` is `storage/settings` for all three systems; the dryer
systems set `metadata.translations_root` to `storage/translations`.
The defining module determines `package_root()`, and configuration overrides
preserve that module identity.

With `ROBOT_PLATFORM_DATA_ROOT` set, writable paths resolve beneath
`<data_root>/<system>/storage/`. Translation catalogs remain bundled resources
under the respective system package. Legacy `paint/profiles/<profile>/storage/`
is migrated during installed update activation; see
[the update storage documentation](../../engine/updates/README.md).

---

## System Declaration

**File:** `src/robot_systems/paint/paint_robot_system.py`

`PaintRobotSystem` declares the shell, settings, services, movement groups, target points, target frames, work areas, and role policy that the platform consumes through `SystemBuilder`.

### Movement, targeting and work-area declarations

Current movement-group IDs include `HOME`, `CALIBRATION`, `JOG`, `Horizontal Shaft`, `Vertical Shaft`, `Vertical Shaft Alignment`, `Clean`, `Dropoff`, `Magazine`, and `Magazine Fixed Pickup`. The older `PAINTING` / `PAINTING_NEW` names are not the current class declarations. Their pose/velocity values remain settings-owned.

Remote TCP points are `camera` and `tool`. Target frames and work areas include `calibration`/`paint`, `magazine`, and `vertical_shaft_alignment`, with observer bindings to their respective movement groups. The default active work area is `paint`. Tool/slot declarations and role/application metadata also live on the class; use [the source reference](MODULES.md) for their exact fields and values.

---

## Settings

Default paint settings are rooted under `src/robot_systems/paint/storage/settings/`.
The dryer variants use their own roots listed above, with the same relative
settings file paths.

| Key (`CommonSettingsID`) | File | Purpose |
|--------------------------|------|---------|
| `ROBOT_CONFIG` | `robot/config.json` | generic robot runtime and tool offsets |
| `MOVEMENT_GROUPS` | `robot/movement_groups.json` | persisted named positions |
| `ROBOT_CALIBRATION` | `robot/calibration.json` | robot/camera calibration settings |
| `TARGETING` | `targeting/definitions.json` | target-point and target-frame persistence |
| `CALIBRATION_VISION_SETTINGS` | `vision/calibration_settings.json` | calibration-specific camera settings |
| `VISION_CAMERA_SETTINGS` | `vision/camera_settings.json` | runtime vision settings |
| `WORK_AREA_SETTINGS` | `vision/work_areas.json` | paint work-area polygons and ROI state |
| `HEIGHT_MEASURING_SETTINGS` | `height_measuring/settings.json` | laser/height-measuring settings |
| `HEIGHT_MEASURING_CALIBRATION` | `height_measuring/calibration_data.json` | height calibration data |
| `DEPTH_MAP_DATA` | `height_measuring/depth_map.json` | stored height-map data |

Non-settings storage owned by the paint system:

- `storage/users/users.csv`
- `storage/workpieces/`

### Workpiece editor geometry

The paint editor keeps two independent contour representations:

- `contour` / **Workpiece** is the complete captured boundary used for saved-workpiece matching and pickup alignment.
- `sprayPattern.Contour` / **Paint** is the RTCP process contour. For a new capture or a legacy workpiece with no saved paint sections, the editor initializes this layer with a complete copy of the matching boundary.

Editing the Paint layer therefore does not modify the canonical matching contour. The initial copy also provides the source geometry for the planned rectangle-selection workflow, where operators will turn parts of the complete contour into explicit RTCP paint sections.

To define the executed sections, activate **Rectangle Select** from the editor tools, drag over neighboring contour points, and press the paint-roller action. Each contiguous run selected from the canonical Workpiece outline is copied into `sprayPattern.Contour`. The first selection removes the initial complete Paint copy; later selections append more paint sections. The orange Workpiece contour is retained unchanged.

RTCP still projects one continuous portion of the complete Workpiece contour. Paint segments act as a contact mask: selected regions remain at the configured pivot contact, gaps between them retract 5 mm along the paint axis with a 5 mm transition ramp. Planning starts at the first selected region and cuts the contour after the last selected region, avoiding an unnecessary remainder traversal.

### Unmatched two-pass painting

Captured contours executed without a library match can run one or two paint passes. Pass one keeps the legacy default velocity, acceleration, and press-offset keys. Pass two either inherits those values dynamically or uses its own overrides.

For two passes, the ordered robot chain is built before execution as `pass 1 → detach → Joint 6 unwind → pass 2 attach → pass 2 → detach`. The backend may preplan later segments, but executes each only after the preceding protected segment succeeds. The prepared workpiece execution plan is reused; capture, contour preparation, matching, and interpolation are not repeated. Matched workpieces remain single-pass and retain their segment-owned settings.

---

## Services

### Declared services

| Name | Type | Required | Source |
|------|------|----------|--------|
| `ROBOT` | `IRobotService` | yes | shared default builder |
| `NAVIGATION` | `NavigationService` | yes | shared default builder |
| `WORK_AREAS` | `IWorkAreaService` | yes | shared default builder |
| `VISION` | `IVisionService` | no | shared default builder |
| `VACUUM_PUMP` | `IVacuumPumpController` | no | `build_vacuum_pump_service()` |

### Runtime-only paint services composed in `on_start()`

These are not `ServiceSpec` declarations. They are robot-system-owned runtime objects created after shared services and settings are available:

- `PaintNavigationService`
- `PaintRobotSystemTargetingProvider`
- height-measuring services via the shared engine builder
- calibration services via the shared engine builder
- `PaintCalibrationCoordinator`
- `PaintWorkpiecePathExecutor`
- `PaintWorkpieceMatchingService`
- `PaintWorkpiecePreparationService`
- `PaintProductionService`
- `PaintProcess`
- `PaintDashboardService`

---

## Shell And Applications

The paint shell currently exposes four folders:

| Folder | `folder_id` |
|--------|-------------|
| Production | `1` |
| Service | `2` |
| Administration | `3` |
| Tests | `4` |

Applications are documented in [applications/README.md](applications/README.md).

---

## Runtime Lifecycle

### `on_start()`

At startup the paint robot system:

1. resolves shared robot, navigation, work-area, and optional vision services
2. builds `PaintNavigationService`
3. loads robot and targeting settings into runtime fields
4. registers the optional vision service before starting it
5. builds height-measuring services
6. builds calibration services and the paint calibration coordinator
7. builds workpiece-editor, snapshot, path-preparation, executor, matching, and preparation services
8. creates one shared `PlateLayoutService` and injects it into the executor, production service and dashboard
9. builds and registers `PaintProcess`, requiring healthy robot service state for RUNNING transitions
10. builds `PaintDashboardService`
11. enables the robot

### `on_stop()`

Shutdown first prevents new paint runs, cancels the active phase, requests a
hardware halt and waits for the production and stop workers outside the process
lock. The default worker deadline is five seconds. A missed deadline raises
`ShutdownPendingError`, retaining hardware ownership for a subsequent `stop()`
attempt. Once workers finish, the system stops motion and attempts to disable
the robot even if the final stop command raises. Shared managed-resource cleanup
then closes remaining dependencies.

Cycle faults and explicit process errors halt motion while preserving the
current vacuum command; ordinary operator Stop retains its vacuum-off behavior.
Drop-off handlers use the public `IDropoffStrategy` / `DropoffResult` boundary;
executor bookkeeping stays inside the executor. See
[recovery and ownership](../paint_tray_dry/RECOVERY.md) for light retries,
startup rollback, timeout handling and commissioning checks.

---

## Navigation, Targeting, And Calibration

### Navigation

**File:** `src/robot_systems/paint/navigation.py`

`PaintNavigationService` is a paint-specific facade over the shared `NavigationService`. It adds:

- paint-specific convenience moves such as `move_home()` and `move_to_calibration_position()`
- optional capture Z-offset application through the vision service
- active-work-area updates after successful moves

### Targeting

**Files:** `targeting/provider.py`, `targeting/frames.py`, `targeting/registry.py`

`PaintRobotSystemTargetingProvider` merges declared target definitions with persisted targeting settings and exposes:

- point registry construction
- frame construction for work areas
- target options for UI use
- work-area/frame resolution helpers

### Calibration

**Files:** `calibration/provider.py`, `calibration/coordinator.py`

The paint system reuses the shared engine calibration services, but supplies:

- a paint-specific calibration navigation adapter
- a thin coordinator around `RobotCalibrationProcess`

---

## Paint Production Architecture

The actual painting workflow lives under `src/robot_systems/paint/processes/paint/`.

High-level flow:

1. capture a fresh vision snapshot
2. select the usable contour
3. prepare a raw workpiece payload
4. build an execution plan
5. execute pickup, staging, pivot-path painting, and cleanup moves

The package is now structured by responsibility:

- `align/`: image-space placement and contour alignment
- `plan/`: matching and workpiece preparation
- `execute/`: pickup planning, pivot projection, plane strategies, and debug artifacts

Detailed process documentation lives in [processes/paint/README.md](processes/paint/README.md).

---

## Domain Modules

Important paint-domain packages outside the process runtime:

| Path | Responsibility |
|------|----------------|
| `domain/contour_editor_schema.py` | paint-specific editor form schemas |
| `domain/dxf_path_form_behavior.py` | DXF import behavior in the workpiece editor |
| `domain/paint_workpiece_editor_adapter.py` | bridges generic editor payloads with paint workpiece data |
| `domain/workpieces/` | repository and service layer for stored paint workpieces |
| `domain/users/paint_user_schema.py` | paint-system user schema |
| `domain/vacuum_pump/` | vacuum-pump transport/controller implementations |

---

## Application Wiring

**File:** `src/robot_systems/paint/application_wiring.py`

`application_wiring.py` is the composition root for paint applications and paint-process support services. It owns:

- widget-application factory functions used by `shell.applications`
- shared robot-system service builders for the workpiece editor and paint process
- paint-process configuration lookups from `PAINT_PROCESS_CONFIG`

This file is the best starting point when tracing how a paint UI screen gets its dependencies.

---

## Tests

The paint system has focused behavioral coverage under `tests/robot_systems/paint/`.

Important slices:

- `test_paint_system_integration.py`
- `test_paint_process_integration.py`
- `test_paint_workpiece_alignment.py`
- `test_paint_pivot_projection.py`
- `test_paint_execution_plane_strategies.py`
- `test_paint_workpiece_path_executor.py`

These tests are the main safety net for future refactors inside the `align / plan / execute` structure.

When workpiece matching is enabled but no saved workpiece matches the captured contour, the
dashboard stops paint execution and shows a **Workpiece not recognized** dialog
with Scan again, Open library, and Dismiss actions. The warning also remains in
the dashboard message list. Scan again recaptures at the current paint position
without returning to the magazine for another workpiece. The complete captured
contour is used only when
matching is disabled. A successfully matched workpiece
without explicit paint segments still uses its complete saved contour as the paint mask.
For matched workpieces with saved paint segments, production builds the plan through the
paint executor so those segments become the RTCP contact mask over the main contour.
Paint selection saving never reorders the main workpiece contour; seam-crossing selections
are stored as one paint segment while preserving the matching and pickup reference geometry.

---

## Related Docs

- [applications/README.md](applications/README.md)
- [processes/README.md](processes/README.md)
- [processes/paint/README.md](processes/paint/README.md)
- [../../pivot_painting_reference.md](../../pivot_painting_reference.md)
- [../paint_process_refactor_review.md](../paint_process_refactor_review.md)

## Update source

This system owns [storage/update_source.json](../../../src/robot_systems/paint/storage/update_source.json),
selected through its `update_source` entry in `config/release_targets.json`.
The checked-in seed uses `feed` with remote updates disabled; existing station
`updates.json` files are preserved. See [per-system source configuration](../update_sources.md)
for URLs, authentication, trust and migration.

<!-- source-navigation:start -->
## Source navigation

[Module reference](MODULES.md) — signatures, fields, imports and source links for every Python file in this directory.

[Resource reference](RESOURCES.md) — non-Python files and their formats; values remain in the owning storage/source files.

| Source subdirectory | Guide |
|---|---|
| `applications/` | [applications](applications/README.md) |
| `calibration/` | [calibration](calibration/README.md) |
| `destinations/` | [destinations](destinations/README.md) |
| `domain/` | [domain](domain/README.md) |
| `hardware/` | [hardware](hardware/README.md) |
| `processes/` | [processes](processes/README.md) |
| `storage/` | [storage](storage/README.md) |
| `targeting/` | [targeting](targeting/README.md) |

[Complete source index](../../SOURCE_INDEX.md).
<!-- source-navigation:end -->

## Tool-change position guard

Paint declares `tool_change_group = "Tool Changer"`. Tool pickup, drop-off, and
Tool Settings editor runs require a fresh robot pose at the configured
`Tool Changer` movement-group position before taught steps execute. The guard checks all six
axes with the capture guard's tolerances (10 mm per position axis, 5 degrees per
rotation axis). Missing configuration or unverifiable feedback blocks execution.
With **Start from Tool Changer** off, move there through navigation before
running the sequence. Enabling it adds an initial navigation move and arrival
check. **Finish at Tool Changer** adds the final navigation move. The switches
are independent for pickup and drop-off and are saved with each sequence.
