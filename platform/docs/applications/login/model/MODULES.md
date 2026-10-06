# Module reference: `src/applications/login/model`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [login_model.py](#login_modelpy)

## `__init__.py`

Source: [src/applications/login/model/__init__.py](../../../../src/applications/login/model/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `login_model.py`

Source: [src/applications/login/model/login_model.py](../../../../src/applications/login/model/login_model.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.login.i_login_application_service`, `src.engine.auth.i_authenticated_user`, `typing`.

### `LoginModel`

```python
class LoginModel:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, service: ILoginApplicationService) -> None
```

```python
def is_first_run(self) -> bool
```

```python
def authenticate(self, user_id: str, password: str) -> Optional[IAuthenticatedUser]
```

```python
def authenticate_qr(self, qr_payload: str) -> Optional[IAuthenticatedUser]
```

```python
def try_qr_login(self) -> Optional[Tuple[str, str]]
```

```python
def move_to_login_pos(self) -> None
```

```python
def create_first_admin(self, user_id: str, first_name: str, last_name: str, password: str) -> Tuple[bool, str]
```

```python
def validate_login_input(self, user_id: str, password: str) -> Optional[str]
```
