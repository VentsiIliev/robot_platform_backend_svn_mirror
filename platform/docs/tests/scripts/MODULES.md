# Module reference: `tests/scripts`

[Package guide](README.md) · [Complete source index](../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [test_migrate_global_calibration_to_work_area.py](#test_migrate_global_calibration_to_work_areapy)

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
