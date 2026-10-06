# Paint raw-contour helpers

The active package exports payload IO/normalization and closed-path sampling helpers from `alignment/`. It does not contain the former standalone DXF image-placement or rigid/reference-smooth alignment solver. Saved-workpiece matching is in `match/`; execution input preparation is in `plan/`.

IO helpers extract/replace raw contour payloads and normalize point arrays. Sampling helpers calculate lengths/areas, resample closed paths, smooth paths and produce diagnostics. Private helpers are linked through their source modules even when not listed as public class APIs. See [current alignment guide](../ALIGNMENT.md).

<!-- source-navigation:start -->
## Source navigation

[Module reference](MODULES.md) — signatures, fields, imports and source links for every Python file in this directory.

| Source subdirectory | Guide |
|---|---|
| `alignment/` | [alignment](alignment/README.md) |

[Complete source index](../../../../../SOURCE_INDEX.md).
<!-- source-navigation:end -->
