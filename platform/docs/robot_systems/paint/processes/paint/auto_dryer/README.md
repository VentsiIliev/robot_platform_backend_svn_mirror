# Automatic-dryer release coordination

`DryerReleaseCoordinator` coordinates paint dropoff/release with the injected dryer service. It is paint-owned process integration; register transport, dryer status and low-level next-position behavior belong to `src/engine/hardware/dryer/`.

Readiness, movement acknowledgement and successful workpiece release are separate conditions. This collaborator is configured/injected by paint composition rather than copied into each system variant. Exact requests, state and reset/stop entry points are recorded in the module reference.

<!-- source-navigation:start -->
## Source navigation

[Module reference](MODULES.md) — signatures, fields, imports and source links for every Python file in this directory.

[Complete source index](../../../../../SOURCE_INDEX.md).
<!-- source-navigation:end -->

## Standalone simulation

`simulation_runner.py` simulates consecutive dryer release cycles without hardware. Run `python src/robot_systems/paint/processes/paint/auto_dryer/simulation_runner.py --cycles 3`. It verifies fresh move/done/eject progression even when a stale DONE remains from the preceding cycle.
