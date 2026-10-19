# `src/robot_systems/paint/domain/workpieces`

This page follows the source directory. The reference below records its modules and contracts; follow child guides for nested implementations.

[Parent guide](../README.md).

## Paint library presentation and duplication

`PaintWorkpieceLibraryService` supplies the shared [Workpiece Library](../../../../applications/workpiece_library/README.md) with paint-owned field definitions. Name, description, and height are editable; the business workpiece ID remains read-only. Repository list metadata includes bounding dimensions calculated from the already-read JSON, so cards can show dimensions without another geometry read for every thumbnail.

The service implements the optional `IWorkpieceDuplicator` capability. `duplicate(storage_id)` loads the original JSON, assigns a new UUID-based `workpieceId`, appends ` (copy)` to its name, and calls `PaintWorkpieceService.save`. Saving uses the normal repository transaction to create a new storage folder, JSON file, and thumbnail. The original record and its geometry remain unchanged. Missing source records and save failures return an unsuccessful result for the library to display.

Matching selection continues to use storage IDs, not display names or business IDs. Duplicating a record does not explicitly change an existing matching selection: select-all mode includes newly available records; an explicit selection keeps its existing IDs.

The shared workpiece editor exposes Help with per-control onboarding, including Undo, Redo, and Nudge. See the [editor guide](../../../../applications/workpiece_editor/README.md#onboarding-tour) for available targets and the requirement to load and expand rows before touring segment and point controls.

Verification includes `tests/robot_systems/paint/test_paint_workpiece_storage.py`, with a real temporary repository test checking separate storage/business IDs, preserved geometry, a generated thumbnail, and an unchanged original after duplication.

<!-- source-navigation:start -->
## Source navigation

[Module reference](MODULES.md) — signatures, fields, imports and source links for every Python file in this directory.

| Source subdirectory | Guide |
|---|---|
| `repository/` | [repository](repository/README.md) |
| `service/` | [service](service/README.md) |

[Complete source index](../../../../SOURCE_INDEX.md).
<!-- source-navigation:end -->
