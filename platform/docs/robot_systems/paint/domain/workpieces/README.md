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

## Storage path confinement

A storage ID is a single nonempty folder name, not a file path or the JSON `workpieceId`. Absolute paths, dot/dot-dot IDs, separators (including backslashes) and NUL characters are rejected. Existing generated IDs and other valid single-component legacy IDs remain supported. Missing valid IDs retain their existing absence behavior.

Record resolution enforces containment under the canonical storage root and rejects symlinks in date directories, record directories, JSON and thumbnail paths. Unsafe records are omitted from library listings. Reads/updates reject unsafe paths; deletion resolves the validated record before removing its directory. New-save paths are checked too. The root itself may be configured through a symlink and is canonicalized at initialization.

Tests use disposable external fixtures to verify invalid IDs cannot read, update or delete outside files and symlink records cannot escape confinement. This protects against malformed IDs and existing symlinks; it is not a race-resistant filesystem sandbox against another process replacing directories during an operation.
