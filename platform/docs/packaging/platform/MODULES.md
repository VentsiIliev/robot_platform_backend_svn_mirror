# Module reference: `packaging/platform`

[Package guide](README.md) · [Complete source index](../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [build.py](#buildpy)
- [build_and_release.py](#build_and_releasepy)
- [build_release.py](#build_releasepy)
- [gitea_release.py](#gitea_releasepy)
- [local_release.py](#local_releasepy)
- [manage.py](#managepy)
- [publish_platform.py](#publish_platformpy)
- [release_robot.py](#release_robotpy)
- [targets.py](#targetspy)

## `build.py`

Source: [packaging/platform/build.py](../../../packaging/platform/build.py).

Build one robot-system/profile bundle without bundling other systems.

Imports (including optional/function-local imports; not a startup dependency list): `argparse`, `ast`, `os`, `pathlib`, `subprocess`, `sys`, `targets`.

### `main`

```python
def main()
```

## `build_and_release.py`

Source: [packaging/platform/build_and_release.py](../../../packaging/platform/build_and_release.py).

Build, verify without hardware, and package an explicitly selected target.

Imports (including optional/function-local imports; not a startup dependency list): `build_release`, `os`, `pathlib`, `platform`, `src.engine.updates.releases`, `subprocess`, `sys`, `targets`.

### `main`

```python
def main(argv=None)
```

## `build_release.py`

Source: [packaging/platform/build_release.py](../../../packaging/platform/build_release.py).

Package an existing PyInstaller bundle into a platform-only release.

Imports (including optional/function-local imports; not a startup dependency list): `argparse`, `hashlib`, `json`, `pathlib`, `platform`, `src.engine.updates.factory_defaults`, `src.engine.updates.releases`, `subprocess`, `sys`, `tarfile`, `targets`, `tempfile`.

### `release_parser`

```python
def release_parser()
```

### `main`

```python
def main()
```

## `gitea_release.py`

Source: [packaging/shared/gitea_release.py](../../../packaging/shared/gitea_release.py).

Publish verified release artifacts through Gitea's release API.

Imports (including optional/function-local imports; not a startup dependency list): `hashlib`, `requests`, `urllib.parse`, `uuid`.

### `MultipartUpload`

```python
class MultipartUpload:
```

Stream a large archive with a known multipart content length.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, path)
```

### `GiteaPublisher`

```python
class GiteaPublisher:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, repository_url, token)
```

```python
def username(self)
```

```python
def request(self, method, path, **kwargs)
```

```python
def publish(self, directory, manifest, notes, digest)
```

```python
def publish_assets(self, tag, title, body, marker, files, digest)
```

Resume matching drafts; publish only after every attachment is verified.

## `local_release.py`

Source: [packaging/platform/local_release.py](../../../packaging/platform/local_release.py).

Install the latest local kit or run the selected installed robot platform.

Imports (including optional/function-local imports; not a startup dependency list): `argparse`, `json`, `pathlib`, `platform`, `re`, `src.engine.updates.config`, `src.engine.updates.releases`, `subprocess`, `sys`, `tarfile`, `targets`, `tempfile`.

### `latest_installer`

```python
def latest_installer(releases: Path, target: dict) -> Path
```

Select by semantic version, never by filename order or modification time.

### `install`

```python
def install(kit: Path, target: dict, config: Path | None, root: Path | None) -> int
```

### `run`

```python
def run(target: dict, config: Path | None, root: Path | None) -> int
```

### `main`

```python
def main() -> int
```

## `manage.py`

Source: [packaging/runtime/manage.py](../../../packaging/runtime/manage.py).

Independent installer/updater/launcher. Uses Ubuntu's system Python, not Qt.

Imports (including optional/function-local imports; not a startup dependency list): `argparse`, `json`, `os`, `pathlib`, `pwd`, `shutil`, `src.engine.updates.config`, `src.engine.updates.files`, `src.engine.updates.releases`, `src.engine.updates.updater`, `subprocess`, `sys`, `tarfile`, `uuid`.

Module declarations (expressions are shown without evaluating them):

```python
HERE = Path(__file__).resolve().parent
```

### `install_remote_support`

```python
def install_remote_support(root)
```

Provision system remote support, preserving the controller's ON/OFF state.

### `install`

```python
def install(args)
```

### `launch`

```python
def launch(updater, config_path)
```

### `main`

```python
def main()
```

## `publish_platform.py`

Source: [packaging/platform/publish_platform.py](../../../packaging/platform/publish_platform.py).

Run the existing platform build wrapper and publish its verified artifacts.

Imports (including optional/function-local imports; not a startup dependency list): `argparse`, `gitea_release`, `json`, `os`, `pathlib`, `release_common`, `src.engine.updates.releases`, `subprocess`, `sys`, `urllib.parse`.

Module declarations (expressions are shown without evaluating them):

```python
PLATFORM = Path(__file__).resolve().parents[2]
```

### `prepare_artifacts`

```python
def prepare_artifacts(output, target, version, identity)
```

### `publish`

```python
def publish(target, output, repository_url, token, notes='', signing_key=None)
```

### `main`

```python
def main()
```

## `release_robot.py`

Source: [packaging/robot/release_robot.py](../../../packaging/robot/release_robot.py).

Test, build and verify the configured combined robot release without hardware.

Imports (including optional/function-local imports; not a startup dependency list): `argparse`, `datetime`, `getpass`, `gitea_release`, `json`, `os`, `pathlib`, `release_common`, `subprocess`, `sys`, `tempfile`, `time`.

Module declarations (expressions are shown without evaluating them):

```python
PLATFORM = Path(__file__).resolve().parents[2]
DEPLOYMENT = PLATFORM / 'packaging/robot'
TESTS = ('tests.bootstrap.test_startup_config', 'tests.bootstrap.test_ros_backend_launcher', 'tests.robot_systems.paint.test_paint_system_overrides', 'tests.engine.updates.test_release_targets', 'tests.engine.updates.test_robot_release_workflow', 'tests.engine.updates.test_gitea_release')
```

### `Workflow`

```python
class Workflow:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, target, selected, report)
```

```python
def save(self)
```

```python
def run(self, label, command, cwd=PLATFORM, env=None)
```

```python
def tests(self)
```

```python
def build(self)
```

```python
def publish(self, remote, token, notes)
```

```python
def verify(self)
```

### `main`

```python
def main()
```

## `targets.py`

Source: [packaging/platform/targets.py](../../../packaging/platform/targets.py).

Declarative build identities; importing this module never constructs hardware.

Imports (including optional/function-local imports; not a startup dependency list): `json`, `pathlib`, `src.bootstrap.startup_config`, `sys`.

Module declarations (expressions are shown without evaluating them):

```python
ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / 'config/release_targets.json'
```

### `load_target`

```python
def load_target(name: str) -> dict
```

### `prepare_target`

```python
def prepare_target(name: str, destination: Path) -> dict
```
