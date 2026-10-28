"""Application-owned login contracts; implementations may use any identity backend."""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Generic, Protocol, TypeAlias, TypeVar


class LoginUser(Protocol):
    @property
    def user_id(self) -> str: ...

    @property
    def role(self) -> Enum: ...


class LoginErrorCode(str, Enum):
    INVALID_INPUT = "invalid_input"
    INVALID_PROOF = "invalid_proof"
    RATE_LIMITED = "rate_limited"
    BUSY = "busy"
    SETUP_CLOSED = "setup_closed"
    ALREADY_EXISTS = "already_exists"
    UNAVAILABLE = "unavailable"


@dataclass(frozen=True)
class LoginError:
    code: LoginErrorCode
    reference: str = ""


T = TypeVar("T")


@dataclass(frozen=True)
class LoginSuccess(Generic[T]):
    value: T


@dataclass(frozen=True)
class LoginFailure:
    error: LoginError


LoginResult: TypeAlias = LoginSuccess[T] | LoginFailure


@dataclass(frozen=True)
class AdminSetup:
    login_id: str
    first_name: str
    last_name: str
    password: str = field(repr=False)


@dataclass(frozen=True)
class AdminRecovery:
    login_id: str
    code: str = field(repr=False)
    new_password: str = field(repr=False)


@dataclass(frozen=True)
class RecoveryCodeDisplay:
    codes: tuple[str, ...] = field(repr=False)


class ILoginApplicationService(ABC):
    @abstractmethod
    def get_connection_information(self) -> dict:
        """Read-only connection identifiers; never requires account authentication."""

    @abstractmethod
    def authenticate(self, user_id: str, password: str) -> LoginResult[LoginUser]: ...

    @abstractmethod
    def authenticate_qr(self, payload: str) -> LoginResult[LoginUser]: ...

    @abstractmethod
    def scan_qr(self) -> LoginResult[str | None]:
        """Poll an optional scanner for an opaque card payload; never a password."""

    @abstractmethod
    def move_to_login_pos(self) -> None: ...

    @abstractmethod
    def is_first_run(self) -> LoginResult[bool]:
        """Whether first customer Admin setup is still open (not a user count)."""

    @abstractmethod
    def create_first_admin(self, command: AdminSetup) -> LoginResult[None]: ...

    @abstractmethod
    def recover_admin(self, command: AdminRecovery) -> LoginResult[RecoveryCodeDisplay]:
        """Consume saved proof and return replacement codes once; no automatic login."""
