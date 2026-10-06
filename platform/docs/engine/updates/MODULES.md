# Module reference: `src/engine/updates`

[Package guide](README.md) · [Complete source index](../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [config.py](#configpy)
- [environment.py](#environmentpy)
- [factory_defaults.py](#factory_defaultspy)
- [files.py](#filespy)
- [migrations.py](#migrationspy)
- [paths.py](#pathspy)
- [releases.py](#releasespy)
- [updater.py](#updaterpy)

## `__init__.py`

Source: [src/engine/updates/__init__.py](../../../src/engine/updates/__init__.py).

Platform release installation and updates, independent of Qt and ROS.

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `config.py`

Source: [src/engine/updates/config.py](../../../src/engine/updates/config.py).

Machine-owned update configuration, never taken from a release archive.

Imports (including optional/function-local imports; not a startup dependency list): `dataclasses`, `json`, `os`, `pathlib`, `urllib.parse`.

### `default_config_path`

```python
def default_config_path(product: str | None=None) -> Path
```

### `default_install_root`

```python
def default_install_root(product: str) -> Path
```

### `UpdateConfig`

```python
@dataclass(frozen=True)
class UpdateConfig:
```

Declared fields/defaults:

```python
install_root: Path
repository_url: str
public_key: Path | None
product: str = 'paint-robot'
channel: str = 'stable'
enabled: bool = False
timeout_seconds: int = 30
max_download_bytes: int = 4 * 1024 ** 3
max_extracted_bytes: int = 8 * 1024 ** 3
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@property
def local_repository(self) -> Path | None
```

```python
@classmethod
def load(cls, path: Path | None=None)
```

## `environment.py`

Source: [src/engine/updates/environment.py](../../../src/engine/updates/environment.py).

Keep PyInstaller's private libraries out of independent subprocesses.

Imports (including optional/function-local imports; not a startup dependency list): `os`, `sys`.

### `subprocess_environment`

```python
def subprocess_environment() -> dict[str, str]
```

## `factory_defaults.py`

Source: [src/engine/updates/factory_defaults.py](../../../src/engine/updates/factory_defaults.py).

Seed authored factory settings without replacing machine-owned files.

Imports (including optional/function-local imports; not a startup dependency list): `.files`, `json`, `os`, `pathlib`, `uuid`.

Module declarations (expressions are shown without evaluating them):

```python
ALLOWED_FILES = frozenset({'hardware/peripherals.json', 'hardware/modbus.json', 'hardware/cameras.json', 'dryer/settings.json'})
```

### `load_factory_defaults`

```python
def load_factory_defaults(resource_root: Path, identity: dict) -> dict
```

Validate the selected product's templates; legacy bundles have none.

### `seed_factory_defaults`

```python
def seed_factory_defaults(resource_root: Path, data_root: Path, identity: dict) -> list[str]
```

Atomically create missing settings files, including on subsequent releases.

### `migrate_paint_profile_storage`

```python
def migrate_paint_profile_storage(data_root: Path, identity: dict) -> None
```

Relocate legacy paint data in the updater's staged copy before seeding.

## `files.py`

Source: [src/engine/updates/files.py](../../../src/engine/updates/files.py).

Durable state files and cooperative process locks for Linux installations.

Imports (including optional/function-local imports; not a startup dependency list): `contextlib`, `fcntl`, `json`, `os`, `pathlib`, `tempfile`.

### `sync_directory`

```python
def sync_directory(path: Path) -> None
```

### `atomic_json`

```python
def atomic_json(path: Path, value: object) -> None
```

### `lock`

```python
def lock(path: Path, *, shared: bool=False)
```

### `sync_tree`

```python
def sync_tree(root: Path) -> None
```

Persist file contents and directory entries before publishing a tree.

## `migrations.py`

Source: [src/engine/updates/migrations.py](../../../src/engine/updates/migrations.py).

Explicit JSON field migrations; unrelated values and files are preserved.

Imports (including optional/function-local imports; not a startup dependency list): `.files`, `json`, `pathlib`.

### `migrate`

```python
def migrate(data_root: Path, release: Path, old_schema: int, new_schema: int) -> None
```

## `paths.py`

Source: [src/engine/updates/paths.py](../../../src/engine/updates/paths.py).

Resolve mutable robot-system paths independently of installed software.

Imports (including optional/function-local imports; not a startup dependency list): `os`, `pathlib`.

### `system_path`

```python
def system_path(system_class, relative_path: str) -> str
```

Resolve a system-relative writable path; preserve source-run defaults.

## `releases.py`

Source: [src/engine/updates/releases.py](../../../src/engine/updates/releases.py).

Release format validation and extraction; archives never contain live data.

Imports (including optional/function-local imports; not a startup dependency list): `json`, `pathlib`, `platform`, `re`, `shutil`, `tarfile`.

Module declarations (expressions are shown without evaluating them):

```python
VERSION = re.compile('^(0|[1-9][0-9]*)\\.(0|[1-9][0-9]*)\\.(0|[1-9][0-9]*)$')
```

### `version_tuple`

```python
def version_tuple(value: str) -> tuple[int, int, int]
```

### `validate_manifest`

```python
def validate_manifest(raw: dict, product: str) -> dict
```

### `extract_release`

```python
def extract_release(archive: Path, destination: Path, max_bytes: int) -> None
```

Extract only regular files/directories within the release root.

### `release_executable`

```python
def release_executable(manifest: dict) -> str
```

### `release_identity`

```python
def release_identity(manifest: dict) -> tuple[str, str, str]
```

## `updater.py`

Source: [src/engine/updates/updater.py](../../../src/engine/updates/updater.py).

Download signed releases and activate them only while the platform is closed.

Imports (including optional/function-local imports; not a startup dependency list): `.config`, `.environment`, `.factory_defaults`, `.files`, `.migrations`, `.releases`, `contextlib`, `hashlib`, `json`, `os`, `pathlib`, `shutil`, `subprocess`, `tempfile`, `urllib.parse`, `urllib.request`, `uuid`.

### `_HttpsRedirect`

```python
class _HttpsRedirect(urllib.request.HTTPRedirectHandler):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def redirect_request(self, request, response, code, message, headers, new_url)
```

### `PlatformUpdater`

```python
class PlatformUpdater:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, config: UpdateConfig)
```

```python
def installed(self) -> dict | None
```

```python
def check(self) -> dict
```

```python
def stage_latest(self) -> dict
```

```python
def stage_local(self, archive: Path) -> dict
```

Bootstrap a trusted local release; remote releases always require signatures.

```python
def queue(self) -> None
```

```python
@contextmanager
def offline(self)
```

```python
def recover(self) -> None
```

Roll back an interrupted activation before opening the application.

```python
def apply_pending(self) -> bool
```

```python
def rollback(self) -> None
```

Explicitly restore previous software AND its pre-update data snapshot.
