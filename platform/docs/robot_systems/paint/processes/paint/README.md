# Paint production package

This is the shared production implementation used by the paint family. System classes own storage, profile restrictions and runtime wiring; this package owns paint orchestration and its collaborators.

| Package/module | Responsibility |
|---|---|
| `paint_process.py` | Process state, background run, stop worker, manual/adjustment/retry entry points |
| `paint_production_service.py` | Capture, magazine/production flow and business execution-machine coordination |
| `config.py`, config service/serializer | Typed defaults, validated persisted configuration and runtime snapshots |
| [match](match/README.md) | Saved-workpiece candidate selection, matcher adapter and diagnostics |
| [align](align/README.md) | Raw contour payload IO, normalization and sampling helpers |
| [plan](plan/README.md) | Raw workpiece preparation, pickup transfer and paint-contact planning |
| [motion](motion/README.md) | Pose comparison, fresh-pose sampling and path geometry helpers |
| [execute](execute/README.md) | Path-executor facade, pickup/contact/motion/dropoff/cleanup collaborators and preview |
| [execution_machine](execution_machine/README.md) | Business states, context, transitions and per-phase handlers |
| [destination](destination/README.md) | Workpiece destination abstraction |
| [tray_dry](tray_dry/README.md) | Plate-layout reservations, occupancy and placement |
| [auto_dryer](auto_dryer/README.md) | Dryer release coordination |

`PaintWorkpiecePreparationService` returns a matched saved payload when matching is available/enabled and succeeds. Failed matching in that mode returns `Unknown workpiece`; it does not silently fall back to the captured contour. A captured-contour fallback is used when matching is disabled/unavailable. Shared path preparation converts the raw payload into a `WorkpieceExecutionPlan` before pickup/contact planning.

Cooperative execution controls coordinate pause, resume and stop across the active context, magazine navigation and path execution. The business machine includes magazine phases, capture/prepare/plan, pickup, paint contact, edge cleanup, prepare/dropoff/post-return and lifecycle states. See [trajectory/execution](TRAJECTORY_AND_EXECUTION.md) for responsibilities and [alignment](ALIGNMENT.md) for the current geometry path.

Plate layout separates reservations from committed occupied records. Outlines support dashboard placement display; conservative footprints support allocation. Automatic-dryer coordination and tray dropoff are selected/configured at composition/runtime rather than duplicated into separate full process packages.

The current tree no longer has `align/alignment/core.py`, `align/dxf_image_placement.py` or `execute/pivot_projection/core.py`. Earlier descriptions are retained in [archive](../../../../archive/robot_systems/paint/processes/paint/README.md), not treated as current APIs.

<!-- source-navigation:start -->
## Source navigation

[Module reference](MODULES.md) — signatures, fields, imports and source links for every Python file in this directory.

[Resource reference](RESOURCES.md) — non-Python files and their formats; values remain in the owning storage/source files.

| Source subdirectory | Guide |
|---|---|
| `align/` | [align](align/README.md) |
| `auto_dryer/` | [auto_dryer](auto_dryer/README.md) |
| `destination/` | [destination](destination/README.md) |
| `execute/` | [execute](execute/README.md) |
| `execution_machine/` | [execution_machine](execution_machine/README.md) |
| `match/` | [match](match/README.md) |
| `motion/` | [motion](motion/README.md) |
| `plan/` | [plan](plan/README.md) |
| `tray_dry/` | [tray_dry](tray_dry/README.md) |

[Complete source index](../../../../SOURCE_INDEX.md).
<!-- source-navigation:end -->
