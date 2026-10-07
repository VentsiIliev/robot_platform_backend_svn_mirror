# Paint saved-workpiece matching

`PaintWorkpieceMatchingService` implements the shared editor matcher interface using injected repository list/load callbacks, selected-ID filtering, a matching function and optional capture snapshots. `MatchableWorkpiece` adapts stored data to the vision matcher and back to a raw payload. Diagnostic saving is optional and does not change a successful/failed match result.

`match_result()` returns `Ready[MatchedWorkpiece]`, `NoMatch`, or `Failed`. Empty candidates and an unmatched contour are absence outcomes. Unavailable dependencies, conversion failures and exceptions are failures; candidate-loading I/O failures carry `STORAGE`, while unexpected bugs carry `INTERNAL` and retain a logged traceback. `MatchedWorkpiece` explicitly names raw data, identity, candidate/no-match counts and optional confidence. `match_saved_workpieces()` adapts this result to the unchanged shared editor tuple/dictionary contract. Production preparation is wired to the typed matcher and strict workpiece repository reads; legacy injected matcher callbacks cannot recover categories that their tuple contract discarded. The actual matching implementation is injected by system composition; this package adapts it rather than supplying the removed standalone alignment solver.

<!-- source-navigation:start -->
## Source navigation

[Module reference](MODULES.md) — signatures, fields, imports and source links for every Python file in this directory.

[Complete source index](../../../../../SOURCE_INDEX.md).
<!-- source-navigation:end -->
