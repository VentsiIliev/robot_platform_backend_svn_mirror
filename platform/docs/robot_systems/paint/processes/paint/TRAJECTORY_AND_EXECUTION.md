# Paint planning and execution

Current execution is composed from shared path preparation, paint-specific transfer/contact planning and a business execution machine. The old `execute/pivot_projection/core.py` path is absent.

## Plans and coordinates

`DefaultWorkpiecePathPreparationService` produces the shared `WorkpieceExecutionPlan` from raw workpiece geometry and targeting context. Its job/pickup/path fields are documented in [path preparation](../../../../engine/robot/path_preparation/README.md). This plan is input to paint-specific motion planning, not a promise that its points are already final robot waypoints.

`PaintPickupTransferPlanner` in `plan/pickup_transfer_planner.py` builds pickup/transfer poses. `plan/paint_contact_motion/source_plan.py` prepares source contact data; `core.py` projects continuous contact motion and supports rebasing initial rotation. `execute/execution_plane/strategies.py` selects plane behavior. Exact axes, offsets, pass tuning and projection defaults are defined by typed configuration and the active snapshot.

`execute/projection_preview.py` builds editor-facing projected paths/snapshots. Preview is not robot execution; diagnostic figures and cached editor results do not establish successful hardware movement.

## Execution ownership

`PaintWorkpiecePathExecutor` implements the shared editor path-execution contract and delegates phases to `PaintPickupExecutor`, `PaintMotionExecutor`, `PaintContactExecutor`, `PaintEdgeCleanupExecutor` and `PaintDropoffExecutor`. Its facade also resolves current configuration, poses and preview behavior.

The production `PaintExecutionMachineFactory` wires handlers for magazine loading, capture, preparation, plan construction, pickup, contact paint, cleanup, dropoff and post-return. `PaintExecutionState` and `PaintExecutionTransitions` define legal business transitions. The legacy `EXECUTE_PAINT` path and the split pickup/contact/dropoff path coexist in the state contract; exact route depends on construction/configuration.

Pause/resume use cooperative run gates and execution control; stop sets stop events and requests hardware halt. Terminal handlers normalize state/cleanup. Failed motion, unavailable fresh pose, failed matching or a blocked dropoff must be assessed through the returned result/error state, not only command submission.

The public process may already be `STOPPED` while production cancellation or the hardware-stop worker is still finishing. `PaintProcess` rejects new runs until both workers have exited, and the dashboard keeps Start disabled during that interval. Per-run cancellation remains set across reset, and completion is serialized with Stop/reset so cancelled workers cannot publish late results. See the [production guide](README.md) for delayed-stop feedback and the start/retry entry points covered by the guard.

Plate-layout and automatic-dryer paths have their own destination/release coordination. Reservation, committed occupancy, vacuum release, return motion and dryer readiness are separate operations. See [tray](tray_dry/README.md) and [dryer](auto_dryer/README.md).

For exact APIs/defaults use [plan](plan/README.md), [execute](execute/README.md) and [execution machine](execution_machine/README.md). The [previous projection/order description](../../../../archive/robot_systems/paint/processes/paint/TRAJECTORY_AND_EXECUTION.md) is retained for historical context and must not be used as a fixed execution sequence.

## Motion completion and failures

Paint uses `Ros2Robot` exclusively. Pickup ordered chains, paint contact trajectories, incremental adjustment sections and edge-cleanup trajectories/chains use blocking calls and accept only integer `0` as completed success. Booleans, `None`, queued results and other nonzero outcomes follow the existing failure path instead of recording completed motion or advancing the last successful pose. Production failures enter `ERROR` and require operator action. Explicit pause/resume retains its existing interrupted non-contact motion retry behavior.

## Finite configured waypoints

Configured waypoint parsing rejects NaN and positive/negative infinity in X/Y/Z/RX/RY/RZ, velocity, acceleration and blend radius. Errors identify the field and, when parsing a sequence, its one-based waypoint number. An invalid waypoint fails the operation rather than silently skipping a route segment. `ConfiguredMotionWaypoint` also enforces finite fields on direct construction. Blend-radius validation occurs before the existing negative-to-zero clamp; finite settings and supported motion modes retain their behavior.
