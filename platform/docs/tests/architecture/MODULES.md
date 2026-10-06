# Module reference: `tests/architecture`

[Package guide](README.md) · [Complete source index](../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [test_import_boundaries.py](#test_import_boundariespy)
- [test_paint_packaging_profile.py](#test_paint_packaging_profilepy)
- [test_shell_package.py](#test_shell_packagepy)

## `__init__.py`

Source: [tests/architecture/__init__.py](../../../tests/architecture/__init__.py).

Architecture-level regression tests.

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `test_import_boundaries.py`

Source: [tests/architecture/test_import_boundaries.py](../../../tests/architecture/test_import_boundaries.py).

Imports (including optional/function-local imports; not a startup dependency list): `ast`, `dataclasses`, `pathlib`, `unittest`.

Module declarations (expressions are shown without evaluating them):

```python
ROOT = Path(__file__).resolve().parents[2]
```

### `ImportViolation`

```python
@dataclass(frozen=True, order=True)
class ImportViolation:
```

Declared fields/defaults:

```python
source: str
imported_module: str
```

### `TestImportBoundaries`

```python
class TestImportBoundaries(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_cross_layer_and_cross_system_imports_match_known_debt(self)
```

### `_find_imports`

```python
def _find_imports(relative_root: str, forbidden_prefixes: tuple[str, ...]) -> set[ImportViolation]
```

### `_imported_modules`

```python
def _imported_modules(tree: ast.AST) -> tuple[str, ...]
```

### `_format_failure`

```python
def _format_failure(*, unexpected: list[ImportViolation], resolved: list[ImportViolation]) -> str
```

## `test_paint_packaging_profile.py`

Source: [tests/architecture/test_paint_packaging_profile.py](../../../tests/architecture/test_paint_packaging_profile.py).

Imports (including optional/function-local imports; not a startup dependency list): `ast`, `json`, `pathlib`, `unittest`.

Module declarations (expressions are shown without evaluating them):

```python
ROOT = Path(__file__).resolve().parents[2]
PACKAGING_ROOT = ROOT / 'packaging'
```

### `TestPaintPackagingProfile`

```python
class TestPaintPackagingProfile(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_bundled_startup_config_selects_only_paint(self)
```

```python
def test_spec_excludes_other_robot_systems(self)
```

```python
def test_build_script_checks_collected_module_archive(self)
```

### `_literal_assignments`

```python
def _literal_assignments(path: Path) -> dict[str, object]
```

## `test_shell_package.py`

Source: [tests/architecture/test_shell_package.py](../../../tests/architecture/test_shell_package.py).

Verify that the shell can be distributed without the platform checkout.

Imports (including optional/function-local imports; not a startup dependency list): `ast`, `os`, `pathlib`, `shutil`, `subprocess`, `sys`, `tarfile`, `tempfile`, `tomllib`, `unittest`, `zipfile`.

Module declarations (expressions are shown without evaluating them):

```python
ROOT = Path(__file__).resolve().parents[2]
SHELL = ROOT / 'pl_gui'
```

### `TestShellBoundary`

```python
class TestShellBoundary(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_shell_has_no_platform_imports(self)
```

```python
def test_metadata_covers_existing_subpackages(self)
```

### `TestShellDistribution`

```python
class TestShellDistribution(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_standalone_sdist_wheel_and_installed_shell(self)
```
