# `src/engine/updates/` — Platform Releases and Updates

Pure-Python release installation, verification, migration, and rollback. Qt-free
and ROS-free: nothing here imports the GUI, and no module runs at import time.

Operational instructions — building, signing, publishing, and applying releases —
live in [`packaging/platform/README.md`](../../../packaging/platform/README.md);
this document covers the code itself.

---

## Files

| File | Contents |
|------|----------|
| `config.py` | `UpdateConfig`, `default_config_path()`, `default_install_root()` |
| `updater.py` | `PlatformUpdater`, `_HttpsRedirect` |
| `releases.py` | `version_tuple()`, `validate_manifest()`, `extract_release()`, `release_executable()`, `release_identity()` |
| `migrations.py` | `migrate()` |
| `factory_defaults.py` | `load_factory_defaults()`, `seed_factory_defaults()`, `ALLOWED_FILES` |
| `files.py` | `atomic_json()`, `lock()`, `sync_directory()`, `sync_tree()` |
| `environment.py` | `subprocess_environment()` |
| `paths.py` | `system_path()` |

---

## Filesystem Layout

```
~/.local/share/robot-platform/           ← install_root (paint-robot legacy location)
├── current        → releases/<version>   ← symlink, the active release
├── releases/<version>/
│   ├── manifest.json
│   ├── platform/…                        ← extracted release tree
│   └── migrations/<n>.json
├── data/                                 ← mutable, machine-owned (settings, storage)
├── backups/<uuid>/                       ← data snapshots taken by apply/rollback
└── update-state/
    ├── update.lock, runtime.lock         ← cooperative fcntl locks
    ├── latest.json / staged.json / pending.json
    ├── transaction.json                  ← journal of an interrupted activation
    ├── rollback.json, result.json
```

`data/` is machine-owned and **never** shipped inside a release archive;
`releases/` is software-owned and never carries live data. `apply_pending()`
refuses to run if `data/` contains a symlink.

---

## `config.py`

```python
@dataclass(frozen=True)
class UpdateConfig:
    install_root: Path
    repository_url: str
    public_key: Path | None
    product: str = "paint-robot"
    channel: str = "stable"
    enabled: bool = False
    timeout_seconds: int = 30
    max_download_bytes: int = 4 * 1024**3
    max_extracted_bytes: int = 8 * 1024**3

    @property
    def local_repository(self) -> Path | None: ...
```

Frozen, because it is validated once at load and then trusted by every download
and extraction call.

### `default_config_path(product=None)`

Resolution order:

1. `$ROBOT_PLATFORM_UPDATE_CONFIG`
2. `~/.config/robot-platform/<product>/updates.json`
3. **Legacy exception** — for `product == "paint-robot"`, if
   `~/.config/robot-platform/updates.json` already exists it is kept, preserving
   the first paint install's configuration location

`product` falls back to `$ROBOT_PLATFORM_PRODUCT`, then `"paint-robot"`.

### `default_install_root(product)`

Returns `~/.local/share/robot-platform` for `paint-robot` **when** that directory
already contains `current/` or `data/` (legacy layout), otherwise
`~/.local/share/robot-platform/products/<product>`.

### `UpdateConfig.load(path=None)`

Reads the JSON file and validates it hard — every failure raises `ValueError`:

| Check | Message |
|-------|---------|
| Top level is an object | "Update configuration must be an object" |
| `enabled` is a bool | "enabled must be a boolean" |
| `install_root` is absolute | "install_root must be absolute" |
| `repository_url` is a string | "repository_url must be a string" |
| Enabled + non-local URL must be HTTPS, no credentials/query/fragment | "Enabled updates require an absolute local folder or HTTPS repository_url without credentials/query" |
| `product` / `channel` match `[A-Za-z0-9_-]+` | "Invalid product" / "Invalid channel" |
| `public_key` is a string or null | "public_key must be a quoted file path or null" |
| `public_key` is absolute when set | "public_key must be absolute" |
| Enabled ⇒ public key present and a file, **or** local repository | "Enabled updates require an installed public_key" |
| `timeout_seconds`, `max_download_bytes`, `max_extracted_bytes` positive ints (bools rejected) | "… must be a positive integer" |

The `repository_url` is stored with a trailing `/` stripped then re-appended
(`repository.rstrip("/") + "/"`), and `install_root` is `.resolve()`d.

