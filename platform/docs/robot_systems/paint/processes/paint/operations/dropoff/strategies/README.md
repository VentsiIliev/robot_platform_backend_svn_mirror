# Dropoff strategies

Each strategy module owns its behavior:

- `plate_layout.py`: geometry and reservation, painting detach, combined entry contribution, routing, preparation, release, occupancy commit, and reservation cancellation.
- `movement_group.py`: optional combined preparation, movement-group plans, verified release, passage exit, return target, and destination handoff.
- `configured.py`: selection and cycle binding. Selection is pinned from `begin_cycle()` until `finish_cycle()`, and the binding is released even if finalization raises.

The workflow handles typed results and executes contributed commands. It does not inspect plate-layout configuration or reservation objects. Painting requests an optional detach pose through the interface; edge cleanup requests a strategy-owned approach extension.

Shared implementation helpers remain in `../motion.py`. Existing configuration/start-readiness policy and access to runtime fields remain separate follow-up boundaries.

[Operation guide](../README.md). [Module reference](MODULES.md).
