# Module reference: `src/applications/user_management/domain`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [auth_user_repository_adapter.py](#auth_user_repository_adapterpy)
- [csv_user_repository.py](#csv_user_repositorypy)
- [default_schema.py](#default_schemapy)
- [i_user_repository.py](#i_user_repositorypy)
- [user.py](#userpy)
- [user_schema.py](#user_schemapy)

## `__init__.py`

Source: [src/applications/user_management/domain/__init__.py](../../../../src/applications/user_management/domain/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `auth_user_repository_adapter.py`

Source: [src/applications/user_management/domain/auth_user_repository_adapter.py](../../../../src/applications/user_management/domain/auth_user_repository_adapter.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.applications.user_management.domain.i_user_repository`, `src.engine.auth.auth_user_record`, `src.engine.auth.i_auth_user_repository`, `typing`.

### `AuthUserRepositoryAdapter`

```python
class AuthUserRepositoryAdapter(IAuthUserRepository):
```

Expose an application-level user repository through the auth contract.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, repository: IUserRepository) -> None
```

```python
def get_by_id(self, user_id: str) -> Optional[AuthUserRecord]
```

### `_RoleValue`

```python
class _RoleValue(str):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@property
def value(self) -> str
```

## `csv_user_repository.py`

Source: [src/applications/user_management/domain/csv_user_repository.py](../../../../src/applications/user_management/domain/csv_user_repository.py).

Imports (including optional/function-local imports; not a startup dependency list): `csv`, `logging`, `os`, `src.applications.user_management.domain.i_user_repository`, `src.applications.user_management.domain.user_schema`, `typing`.

### `CsvUserRepository`

```python
class CsvUserRepository(IUserRepository):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, file_path: str, schema: UserSchema)
```

```python
def get_schema(self) -> UserSchema
```

```python
def get_all(self) -> List[UserRecord]
```

```python
def get_by_id(self, user_id) -> Optional[UserRecord]
```

```python
def add(self, record: UserRecord) -> bool
```

```python
def update(self, record: UserRecord) -> bool
```

```python
def delete(self, user_id) -> bool
```

```python
def exists(self, user_id) -> bool
```

## `default_schema.py`

Source: [src/applications/user_management/domain/default_schema.py](../../../../src/applications/user_management/domain/default_schema.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.user_management.domain.user_schema`.

Module declarations (expressions are shown without evaluating them):

```python
DEFAULT_USER_SCHEMA = UserSchema(id_key='id', fields=[FieldDescriptor(key='id', label='ID', widget='int', required=True, read_only_on_edit=True), FieldDescriptor(key='firstName', label='First Name', widget='text', required=True), FieldDescriptor(key='lastName', label='Last Name', widget='text', required=True), FieldDescriptor(key='password', label='Password', widget='password', required=True, mask_in_table=True), FieldDescriptor(key='role', label='Role', widget='combo', required=True, options=['Admin', 'Operator', 'Viewer']), FieldDescriptor(key='email', label='Email', widget='email', required=False)])
```

## `i_user_repository.py`

Source: [src/applications/user_management/domain/i_user_repository.py](../../../../src/applications/user_management/domain/i_user_repository.py).

Imports (including optional/function-local imports; not a startup dependency list): `abc`, `src.applications.user_management.domain.user_schema`, `typing`.

### `IUserRepository`

```python
class IUserRepository(ABC):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def get_schema(self) -> UserSchema
```

```python
@abstractmethod
def get_all(self) -> List[UserRecord]
```

```python
@abstractmethod
def get_by_id(self, user_id) -> Optional[UserRecord]
```

```python
@abstractmethod
def add(self, record: UserRecord) -> bool
```

```python
@abstractmethod
def update(self, record: UserRecord) -> bool
```

```python
@abstractmethod
def delete(self, user_id) -> bool
```

```python
@abstractmethod
def exists(self, user_id) -> bool
```

## `user.py`

Source: [src/applications/user_management/domain/user.py](../../../../src/applications/user_management/domain/user.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`, `enum`, `typing`, `uuid`.

### `Role`

```python
class Role(Enum):
```

Declared fields/defaults:

```python
ADMIN = 'Admin'
OPERATOR = 'Operator'
VIEWER = 'Viewer'
DEVELOPER = 'Developer'
```

### `UserField`

```python
class UserField(Enum):
```

Declared fields/defaults:

```python
ID = 'id'
FIRST_NAME = 'firstName'
LAST_NAME = 'lastName'
PASSWORD = 'password'
ROLE = 'role'
EMAIL = 'email'
```

### `User`

```python
@dataclass
class User:
```

Declared fields/defaults:

```python
id: int
firstName: str
lastName: str
password: str
role: Role
email: Optional[str] = None
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def get_full_name(self) -> str
```

```python
def to_dict(self) -> dict
```

```python
@staticmethod
def from_dict(data: dict) -> User
```

## `user_schema.py`

Source: [src/applications/user_management/domain/user_schema.py](../../../../src/applications/user_management/domain/user_schema.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`, `typing`.

### `FieldDescriptor`

```python
@dataclass
class FieldDescriptor:
```

Declared fields/defaults:

```python
key: str
label: str
widget: str
required: bool = True
table_display: bool = True
read_only_on_edit: bool = False
options: Optional[List[str]] = None
mask_in_table: bool = False
```

### `UserSchema`

```python
@dataclass
class UserSchema:
```

Declared fields/defaults:

```python
fields: List[FieldDescriptor]
id_key: str = 'id'
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def get_table_fields(self) -> List[FieldDescriptor]
```

```python
def get_table_headers(self) -> List[str]
```

```python
def get_filterable_labels(self) -> List[str]
```

### `UserRecord`

```python
class UserRecord:
```

Generic user record backed by a plain dict — works with any schema.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, data: Dict[str, Any])
```

```python
def get(self, key: str, default: Any=None) -> Any
```

```python
def set(self, key: str, value: Any) -> None
```

```python
def get_id(self, id_key: str) -> Any
```

```python
def to_dict(self) -> Dict[str, Any]
```

```python
@staticmethod
def from_dict(data: Dict[str, Any]) -> UserRecord
```