`local_repository` returns a `Path` only when `repository_url` starts with `/` —
that single test distinguishes a local feed folder from an HTTPS endpoint.

---

## `releases.py`

### `version_tuple(value)`

```python
VERSION = re.compile(r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$")
```

Rejects leading zeros and anything not `major.minor.patch`. Returns
`tuple[int, int, int]` for ordering comparisons. Raises `ValueError` otherwise.

### `validate_manifest(raw, product)`

Applies, in order:

1. `raw` is a dict, `format` ∈ `{1, 2}`, `product` matches the configured product
2. **Format 1 (legacy) only works with `product == "paint-robot"`**
3. Format 2 requires `robot_system`, `profile`, `storage_system`, `executable`
   each matching `[a-z][a-z0-9_-]*`
4. `version_tuple(raw["version"])`
5. `architecture == platform.machine()`
6. `os == "ubuntu-24.04"`, **and** the running OS is actually Ubuntu 24.04
   (`platform.freedesktop_os_release()`)
7. `storage_schema` is an `int >= 1`, rejecting `bool`

Returns `raw` unchanged on success.

### `extract_release(archive, destination, max_bytes)`

Extracts a `.tar.gz` with an explicit allow-list and no trust in the archive:

| Rejection | Condition |
|-----------|-----------|
| Unsafe path | absolute, `..`, empty parts, or `\` in the name |
| Unexpected content | top-level must be `platform`, `manifest.json`, or `migrations` |
| Special files | anything that is not a regular file or directory, **including symlinks and hardlinks** |
| Duplicates | a member name seen twice |
| Mutable data | any file under a `storage` or `profiles` path component — except under `translations` |
| Size | cumulative member sizes exceed `max_bytes` |
| Count | more than 100 000 entries |

Files are opened with `"xb"` (exclusive create) and permissions are set to
`0o755` when the member has any execute bit, else `0o644`.

It also verifies that `platform/<release_executable(manifest)>` exists **and is
executable**.

On **any** exception the destination directory is removed before re-raising, so a
partial extraction never becomes a candidate release.

### `release_executable(manifest)`

`"paint-robot"` for format 1; otherwise the manifest's `executable`, validated
against `[a-z][a-z0-9_-]*`.

### `release_identity(manifest)`

```python
format 1 → (product, "paint", "default")
format 2 → (product, robot_system, profile)
```

Used at every stage transition to guarantee an update can never switch robot
system or profile — see the constructor check below.

---

## `updater.py` — `PlatformUpdater`

```python
PlatformUpdater(config: UpdateConfig)
```

The constructor reads `current/manifest.json` and raises if its `product`
differs from `config.product`:

> "Installed robot system/profile cannot be changed through update configuration"

So identity is enforced at construction, not only at activation.

### Transport security — `_HttpsRedirect`

```python
class _HttpsRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, response, code, message, headers, new_url):
        if urllib.parse.urlparse(new_url).scheme != "https":
            raise ValueError("Update redirects must remain HTTPS")
        ...
