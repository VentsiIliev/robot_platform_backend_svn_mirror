# JSON repository persistence

`BaseJsonSettingsRepository` uses the serializer contract and the shared durable
file helper in `src/engine/core/durable_files.py`. Reads never create or repair files.

## Load policy

`load_result()` returns `LoadResult(status, value, detail)`. Status is `OK`,
`MISSING`, `EMPTY`, `CORRUPT`, or `INACCESSIBLE`. Empty bytes are different from a
valid empty object. Duplicate keys, nonfinite numbers, invalid encoding and
non-object JSON are rejected. Domain validation remains the serializer's job;
existing serializer field defaults are unchanged.

`load()` returns the validated value or raises `SettingsLoadError` with a status.
Only `required=False` plus a missing file may return defaults, with a warning.
Those defaults remain in memory; loading never writes them. Empty, corrupt or
unreadable optional files also raise, preserving the original evidence.

The settings factory passes `SettingsSpec.required` to the repository. Existing
specs default to required. Missing required data must be explicitly provisioned
for a clean installation or restored for an established installation.

## Write policy

Explicit `save()` serializes and validates the value before publishing it. A
same-directory unique temporary file is written, flushed and fsynced, then
replaced atomically; the parent directory is fsynced. Existing ownership and mode
are preserved (failure to preserve them fails the write); new files default to
0600. Symlink and non-regular destination files are rejected. Handled failures
clean up temporary files. Abrupt process termination may leave hidden temporary
files, which are never interpreted as committed data.

Errors before replacement leave the previous file intact. Errors after replacement
raise a `SettingsSaveError` with `published=True`: the new file is visible but
crash durability is unconfirmed. Do not report these as an unchanged file or
silently retry a larger business operation. Inspect/reload before recovery.

Per-store sidecar locks serialize writes across repository instances/processes.
Whole-settings saves remain last-writer-wins; locks do not merge independently
edited snapshots. The stable `.lock` file must not be deleted while writers run.

## Cache behavior

`SettingsService` returns independent copies, so editing a retrieved settings
object cannot modify the active cache before save. Load/save/cache operations are
serialized. Failed reloads and saves evict the cached value; the next `get()` must
read the repository again. Other processes' successful writes still require an
explicit reload to refresh a running service.

## Repository coverage

- Settings: strict reads, required policy, durable writes and isolated cache.
- Permissions: strict schema, no missing-file creation, fresh reads, locked full
  read-modify-write and 0600 publication. A failed pre-publication save cannot
  change effective permissions.
- Glue workpieces: durable JSON replacement; corrupt loads and inventory reads
  raise instead of silently omitting records. Thumbnails remain derived assets.
- Paint workpieces: existing JSON/thumbnail staged publication is retained, with
  durable staging, directory synchronization and cross-instance update/read locks.
  Incomplete or durability-uncertain updates block production reads and retain
  recovery evidence. UI listings may log and skip unusable records.
- Twin choreography: unique durable replacement and strict JSON inventory reads.
- Updater state: reuses the same atomic helper; updater locking semantics remain
  unchanged. Standalone updater packaging includes the shared helper.

Factory seeding only creates missing files in a clean settings directory. Missing
files inside established settings storage require explicit provisioning/recovery;
new release settings must be provisioned by a deliberate migration, not inferred
from absence.

## Recovery and deployment

Before deploying, back up settings, permissions and workpiece libraries. Verify
all declared required settings and permissions files exist and parse correctly.
A permissions file must contain an object mapping app IDs to role lists. For a
clean installation, explicitly provision the intended policy; do not reset an
established file to `{}` just to pass startup.

Stop affected processes before restoring trusted backups. Preserve damaged files
and paint `.incomplete` markers/staging for diagnosis. Validate restored data with
its serializer/repository before allowing operation. A blocked paint record needs
both JSON and thumbnail restored consistently before its marker is removed.

This change does not add automatic last-known-good restoration, a recovery GUI,
schema migrations, installation identity, or CSV enrollment changes. It does not
make several separate JSON saves one transaction. Those remain separate work.

## Verification

Fault-injection and concurrency tests live in `tests/engine/core/test_durable_files.py`
and `tests/engine/repositories/test_json_persistence_failures.py`, with repository,
workpiece, choreography and updater regression suites alongside them. Tests use
temporary files and fake services; no hardware operation is needed.
