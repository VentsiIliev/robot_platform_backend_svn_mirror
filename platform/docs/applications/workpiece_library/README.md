# Workpiece Library

The shared library displays saved workpieces as list cards or a thumbnail grid, with an inspector on the right. Robot systems supply their own schema and storage service; the shell and its navigation stay unchanged.

## Operator workflow

- Search by name or storage ID. Recent sorts newest dates first; Name sorts alphabetically; Height sorts numerically from low to high.
- Switch between list and grid without changing the selected record. Cards show available names, descriptions, dates, dimensions, and height; thumbnails load for visible records.
- Select a card to inspect its preview, dimensions, business ID, point count, path length, and saved date. The date is the storage date, not a tracked last-edit timestamp.
- Edit schema-owned fields in the inspector. Name and description use the shared virtual keyboard; height uses `KeyboardNumberField` with numeric entry and minus/plus controls. Save changes becomes available when values differ from the saved record. Sorting and language switching preserve unsaved values for the same selected record.
- Open in Editor loads the selected record through the existing broker/navigation flow. Delete requires confirmation. These actions are disabled when no record is selected.
- When a system supplies matching selection, Select reveals checkboxes, Select All, Clear Selection, and Show Selected. Changes persist immediately. Checked storage IDs survive search and view-mode changes; `None` represents all available workpieces.
- Duplicate appears only for services implementing the optional `IWorkpieceDuplicator` capability. Paint currently implements this capability.

## Ownership and contracts

`WorkpieceLibraryView` renders schema-owned fields, card delegates, and the inspector. `LibraryCardDelegate` paints cards without allocating a widget for each record. The view emits user-action signals; it does not access storage or the broker.

`IWorkpieceLibraryService` provides `get_schema`, `list_all`, `update`, `delete`, `get_thumbnail`, and `load_raw`. `IWorkpieceDuplicator` separately declares `duplicate(storage_id) -> (success, message)` so existing services need not implement unsupported copying.

`WorkpieceLibraryModel` delegates storage operations, refreshes its record cache after successful writes, and calculates read-only preview statistics from raw geometry. `WorkpieceLibraryController` maintains search/matching filters and thumbnail caching, handles confirmation and errors, and connects actions to the model. After metadata changes, it refreshes its search cache and reapplies the active filter.

`domain/geometry_summary.py` reads the stored outline and `sprayPattern.Contour` / `sprayPattern.Fill` polylines. It reports stored point count, bounding dimensions, and the sum of distances between consecutive path points without joining independent paths. If no process paths exist, length falls back to the closed outline (or the single open line for two points). These are stored-geometry measurements in the workpiece coordinate units displayed as millimeters, not robot timing or a post-interpolation path estimate. Missing geometry displays dashes.

## Open-in-editor flow

The controller loads the selected storage ID, publishes `WorkpieceTopics.OPEN_IN_EDITOR` with `{"raw": raw, "storage_id": storage_id}`, and publishes `ShellTopics.NAVIGATE` for `WorkpieceEditor`. A delayed repeat of the open event supports lazy editor creation. The system's editor loader handles conversion and arms saving as an update of the selected record.

## Localization and styling

English and Bulgarian UI strings live under `src/applications/workpiece_library/localization/`, using `WorkpieceLibraryView` and `WorkpieceLibrary` contexts. Runtime retranslation preserves unsaved field values. Record names, descriptions, IDs, and combo options remain user data. Styling uses the shared platform palette and action styles.

## Verification

```bash
QT_QPA_PLATFORM=offscreen .venv/bin/python -m unittest discover -s tests/applications/workpiece_library -v
QT_QPA_PLATFORM=offscreen .venv/bin/python -m unittest tests.robot_systems.paint.test_paint_workpiece_storage tests.robot_systems.glue.test_workpiece_library_plugin_integration -v
```

The tests cover list/grid selection, numeric sorting and height edits, dirty-save state, filtering after writes, matching selection persistence, language switching, geometry measurements, and independent paint duplication.

<!-- source-navigation:start -->
## Source navigation

[Module reference](MODULES.md) — signatures, fields, imports and source links for every Python file in this directory.

| Source subdirectory | Guide |
|---|---|
| `controller/` | [controller](controller/README.md) |
| `domain/` | [domain](domain/README.md) |
| `localization/` | [localization](localization/README.md) |
| `model/` | [model](model/README.md) |
| `service/` | [service](service/README.md) |
| `view/` | [view](view/README.md) |

[Complete source index](../../SOURCE_INDEX.md).
<!-- source-navigation:end -->
