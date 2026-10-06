# Module reference: `tests/scripts`

[Package guide](README.md) · [Complete source index](../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [test_migrate_global_calibration_to_work_area.py](#test_migrate_global_calibration_to_work_areapy)
- [test_publish_changes.py](#test_publish_changespy)

## `__init__.py`

Source: [tests/scripts/__init__.py](../../../tests/scripts/__init__.py).

Tests for independently runnable repository scripts.

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `test_migrate_global_calibration_to_work_area.py`

Source: [tests/scripts/test_migrate_global_calibration_to_work_area.py](../../../tests/scripts/test_migrate_global_calibration_to_work_area.py).

Imports (including optional/function-local imports; not a startup dependency list): `argparse`, `importlib.util`, `json`, `pathlib`, `tempfile`, `unittest`.

Module declarations (expressions are shown without evaluating them):

```python
migrate = _MODULE.migrate
```

### `TestMigrateGlobalCalibrationToWorkArea`

```python
class TestMigrateGlobalCalibrationToWorkArea(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_migrates_without_enabling_per_area_mode(self)
```

```python
def test_existing_profile_requires_explicit_overwrite(self)
```

## `test_publish_changes.py`

Source: [tests/scripts/test_publish_changes.py](../../../tests/scripts/test_publish_changes.py).

Exercise publication against disposable Git repos; SVN and push are simulated.

Imports (including optional/function-local imports; not a startup dependency list): `contextlib`, `io`, `pathlib`, `scripts.publish_changes`, `subprocess`, `tempfile`, `unittest`.

### `SimulatedPublicationGit`

```python
class SimulatedPublicationGit(Git):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, root)
```

```python
def read(self, *args, **kwargs)
```

```python
def run(self, *args)
```

```python
def local(self, *args)
```

### `PublishChangesTests`

```python
class PublishChangesTests(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def setUp(self)
```

```python
def execute(self, argv, paths=None)
```

```python
def test_all_commits_then_svn_then_pushes_rewritten_head(self)
```

```python
def test_dry_run_does_not_change_index_head_or_files(self)
```

```python
def test_svn_failure_never_pushes_and_keeps_local_commit(self)
```

```python
def test_push_failure_can_resume_without_duplicate_commit(self)
```

```python
def test_unsynced_head_is_not_pushed_even_if_svn_returns_success(self)
```

```python
def test_staged_only_rejects_unrelated_untracked_files_before_commit(self)
```

```python
def test_partial_paths_reject_leftovers_before_commit(self)
```

```python
def test_protected_branch_is_rejected_before_mutation(self)
```

```python
def test_empty_staging_does_not_create_commit(self)
```

```python
def test_whitespace_error_prevents_commit_and_publication(self)
```
