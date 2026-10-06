# `src/robot_systems/paint/applications/paint_adjustment`

This page follows the source directory. The reference below records its modules and contracts; follow child guides for nested implementations.

[Parent guide](../README.md).

<!-- source-navigation:start -->
## Source navigation

[Module reference](MODULES.md) — signatures, fields, imports and source links for every Python file in this directory.

| Source subdirectory | Guide |
|---|---|
| `controller/` | [controller](controller/README.md) |
| `model/` | [model](model/README.md) |
| `service/` | [service](service/README.md) |
| `view/` | [view](view/README.md) |

[Complete source index](../../../../SOURCE_INDEX.md).
<!-- source-navigation:end -->

The shared guard covers pending serial actions, position reads and cycle commands, plus running, paused and stopping paint cycles. Camera streaming is excluded. The system passes stopping state through the cycle callback so Stop does not prematurely unlock navigation.
