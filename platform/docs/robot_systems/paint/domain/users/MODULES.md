# Module reference: `src/robot_systems/paint/domain/users`

[Package guide](README.md) · [Complete source index](../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [paint_user_schema.py](#paint_user_schemapy)

## `__init__.py`

Source: [src/robot_systems/paint/domain/users/__init__.py](../../../../../src/robot_systems/paint/domain/users/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `.paint_user_schema`.

Package-level import/export surface:

```python
from .paint_user_schema import build_paint_user_schema
```

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `paint_user_schema.py`

Source: [src/robot_systems/paint/domain/users/paint_user_schema.py](../../../../../src/robot_systems/paint/domain/users/paint_user_schema.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.user_management.domain.user_schema`.

### `build_paint_user_schema`

```python
def build_paint_user_schema(role_values: list[str]) -> UserSchema
```
