# `src/robot_systems/paint/hardware`

This page follows the source directory. The reference below records its modules and contracts; follow child guides for nested implementations.

[Parent guide](../README.md).

<!-- source-navigation:start -->
## Source navigation

[Module reference](MODULES.md) — signatures, fields, imports and source links for every Python file in this directory.

[Complete source index](../../../SOURCE_INDEX.md).
<!-- source-navigation:end -->

## Paint vacuum coordination

`PaintVacuumControl` in `vacuum_control.py` applies pickup/release policy to the platform `IVacuumPumpController`. It receives only the controller and a live enabled-state provider. Required-but-disabled or unavailable vacuum fails pickup; nonblocking release retains its separate blow-off command. Platform transport and device control stay under `src/engine/hardware/`.
