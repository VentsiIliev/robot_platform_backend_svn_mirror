# `src/robot_systems/paint/domain/workpieces/service`

This page follows the source directory. The reference below records its modules and contracts; follow child guides for nested implementations.

[Parent guide](../README.md).

Production matching uses `list_for_matching()` and `load_for_matching()` so read failures propagate to its typed boundary. Missing records may return `None`; unreadable or invalid saved data raises `WorkpieceReadError` with exception chaining. Legacy `list_all()`/`load_raw()` retain their tolerant library behavior. These policies must remain separate: an empty library or absent record is different from failed storage access.

<!-- source-navigation:start -->
## Source navigation

[Module reference](MODULES.md) — signatures, fields, imports and source links for every Python file in this directory.

[Complete source index](../../../../../SOURCE_INDEX.md).
<!-- source-navigation:end -->
