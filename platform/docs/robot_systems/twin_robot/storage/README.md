# `src/robot_systems/twin_robot/storage`

This page follows the source directory. The reference below records its modules and contracts; follow child guides for nested implementations.

[Parent guide](../README.md).

<!-- source-navigation:start -->
## Source navigation

[Module reference](MODULES.md) — signatures, fields, imports and source links for every Python file in this directory.

[Complete source index](../../../SOURCE_INDEX.md).
<!-- source-navigation:end -->

## Durable JSON persistence

JSON publication uses the shared engine durable-file helper. Read failures are not silently converted to empty production data. See the repository-wide persistence contract in `docs/engine/repositories/json/README.md` for failure states and recovery. Paint retains its staged JSON/thumbnail transaction and blocks incomplete records; its UI listing may log and omit unusable records.
