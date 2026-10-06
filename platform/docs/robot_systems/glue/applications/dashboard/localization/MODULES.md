# Module reference: `src/robot_systems/glue/applications/dashboard/localization`

[Package guide](README.md) · [Complete source index](../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [compile.py](#compilepy)

## `__init__.py`

Source: [src/robot_systems/glue/applications/dashboard/localization/__init__.py](../../../../../../src/robot_systems/glue/applications/dashboard/localization/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `compile.py`

Source: [src/robot_systems/glue/applications/dashboard/localization/compile.py](../../../../../../src/robot_systems/glue/applications/dashboard/localization/compile.py).

Compile translation files for the glue dispensing dashboard. Expected layout: translations/ de/ glue_de.qts → glue_de.qm fr/ glue_fr.qts → glue_fr.qm ... Usage: python compile.y_pixels # compile all languages python compile.y_pixels de fr # compile specific languages only

Imports (including optional/function-local imports; not a startup dependency list): `pathlib`, `subprocess`, `sys`.

Module declarations (expressions are shown without evaluating them):

```python
TRANSLATIONS_DIR = Path(__file__).parent / 'translations'
```

### `find_lrelease`

```python
def find_lrelease() -> str | None
```

### `compile_language`

```python
def compile_language(lang_dir: Path, lrelease: str) -> bool
```

### `main`

```python
def main(langs: list[str] | None=None) -> bool
```
