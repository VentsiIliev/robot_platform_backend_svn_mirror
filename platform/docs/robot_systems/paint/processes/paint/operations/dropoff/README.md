# Dropoff operation and interchangeable strategies

The runtime receives an `IDropoffStrategy` through `PaintExecutorDependencies.dropoff_strategy_factory`. Robot-system composition selects the implementation. Pickup, painting, edge cleanup, and terminal workflow handlers depend on generic lifecycle hooks rather than concrete strategy types.

## Cycle contract

1. `begin_cycle(DropoffCycleRequest)` reserves destination capacity before pickup and returns a typed refusal, capacity outcome, or completion. The request carries the prepared workpiece, pickup geometry, and a lazy calibration-source callback. Movement-group dropoff does not read that calibration source.
2. `painting_detach_pose(...)` optionally supplies a destination handoff pose at the end of painting.
3. `plan_paint_approach(cleanup_pending=...)` contributes commands to the pickup/paint chain. `plan_cleanup_approach(final_pose)` contributes commands after edge cleanup.
4. `activate_approach(approach)` establishes required passage state before execution. `approach_completed(approach)` records only a successful combined-chain execution, avoiding repeated preparation and unwind.
5. `prepare_dropoff()` and `release_dropoff(next_cycle_start)` complete remaining preparation, release, and exit. `DropoffResult` retains failure, capacity, and prepositioning metadata.
6. `finish_cycle(result)` runs on every terminal path. The plate strategy cancels pending reservations on unsuccessful outcomes. Cleanup attempts the other resources even if finalization fails and preserves the primary failure with a secondary cleanup failure.

`DropoffApproach` is the command contribution and completion receipt. The workflow appends its commands and passes the record back without interpreting destination-specific completion fields.

## Implementations

- `strategies/plate_layout.py` owns footprint/orientation calculations, reservation, painting handoff, entry/exit routing, distributed unwind, release, occupancy commit, capacity reporting, and cancellation.
- `strategies/movement_group.py` owns movement-group preparation, safe approach contributions, release plans, passage exit, return-target verification, and external handoff notification.
- `strategies/configured.py` selects a built-in implementation from the cycle configuration. It pins that selection when reservation starts and releases it during finalization, including when cleanup raises. Its selected identity is also used by legacy shared pose resolvers.

`motion.py` retains shared pose/passage/verification helpers, cleanup-approach construction, and thin dispatch entry points for older callers. `plan.py` defines the lower-level waypoint-plan contract. `executor.py` executes waypoint plans with its existing default movement-group planner.

## Injecting another strategy

Implement every hook in `src/robot_systems/paint/contracts/dropoff.py` and supply its factory from robot-system composition:

```python
dependencies = PaintExecutorDependencies(
    robot_service=robot_service,
    dropoff_strategy_factory=lambda runtime: CustomDropoff(runtime),
    # other runtime inputs
)
```

A destination without reservations or painting handoff returns a completed begin result and no detach pose. A strategy that contributes no approach returns an empty `DropoffApproach`. Generic phase coordination does not need another enum branch.

## Remaining boundaries

The built-in implementations still use execution-runtime fields for motion state and injected services. The existing production start-readiness checks and alternating-drying policy still use configured modes. This refactor extracts cycle reservation, handoff, command contribution, completion, and finalization; it does not yet replace every runtime field with a standalone cycle-session object.

[Module reference](MODULES.md).
