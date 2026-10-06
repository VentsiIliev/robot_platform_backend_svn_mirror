# Module reference: `src/robot_systems/welding/domain/users`

[Package guide](README.md) · [Complete source index](../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [welding_user_schema.py](#welding_user_schemapy)

## `__init__.py`

Source: [src/robot_systems/welding/domain/users/__init__.py](../../../../../src/robot_systems/welding/domain/users/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `.welding_user_schema`.

Package-level import/export surface:

```python
from .welding_user_schema import build_welding_user_schema
```

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `welding_user_schema.py`

Source: [src/robot_systems/welding/domain/users/welding_user_schema.py](../../../../../src/robot_systems/welding/domain/users/welding_user_schema.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.user_management.domain.user_schema`.

### `build_welding_user_schema`

```python
def build_welding_user_schema(role_values: list[str]) -> UserSchema
```
