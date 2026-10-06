# Paint execution collaborators

`PaintWorkpiecePathExecutor` is the facade implementing the shared editor path-execution contract. It resolves live config, targeting/poses and preview data, and delegates pickup, contact painting, robot motion, edge cleanup and dropoff to separate executors. This layer can issue robot/peripheral operations; it is not data-only geometry.

`execution_plane/` supplies plane strategies; `projection_preview.py` produces editor overlays/snapshots. `paint_debug_artifacts.py` and `diagnostics.py` support diagnostics. Planning data arrives from `plan/` and shared engine path preparation; business phase sequencing is owned by the production execution machine.

Pause/stop checks, fresh-pose confirmation, ordering of vacuum/contact/retract moves and failure propagation are part of execution semantics. Consult the source-backed signatures and guide before changing these contracts. Preview/diagnostic output does not establish that hardware reached a target.

<!-- source-navigation:start -->
## Source navigation

[Module reference](MODULES.md) — signatures, fields, imports and source links for every Python file in this directory.

| Source subdirectory | Guide |
|---|---|
| `execution_plane/` | [execution_plane](execution_plane/README.md) |

[Complete source index](../../../../../SOURCE_INDEX.md).
<!-- source-navigation:end -->
