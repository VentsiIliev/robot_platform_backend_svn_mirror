# Paint domain adapters and storage services

This package adapts workpiece contour schemas, paint segment selection, user schemas, repository data and editor/library contracts to paint-system behavior. `workpieces/repository/` owns paint JSON workpiece storage; `workpieces/service/` owns storage operations; the library service adapts them to the shared library application.

`contour_editor_schema.py`, `paint_workpiece_editor_adapter.py` and `paint_segment_selection.py` define paint-specific editor fields/geometry interactions. Camera capture, shared path preparation and robot motion are injected from composition rather than owned by a Qt model. System-specific storage paths must be resolved from the active paint variant, even though these implementations are shared.

<!-- source-navigation:start -->
## Source navigation

[Module reference](MODULES.md) — signatures, fields, imports and source links for every Python file in this directory.

| Source subdirectory | Guide |
|---|---|
| `users/` | [users](users/README.md) |
| `workpieces/` | [workpieces](workpieces/README.md) |

[Complete source index](../../../SOURCE_INDEX.md).
<!-- source-navigation:end -->
