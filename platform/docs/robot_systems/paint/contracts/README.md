# Paint-system contracts

Contracts here bridge components owned by the paint robot system. They can be imported by production and applications without importing either implementation. Engine-to-system contracts remain in `src/shared_contracts/`.

[Events](events/README.md).

`dropoff.py` defines the injected reservation, painting handoff, approach, preparation/release, and finalization interface and `DropoffResult`. `next_cycle_target.py` defines validated prepositioning data shared by production and dropoff implementations. These contracts are owned by the paint system.

`DropoffCycleRequest` supplies workpiece/pickup inputs and lazy calibration access. `DropoffApproach` carries command contributions plus their completion receipt. Consumers pass these through the lifecycle interface without interpreting the selected destination.

`IDropoffExecution` is the narrower preparation/release boundary consumed by production orchestration. `IDropoffStrategy` extends it with cycle ownership and motion-plan hooks. The execution runtime implements the narrow boundary by delegating to its injected full strategy.
