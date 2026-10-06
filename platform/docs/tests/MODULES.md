# Module reference: `tests`

[Package guide](README.md) · [Complete source index](../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [run_tests.py](#run_testspy)

## `__init__.py`

Source: [tests/__init__.py](../../tests/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `run_tests.py`

Source: [tests/run_tests.py](../../tests/run_tests.py).

Imports (including optional/function-local imports; not a startup dependency list): `coverage`, `io`, `logging`, `os`, `pathlib`, `shutil`, `sys`, `unittest`.

Module declarations (expressions are shown without evaluating them):

```python
ROOT = Path(__file__).resolve().parent.parent
TESTS_DIR = Path(__file__).resolve().parent
ARTIFACT_DIRS = [TESTS_DIR / 'MagicMock']
```

### `_clean_test_artifacts`

```python
def _clean_test_artifacts() -> None
```

### `run`

```python
def run() -> None
```
