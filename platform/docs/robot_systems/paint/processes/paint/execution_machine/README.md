# Paint business execution machine

`PaintExecutionContext` carries runtime collaborators, per-run inputs/results, cooperative stop/run events and progress/error context. `PaintExecutionMachineFactory` assembles the state registry and `ExecutableStateMachine`. `PaintExecutionState` and `PaintExecutionTransitions` define the business graph, independently of the outer `BaseProcess` lifecycle state.

The graph contains optional magazine pickup/release/camera-settle phases, workpiece capture/preparation/plan construction, either combined execution or split pickup/contact/cleanup/dropoff/post-return phases, and pause/completed/stopped/error/idle states. Paused execution resumes to a remembered active phase rather than treating every resume as a brand-new process.

The current business state describes where execution is; the typed context result describes its outcome. Expected absence, cancellation and capacity limits are declared at their sources, rather than inferred from messages. Pickup planning consumes `Ready[PickupPlan]`/`Failed`; ordered attempts distinguish `NOT_APPLICABLE` from failed execution, and waypoint counts describe planned paths rather than verified physical progress.

The handler boundary translates known paint/tray exceptions to an error transition. Unexpected exceptions are logged with tracebacks and recorded as `INTERNAL` failures before running terminal cleanup. Terminal cleanup independently attempts motion-session restoration, reservation cancellation when appropriate, brightness restoration and live-view restoration. Cleanup failures are chained and attached to a primary failure when one exists; terminal exceptions never re-enter the same cleanup state indefinitely. Optional timing export cannot prevent restoration of the previous execution control or closure of the timing session.

Handlers are grouped by magazine loading, common motion/guards, workflow, dropoff and lifecycle. Plan/preparation failures, stop events and terminal cleanup are explicit transition paths. Configuration and the factory decide the active route; a list of enum states is not an unconditional command order.

See each handler reference for constructor dependencies and `handle(context)` behavior, and [production guide](../README.md) for ownership above this machine.

<!-- source-navigation:start -->
## Source navigation

[Module reference](MODULES.md) — signatures, fields, imports and source links for every Python file in this directory.

| Source subdirectory | Guide |
|---|---|
| `handlers/` | [handlers](handlers/README.md) |

[Complete source index](../../../../../SOURCE_INDEX.md).
<!-- source-navigation:end -->