```

Combined with the `_fetch()` scheme check, no path can downgrade to HTTP — not
even via a redirect.

### `_fetch(url, target, limit)`

| Repository | Behaviour |
|------------|-----------|
| **Local** (`local_repository` not `None`) | Opens the file directly, but only if its resolved parent is exactly the configured feed folder — a path escape outside the feed raises |
| **Remote** | Requires `https`, uses an opener with `_HttpsRedirect`, and honours `timeout_seconds` |

Streams in 1 MiB chunks and raises `"Update download limit exceeded"` as soon as
the running total passes `limit`, so a malicious server cannot fill the disk
before the check.

### `installed()`

Reads `current/manifest.json`; returns `None` when `current/` does not exist.

### `check() -> dict`

```
1. enabled?                      else RuntimeError("Updates are disabled…")
2. fetch <feed>/latest.json      (1 MiB limit)
3. fetch <feed>/latest.json.sig  (16 KiB limit) unless local repo with no key
4. openssl dgst -sha256 -verify <public_key> -signature <sig> <manifest>
5. validate_manifest(manifest, product)
6. channel must equal config.channel
7. archive: a plain *.tar.gz file name (no path separators, \, ?, #)
8. sha256: exactly 64 lowercase hex chars
9. release_identity must match the installed release
10. manifest["available"] = newer than installed (or first install)
```

Signature verification shells out to `openssl` with `check=True`,
`capture_output=True`, a 15 s timeout, and `subprocess_environment()`. The
signature check is skipped only for a local repository that has no public key —
an explicit local-folder bootstrap case.

Everything happens inside a `tempfile.TemporaryDirectory`, so nothing from the
feed persists.

### `stage_latest()` / `stage_local(archive)` / `_stage(archive, expected=None)`

Both entry points take `lock(state/update.lock)` first.

`stage_latest()` requires `manifest["available"]`, downloads the archive (limit
`max_download_bytes`), and compares its SHA-256 against the manifest before
staging.

`stage_local(archive)` is the documented bootstrap path for a trusted local file;
its docstring states *"remote releases always require signatures"* — no signature
is consulted here.

`_stage()`:

```
1. extract to releases/.staging-<uuid>       (extraction limits apply)
2. validate the extracted manifest
3. if expected: every identity field must match the signed manifest
      version, product, architecture, os, storage_schema, robot_system,
      profile, storage_system, executable
4. format 2 only:
      a. platform/_internal/config/release-target.json must agree with the
         manifest on product/robot_system/profile/storage_system/executable
      b. platform/_internal/config/platform.json must have robot_system ==
         manifest and supported_robot_systems == [manifest robot_system]
      c. load_factory_defaults() validates config/factory-defaults.json
5. release_identity must match the installed release
6. run <release executable> --self-test
      QT_QPA_PLATFORM=offscreen, cwd = platform/, 30 s timeout
7. destination releases/<version> must not already exist
      "publish a new version" otherwise
8. sync_tree(temporary) → os.rename → sync_directory(releases)
9. atomic_json(state/staged.json, manifest)
10. finally: remove the staging dir if it is still there
```

Step 6 is the gate that stops a structurally valid archive whose binary cannot
even start. The `finally` block keeps `releases/` clean on every failure path.

### `queue()`

Copies `staged.json` → `pending.json` under `update.lock`. Nothing happens until
`apply_pending()` runs.

### `offline()` — the concurrency primitive

```python
@contextmanager
def offline(self):
    with lock(self.state / "runtime.lock"), lock(self.state / "update.lock"):
        yield
```

`recover()`, `apply_pending()`, and `rollback()` all run inside it. Both locks
are taken with `LOCK_NB`, so if the platform is running (holding
`runtime.lock`) or another update is in progress, the caller gets
`RuntimeError("Platform is running or another update is in progress")` rather
than blocking. **Updates only ever apply while the platform is closed.**

### `_pointer(version)`

Rewrites the `current` symlink atomically:

```python
temporary.symlink_to(Path("releases") / version)   # .current-new
os.replace(temporary, self.root / "current")       # atomic swap
sync_directory(self.root)
```

`version_tuple()` is called first (validating the format) and the target
directory must exist.

### `_recover()` / `recover()` — interrupted-activation repair

If `state/transaction.json` exists, a previous activation did not finish. The
journal records `{"previous": <version or null>, "backup": <uuid>}`.

```
if backups/<backup> exists:
    if data/ exists:   rename it to .failed-data-<uuid>   (discard partial data)
    rename backups/<backup> → data/
if record["previous"]:  repoint current → previous
else:                   unlink current                     (never installed)
write result.json {status: "recovered", version: previous}
remove pending.json, transaction.json
```

`recover()` wraps this in `offline()`; `_recover()` does not, so
`apply_pending()` and `rollback()` can call it without re-taking locks they
already hold.

### `apply_pending() -> bool`

Runs entirely inside `offline()`, and **always calls `_recover()` first** — a
previously interrupted activation is repaired before anything new is attempted.

Returns `False` when there is no `pending.json` (nothing to do).

Otherwise:

```
1. read version, validate via version_tuple
2. read releases/<version>/manifest.json, validate_manifest
3. reject identity mismatch with the installed release
4. reject non-advancing updates: version <= installed → ValueError
5. mkdir data/
6. reject if data/ itself or any descendant is a symlink
7. copy data/ → .data-new-<uuid>            (staged copy)
8. migrate(staged, release, old_schema, new_schema)
     old = installed storage_schema, or 1 on first install
9. format 2 → seed_factory_defaults(release/platform/_internal, staged, manifest)
10. sync_tree(staged)
11. write transaction.json {previous, backup}
12. rename data/ → backups/<uuid>
13. rename .data-new-<uuid> → data/
14. _pointer(version)                        ← activation point
15. write rollback.json {previous, backup}
16. write result.json {status: "installed", version}
17. remove pending.json, staged.json, transaction.json
```

On **any** exception: `_recover()` restores the backup and previous pointer,
`pending.json` is removed, `result.json` records `{"status": "failed", "message": …}`,
and the exception re-raises. The `finally` block deletes the staging directory.

`BaseException` is caught deliberately, so `KeyboardInterrupt` during activation
triggers recovery rather than leaving a half-moved `data/`.

### `rollback()`

> "Explicitly restore previous software AND its pre-update data snapshot."

Also runs inside `offline()` and calls `_recover()` first.

```
1. read rollback.json; "No previous release available" if previous is null
2. backups/<backup> must exist, else "Rollback snapshot missing"
3. write transaction.json {previous: current version, backup: <new uuid>}
4. rename data/ → backups/<new uuid>       ← post-update data is preserved
5. copytree(backups/<backup> → data/)
6. sync_tree(data/)
7. _pointer(record["previous"])
8. result.json {status: "rolled_back", version: previous}
9. remove rollback.json, pending.json, transaction.json
```

Step 3–4 mean the rolled-back-from state is itself snapshotted, so **rollback is
reversible** — the code comment says exactly that: *"rollback is itself
recoverable."*

### `_digest(path)`

`hashlib.file_digest(stream, "sha256").hexdigest()`.

---

## `migrations.py`

```python
def migrate(data_root: Path, release: Path, old_schema: int, new_schema: int) -> None:
```

Applies `release/migrations/<n>.json` for each `n` in
`range(old_schema + 1, new_schema + 1)`. Downgrades raise
`"Storage schema downgrade requires restoring a backup"`.

Each file is a **list of operations**:

```json
[{ "file": "storage/settings/x.json", "path": ["a", "b"], "action": "rename", "to": "c" }]
```

| Action | Behaviour |
|--------|-----------|
| `add` | `setdefault(key, value)` — never overwrites an existing field |
| `remove` | `pop(key, None)` — a missing key is not an error |
| `rename` | Moves `key` → `to`; raises if `to` already exists ("would overwrite an existing field") or if `to` is empty/identical |

Validation per operation:

- `file` must be relative with no `..` and non-empty
- The resolved target must stay inside `data_root` ("Migration leaves data root")
- For `remove`/`rename`, a missing file or a missing intermediate path is
  **skipped silently** — migrations must be idempotent across partially-migrated
  installs
- `path` must be a non-empty list of non-empty strings; intermediate nodes must
  be objects
- Unknown actions raise

Every successful operation rewrites its file with `atomic_json`, so a crash
mid-migration never truncates a settings file.

---

## `factory_defaults.py`

```python
ALLOWED_FILES = frozenset({
    "hardware/peripherals.json", "hardware/modbus.json",
    "hardware/cameras.json", "dryer/settings.json",
})
```

### `load_factory_defaults(resource_root, identity)`

Reads `<resource_root>/config/factory-defaults.json`:

- Missing file → `{}` (legacy format-1 bundles have none)
- `format` must be `1` and `product`/`robot_system`/`profile` must match
  `identity` — otherwise *"Factory defaults belong to another robot
  system/profile"*
- `files` must be a dict whose keys are a **subset of `ALLOWED_FILES`** —
  *"Unsupported factory settings file"*
- Every value must be a JSON object

### `seed_factory_defaults(resource_root, data_root, identity) -> list[str]`

Creates **missing** settings files only; existing files — including empty ones —
are always left alone.

Target directory:

```
<data_root>/<storage_system>/storage/settings/            system-owned storage or default profile
<data_root>/<storage_system>/profiles/<profile>/storage/settings/   legacy shared profile storage
```

`paint_auto_dry` and `paint_tray_dry` own their storage directly. Their system
classes and source-run `storage/` directories live in the respective packages;
shared painting code remains in `paint`. During activation, legacy
`paint/profiles/automatic_dryer/storage/` or `paint/profiles/tray_dryer/storage/`
is relocated into the respective system directory in the staged data copy,
before factory defaults are seeded. Existing accounts, settings, and workpieces
are preserved, and rollback restores the previous layout. If both legacy and
destination storage exist, activation fails without replacing live data.
`--storage-from` accepts either the system package or the legacy paint package
containing the selected profile.

Per file:

1. Walk every parent up to `data_root.parent`; any symlink raises
   *"Factory settings cannot traverse data symlinks"*
2. `destination.exists()` → skip
3. `mkdir(parents=True)`
4. Write `atomic_json(.factory-<uuid>)` then `os.link(temporary, destination)`

The hard link is the atomicity primitive: a competing writer that creates the
same file first causes `FileExistsError`, which is caught and treated as *that
writer wins*. The temporary link is unlinked in `finally`.

Returns the list of created relative paths. Called from
`apply_pending()` step 9, so seeding happens on every release, not just the
first install.

---

## `files.py` — Durability Primitives

| Function | Contract |
|----------|----------|
| `sync_directory(path)` | `fsync` on an `O_DIRECTORY` fd — persists the directory entry itself, not just file contents |
| `atomic_json(path, value)` | Write to `mkstemp` in the same directory → `flush` → `fsync` → `os.replace` → `sync_directory(parent)`. Temp file removed in `finally` |
| `lock(path, shared=False)` | `fcntl.flock` with `LOCK_NB`; `BlockingIOError` → `RuntimeError("Platform is running or another update is in progress")`. Creates the parent directory |
| `sync_tree(root)` | `os.walk(bottomdown=False)` fsync-ing every file, then `sync_directory` for every directory — children before parents, so a tree is durable before it is published |

`atomic_json` plus `sync_directory` is the pattern behind every state file
(`staged.json`, `pending.json`, `transaction.json`, `rollback.json`,
`result.json`).

---

## `environment.py`

```python
def subprocess_environment() -> dict[str, str]:
```

Strips `PYTHONHOME`, `PYTHONPATH`, `VIRTUAL_ENV`, `QT_PLUGIN_PATH`,
`QT_QPA_PLATFORM_PLUGIN_PATH` so child processes are not contaminated by a
PyInstaller bundle's private libraries.

When `sys.frozen`, `LD_LIBRARY_PATH` is restored from `LD_LIBRARY_PATH_ORIG`
(or removed when there is no original). Finally it sets
`PYINSTALLER_RESET_ENVIRONMENT=1`.

Used for the `openssl` signature verification and the `--self-test` subprocess.

---

## `paths.py`

```python
def system_path(system_class, relative_path: str) -> str:
```

Resolves a **writable** robot-system path independently of where the software
is installed:

1. `$ROBOT_PLATFORM_DATA_ROOT` set →
   `<data_root>/<system>/<relative_path>`, where the system name is
   `system_class.__module__.split(".")[2]`
2. Otherwise → `system_class.package_root()` + relative path (source-run default)

Case 1 rejects absolute paths and any `..` component:
*"External storage requires a system-relative path"*. This is what keeps an
installed release's `data/` separate from a source checkout's `storage/`.

Called from `src/bootstrap/run_main.py`,
`src/robot_systems/paint/paint_robot_system.py`,
`src/robot_systems/base_robot_system.py`, and
`src/engine/repositories/settings_service_factory.py`.

---

## Consumers

| Caller | Uses |
|--------|------|
| `src/applications/software_update/service/software_update_service.py` | `UpdateConfig`, `default_config_path`, `PlatformUpdater` |
| `src/bootstrap/run_main.py` | `system_path` |
| `src/robot_systems/base_robot_system.py`, `paint_robot_system.py` | `system_path` |
| `src/engine/repositories/settings_service_factory.py` | `system_path` |
| `packaging/platform/` (build scripts) | Release format, manifest schema |

---

## Design Principles

- **Two-way trust boundary.** Archives are never trusted (allow-listed extraction,
  self-test, manifest cross-checks); release identity is never allowed to change
  robot system or profile.
- **Everything is journaled.** `transaction.json` makes an interrupted activation
  recoverable, and `rollback.json` makes a rollback itself reversible.
- **Durability is explicit.** Every publish is `fsync(file)` → `rename` →
  `fsync(dir)`; nothing relies on process exit to flush.
- **No blocking.** Both locks are `LOCK_NB`, so the updater can never hang
  waiting for a running platform — it fails fast instead.
- **Machine data and software are separate trees.** Releases carry no live data;
  `data/` carries no code; migrations and factory defaults are the only sanctioned
  bridge between them.
