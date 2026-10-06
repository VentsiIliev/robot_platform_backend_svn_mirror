# `paint_tray_dry` — Tray-dryer paint variant

`TrayDryerPaintRobotSystem` inherits shared paint runtime services and replaces metadata with `PaintSystemTrayDryer`. It hides the drying-mode control, limits allowed dropoff strategies to `plate_layout`, and replaces the paint-process serializer's fresh-install default with that strategy. Existing persisted settings are not rewritten merely by changing serializer defaults.

The provider applies only this package's configuration overrides; its override module is empty in the checkout. Settings/translations are resolved under this system's own `storage/`, including when implementation is inherited. Installed paths use `ROBOT_PLATFORM_DATA_ROOT`.

Release identity is `paint-tray-dry-robot`, profile `tray_dryer`, with shared `paint` and this variant packaged together. `config/platform.json` currently selects this variant; that selection is a checkout value, not a universal default. See [shared paint](../paint/README.md), [tray allocation](../paint/processes/paint/tray_dry/README.md) and [configuration](../../config/README.md).

<!-- source-navigation:start -->
## Source navigation

[Module reference](MODULES.md) — signatures, fields, imports and source links for every Python file in this directory.

[Resource reference](RESOURCES.md) — non-Python files and their formats; values remain in the owning storage/source files.

| Source subdirectory | Guide |
|---|---|
| `storage/` | [storage](storage/README.md) |

[Complete source index](../../SOURCE_INDEX.md).
<!-- source-navigation:end -->
