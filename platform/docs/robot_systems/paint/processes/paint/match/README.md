# Paint saved-workpiece matching

`PaintWorkpieceMatchingService` implements the shared editor matcher interface using injected repository list/load callbacks, selected-ID filtering, a matching function and optional capture snapshots. `MatchableWorkpiece` adapts stored data to the vision matcher and back to a raw payload. Diagnostic saving is optional and does not change a successful/failed match result.

An unavailable matching dependency, empty candidate set, no match, failed conversion or exception returns an explicit failure. Successful results include identity, raw data, candidate/no-match counts and optional confidence. The actual matching implementation is injected by system composition; this package adapts it rather than supplying the removed standalone alignment solver.

<!-- source-navigation:start -->
## Source navigation

[Module reference](MODULES.md) — signatures, fields, imports and source links for every Python file in this directory.

[Complete source index](../../../../../SOURCE_INDEX.md).
<!-- source-navigation:end -->
