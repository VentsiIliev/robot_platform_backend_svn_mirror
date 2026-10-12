# `paint_auto_dry` — Automatic-dryer paint variant

`AutomaticDryerPaintRobotSystem` inherits the shared `PaintRobotSystem` runtime. It replaces metadata with `PaintSystemAutomaticDryer` and owns settings/translations under its own module's `storage/`. The bootstrap provider applies this package's `paint_system_config` overrides through `with_paint_system_overrides()`; unspecified switches inherit shared paint defaults without mutating another system.

The override module is intentionally empty in this checkout. The variant class does not independently replace all paint services, process handlers or dropoff configuration. Machine/profile behavior also depends on persisted settings and factory defaults. See [shared paint](../paint/README.md), [automatic dryer coordination](../paint/processes/paint/auto_dryer/README.md) and [configuration](../../config/README.md).

Release identity is `paint-auto-dry-robot`, profile `automatic_dryer`; packaging includes shared `paint` plus `paint_auto_dry`. Source and installed writable storage remain variant-owned. Follow `ROBOT_PLATFORM_DATA_ROOT` path resolution in [updates](../../engine/updates/README.md).

## Update source

This system owns [storage/update_source.json](../../../src/robot_systems/paint_auto_dry/storage/update_source.json),
selected through its `update_source` entry in `config/release_targets.json`.
The checked-in seed uses `feed` with remote updates disabled; existing station
`updates.json` files are preserved. See [per-system source configuration](../update_sources.md)
for URLs, authentication, trust and migration.

<!-- source-navigation:start -->
## Source navigation

[Module reference](MODULES.md) — signatures, fields, imports and source links for every Python file in this directory.

[Resource reference](RESOURCES.md) — non-Python files and their formats; values remain in the owning storage/source files.

| Source subdirectory | Guide |
|---|---|
| `storage/` | [storage](storage/README.md) |

[Complete source index](../../SOURCE_INDEX.md).
<!-- source-navigation:end -->
