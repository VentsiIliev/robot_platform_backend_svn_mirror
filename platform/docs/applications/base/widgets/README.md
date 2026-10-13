# `src/applications/base/widgets`

This page follows the source directory. The reference below records its modules and contracts; follow child guides for nested implementations.

[Parent guide](../README.md).

## Fluid progress

`fluid_progress.py` provides three native PyQt6 progress visuals: `InkBar`,
`PlumeLine`, and `Vessel`. They support determinate progress and an indeterminate
waiting state through `set_progress()`, `set_running()`, and `set_waiting()`.

Application views should construct them through
`create_fluid_progress(style)`. Supported style names are `"ink"`, `"plume"`,
and `"vessel"`; using the factory keeps visual selection separate from
application behavior. The widgets use the shared `pl_gui` palette and must only
be updated from the GUI thread.

<!-- source-navigation:start -->
## Source navigation

[Module reference](MODULES.md) — signatures, fields, imports and source links for every Python file in this directory.

[Complete source index](../../../SOURCE_INDEX.md).
<!-- source-navigation:end -->
