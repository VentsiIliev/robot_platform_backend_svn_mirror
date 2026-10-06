# `src/robot_systems/paint/domain/workpieces`

This page follows the source directory. The reference below records its modules and contracts; follow child guides for nested implementations.

[Parent guide](../README.md).

<!-- source-navigation:start -->
## Source navigation

[Module reference](MODULES.md) — signatures, fields, imports and source links for every Python file in this directory.

| Source subdirectory | Guide |
|---|---|
| `repository/` | [repository](repository/README.md) |
| `service/` | [service](service/README.md) |

[Complete source index](../../../../SOURCE_INDEX.md).
<!-- source-navigation:end -->

## Required thumbnail and safe publication

Saving/updating requires successful JSON serialization and nonempty thumbnail bytes. Preparation writes and flushes both files in a local staging directory before publication. New records become visible by renaming the prepared directory. Updates replace the thumbnail first and JSON last, retaining the old thumbnail for rollback. A repository lock serializes its reads/writes. Failures raise `WorkpieceWriteError` with workpiece and stage context; the existing service failure result reaches the library's Save Failed warning.

An incomplete-update marker blocks listing/loading during publication. If rollback or marker cleanup fails, the record stays blocked and recovery files remain at the path in the error. Do not remove the marker until the JSON/thumbnail pair is checked and repaired. Normal failures preserve the old pair and remove staging files. There is no deferred thumbnail creation for new saves. Existing legacy thumbnail-read fallback is unchanged.

The two-file update is not a filesystem transaction: abrupt termination can leave a marked record requiring manual recovery. This change does not guarantee power-loss durability or concurrent transactions across separate processes. Tests cover serialization, missing/failed thumbnails, staging writes, publication, rollback and blocked-record behavior.
