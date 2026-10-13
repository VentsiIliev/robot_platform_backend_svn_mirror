# Module reference: `src/robot_systems/paint/contracts`

[Package guide](README.md). Generated from source ASTs; no runtime imports.

## `__init__.py`

[Source](../../../../src/robot_systems/paint/contracts/__init__.py).


## `dropoff.py`

[Source](../../../../src/robot_systems/paint/contracts/dropoff.py).

- `DropoffResult`: See source for contract.
- `DropoffCycleRequest`: Workpiece and pickup geometry plus lazy calibration-position access.
- `DropoffApproach`: Commands contributed to a combined chain and their completion receipt.
- `IDropoffExecution`: Preparation/release boundary used by production orchestration.
- `IDropoffStrategy`: Own reservation, painting handoff, approach, release, and finalization.

## `next_cycle_target.py`

[Source](../../../../src/robot_systems/paint/contracts/next_cycle_target.py).

- `NextCycleTarget`: Validated robot target used to preposition for the next paint cycle.
