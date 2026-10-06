# Module reference: `src/robot_systems/ROBOT_SYSTEM_BLUEPRINT/domain/users`

[Package guide](README.md) · [Complete source index](../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [user_schema.py](#user_schemapy)

## `__init__.py`

Source: [src/robot_systems/ROBOT_SYSTEM_BLUEPRINT/domain/users/__init__.py](../../../../../src/robot_systems/ROBOT_SYSTEM_BLUEPRINT/domain/users/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.robot_systems.ROBOT_SYSTEM_BLUEPRINT.domain.users.user_schema`.

Package-level import/export surface:

```python
from src.robot_systems.ROBOT_SYSTEM_BLUEPRINT.domain.users.user_schema import build_my_user_schema
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['build_my_user_schema']
```

## `user_schema.py`

Source: [src/robot_systems/ROBOT_SYSTEM_BLUEPRINT/domain/users/user_schema.py](../../../../../src/robot_systems/ROBOT_SYSTEM_BLUEPRINT/domain/users/user_schema.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.applications.user_management.domain.user_schema`.

### `build_my_user_schema`

```python
def build_my_user_schema(role_values: list[str]) -> UserSchema
```

Build the user-management schema from the robot-system role policy.
