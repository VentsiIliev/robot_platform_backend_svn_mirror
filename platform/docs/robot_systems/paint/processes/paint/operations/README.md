# Workpiece operations

This package contains pickup, painting, edge cleanup, and dropoff. Each operation performs one workpiece-level action and returns its established result contract.

- [Pickup](pickup/README.md): pickup planning and execution, including contact-sensor pickup.
- [Painting](painting/README.md): projected painting-contact trajectories and approach/retreat motion.
- [Edge cleanup](edge_cleanup/README.md): optional cleanup passes and their ordered-chain segments.
- [Dropoff](dropoff/README.md): dropoff contracts and destination execution.

Shared move submission and interrupted-motion recovery live in [motion](../motion/README.md). Vacuum control lives in the [robot-system hardware package](../../../hardware/README.md). Incremental operator-paced execution lives in [adjustment](../adjustment/README.md), projections in [planning](../planning/README.md), and tracing/exports in [diagnostics](../../../diagnostics/README.md).

The [production runtime](../production/README.md) composes these operations. The [editor adapter](../adapters/README.md) exposes editor actions without owning production state. Existing operation collaborators still access runtime state through their owner; private-field coupling remains, while dropoff route and release algorithms now live in the dropoff operation behind an injected lifecycle strategy.

[Module reference](MODULES.md).
