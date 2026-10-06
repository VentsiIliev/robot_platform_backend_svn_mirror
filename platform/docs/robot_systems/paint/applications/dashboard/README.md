# `src/robot_systems/paint/applications/dashboard`

This page follows the source directory. The reference below records its modules and contracts; follow child guides for nested implementations.

[Parent guide](../README.md).

## Start availability during stopping

The dashboard keeps the existing process-state display and disables Start while the previous production worker or hardware-stop worker is still active. `PaintDashboardService.load_state()` sets `can_start=False` during cleanup; process-state events and periodic dashboard refreshes apply this value to the button. Once both workers exit, the next refresh restores Start availability for `IDLE` or `STOPPED`. The process independently rejects premature starts, including calls outside the dashboard.

Process Status details show "Waiting for paint stopping to finish." during cleanup and "Stopping is taking longer than expected." after ten seconds. English and Bulgarian translations are provided. A delayed stop keeps Start disabled; there is no automatic restart or timeout bypass. See the [production guide](../../processes/paint/README.md) for cancellation and worker-lifetime behavior.

<!-- source-navigation:start -->
## Source navigation

[Module reference](MODULES.md) — signatures, fields, imports and source links for every Python file in this directory.

| Source subdirectory | Guide |
|---|---|
| `assets/` | [assets](assets/README.md) |
| `controller/` | [controller](controller/README.md) |
| `model/` | [model](model/README.md) |
| `service/` | [service](service/README.md) |
| `ui/` | [ui](ui/README.md) |
| `view/` | [view](view/README.md) |

[Complete source index](../../../../SOURCE_INDEX.md).
<!-- source-navigation:end -->
