"""Application-owned account contracts. No engine, storage, or Qt dependencies."""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Generic, TypeAlias, TypeVar

T = TypeVar("T")


class UserErrorCode(str, Enum):
    ACCESS_DENIED = "access_denied"
    AUTHENTICATION_REQUIRED = "authentication_required"
    INVALID_INPUT = "invalid_input"
    INVALID_PROOF = "invalid_proof"
    ALREADY_EXISTS = "already_exists"
    NOT_FOUND = "not_found"
    CONFLICT = "conflict"
    RATE_LIMITED = "rate_limited"
    BUSY = "busy"
    POLICY_VIOLATION = "policy_violation"
    CREDENTIAL_STORAGE = "credential_storage"
    INTEGRITY = "integrity"
    UNAVAILABLE = "unavailable"


@dataclass(frozen=True)
class UserError:
    code: UserErrorCode
    reference: str = ""

    def __post_init__(self):
        object.__setattr__(self, "code", UserErrorCode(self.code))


@dataclass(frozen=True)
class UserSuccess(Generic[T]):
    value: T


@dataclass(frozen=True)
class UserFailure:
    error: UserError


UserResult: TypeAlias = UserSuccess[T] | UserFailure


@dataclass(frozen=True)
class UserEntry:
    account_id: str
    login_id: str
    first_name: str
    last_name: str
    role: str
    email: str
    enabled: bool
    revision: int
    created_at: str | None
    created_by: str | None
    updated_at: str | None
    updated_by: str | None
    created_by_label: str = "—"
    updated_by_label: str = "—"

    def get(self, key, default=""):
        name = {"id": "login_id", "firstName": "first_name", "lastName": "last_name"}.get(key, key)
        value = getattr(self, name, default)
        return default if value is None else value

    def get_id(self, key="id"):
        return self.get(key)


@dataclass(frozen=True)
class UserPage:
    users: tuple[UserEntry, ...]
    actor_id: str
    actor_role: str
    session_revision: int


@dataclass(frozen=True)
class ControlAccess:
    key: str
    visible: bool
    role_eligible: bool
    allowed: bool


@dataclass(frozen=True)
class ScreenAccess:
    session_revision: int
    policy_revision: int
    controls: tuple[ControlAccess, ...]
    create_roles: tuple[str, ...]


@dataclass(frozen=True)
class NewUser:
    login_id: str
    first_name: str
    last_name: str
    role: str
    password: str = field(repr=False)
    email: str = ""


@dataclass(frozen=True)
class EditUser:
    account_id: str
    revision: int
    first_name: str
    last_name: str
    email: str


@dataclass(frozen=True)
class PasswordChange:
    account_id: str
    revision: int
    new_password: str = field(repr=False)
    current_password: str = field(default="", repr=False)


@dataclass(frozen=True)
class RoleChange:
    account_id: str
    revision: int
    role: str
    new_password: str | None = field(default=None, repr=False)


@dataclass(frozen=True)
class SecretDisplay:
    text: str = field(repr=False)


@dataclass(frozen=True)
class QrDisplay:
    png: bytes = field(repr=False)


@dataclass(frozen=True)
class HistoryChange:
    field: str
    before: str | None
    after: str | None


@dataclass(frozen=True)
class HistoryEntry:
    occurred_at: str
    actor: str
    action: str
    outcome: str
    changes: tuple[HistoryChange, ...] = ()
    password_changed: bool = False


@dataclass(frozen=True)
class PermissionsPage:
    revision: int
    roles: tuple[str, ...]
    grants: tuple[tuple[str, tuple[str, ...]], ...]
    locked: tuple[tuple[str, str], ...]


class IUserManagementService(ABC):
    @abstractmethod
    def session_revision(self) -> int:
        """Cheap atomic session version; no I/O. Reject late worker responses."""

    @abstractmethod
    def load_users(self) -> UserResult[UserPage]: ...

    @abstractmethod
    def access(self, target_id: str | None) -> UserResult[ScreenAccess]: ...

    @abstractmethod
    def create(self, command: NewUser) -> UserResult[UserEntry]: ...

    @abstractmethod
    def edit(self, command: EditUser) -> UserResult[UserEntry]: ...

    @abstractmethod
    def change_password(self, command: PasswordChange) -> UserResult[UserEntry]: ...

    @abstractmethod
    def change_role(self, command: RoleChange) -> UserResult[UserEntry]: ...

    @abstractmethod
    def delete(self, account_id: str, revision: int) -> UserResult[None]: ...

    @abstractmethod
    def reveal(self, account_id: str) -> UserResult[SecretDisplay]: ...

    @abstractmethod
    def issue_qr(self, account_id: str, revision: int) -> UserResult[QrDisplay]: ...

    @abstractmethod
    def generate_recovery_codes(self, current_password: str) -> UserResult[SecretDisplay]: ...

    @abstractmethod
    def history(self, account_id: str) -> UserResult[tuple[HistoryEntry, ...]]: ...

    @abstractmethod
    def permissions(self) -> UserResult[PermissionsPage]: ...

    @abstractmethod
    def set_permission(self, app_id: str, roles: tuple[str, ...], revision: int) -> UserResult[PermissionsPage]: ...
