# `welding` — Welding robot-system composition

`WeldingRobotSystem` declares robot/navigation/work-area services and optional vision, settings, work-area/target-frame definitions, role policy and shell applications. The active work area is `welding`; calibration uses its declared observer binding. The existing movement-group ID `WELDINGING` is literal persisted identity, not a translated UI identifier.

Startup wraps navigation in `WeldingNavigationService`, starts/manages optional vision, constructs targeting/height/calibration providers, creates a shared robot-calibration process/coordinator and a welding dashboard process/service, then enables the robot. `on_stop()` stops motion and disables the robot; managed resource teardown is provided by the base system.

The main `WeldingProcess` is currently a timed simulation (default three seconds), with timer cancellation on stop/pause/reset and a new timer on resume. It does not implement a production welding cycle. `requirements` defaults to none. The contour editor/path executor is a separate integration path and must not be taken as proof that the dashboard process performs welding.

Shared screens include robot/camera/work-area/calibration settings, calibration, network settings, software update, broker debug and user management; this system also exposes intrinsic capture and hand-eye calibration through its composition. Its own dashboard lives in `applications/dashboard/`. Role policy protects administration/update access. See [module reference](MODULES.md) for exact declarations and [processes](processes/README.md) for the simulated process contract.

Settings use standard robot, movement-group, calibration, targeting, vision and height-measuring serializers under system storage. Deployment identity and backend selection are declared separately in `config`; selecting welding requires a complete `robot_systems.welding` startup entry.

<!-- source-navigation:start -->
## Source navigation

[Module reference](MODULES.md) — signatures, fields, imports and source links for every Python file in this directory.

[Resource reference](RESOURCES.md) — non-Python files and their formats; values remain in the owning storage/source files.

| Source subdirectory | Guide |
|---|---|
| `applications/` | [applications](applications/README.md) |
| `calibration/` | [calibration](calibration/README.md) |
| `domain/` | [domain](domain/README.md) |
| `height_measuring/` | [height_measuring](height_measuring/README.md) |
| `processes/` | [processes](processes/README.md) |
| `storage/` | [storage](storage/README.md) |
| `targeting/` | [targeting](targeting/README.md) |

[Complete source index](../../SOURCE_INDEX.md).
<!-- source-navigation:end -->
