"""Internal account persistence contract; services never depend on SQLite types."""
from abc import ABC, abstractmethod
from contextlib import AbstractContextManager
from dataclasses import dataclass, field

from src.shared_contracts.accounts.events import AuditEvent, HistoryQuery
from src.shared_contracts.accounts.records import AccountSummary


@dataclass(frozen=True)
class StoredAccount:
    summary: AccountSummary
    credential_version: int
    password_hash: str = field(repr=False)
    operator_ciphertext: bytes | None = field(default=None, repr=False)


@dataclass(frozen=True)
class RecoveryVerifier:
    credential_version: int
    digest: str = field(repr=False)


@dataclass(frozen=True)
class RecoveryAttempts:
    failures: int
    window_started: float


class IAccountTransaction(ABC):
    @abstractmethod
    def get(self, account_id: str) -> StoredAccount | None: ...

    @abstractmethod
    def get_by_login(self, login_id: str) -> StoredAccount | None: ...

    @abstractmethod
    def list_accounts(self) -> tuple[StoredAccount, ...]: ...

    @abstractmethod
    def insert(self, account: StoredAccount) -> None: ...

    @abstractmethod
    def replace(self, account: StoredAccount) -> None: ...

    @abstractmethod
    def delete(self, account_id: str) -> None: ...

    @abstractmethod
    def append_event(self, event: AuditEvent) -> None: ...

    @abstractmethod
    def history(self, query: HistoryQuery) -> tuple[AuditEvent, ...]: ...

    @abstractmethod
    def metadata(self, key: str) -> str | None: ...

    @abstractmethod
    def set_metadata(self, key: str, value: str) -> None: ...

    @abstractmethod
    def read_permissions(self) -> dict[str, tuple[str, ...]]: ...

    @abstractmethod
    def write_permissions(self, app_id: str, roles: tuple[str, ...]) -> None: ...

    @abstractmethod
    def recovery_verifiers(self, account_id: str) -> tuple[RecoveryVerifier, ...]: ...

    @abstractmethod
    def replace_recovery_verifiers(self, account_id: str, verifiers: tuple[RecoveryVerifier, ...]) -> None: ...

    @abstractmethod
    def recovery_attempts(self, key: str) -> RecoveryAttempts | None: ...

    @abstractmethod
    def set_recovery_attempts(self, key: str, state: RecoveryAttempts) -> None: ...

    @abstractmethod
    def prune_recovery_attempts(self, older_than: float) -> None: ...

    @abstractmethod
    def replace_login_token(self, account_id: str, digest: str, credential_version: int) -> None: ...

    @abstractmethod
    def account_for_login_token(self, digest: str) -> StoredAccount | None: ...

    @abstractmethod
    def authentication_attempts(self, key: str) -> RecoveryAttempts | None: ...

    @abstractmethod
    def set_authentication_attempts(self, key: str, state: RecoveryAttempts) -> None: ...

    @abstractmethod
    def prune_authentication_attempts(self, older_than: float) -> None: ...


class IAccountStore(ABC):
    @abstractmethod
    def transaction(self) -> AbstractContextManager[IAccountTransaction]:
        """Serialize mutations; rollback all changes if the body or commit fails.

        A transaction owns its connection and can be used from a worker thread.
        Ordinary opening must never initialize missing/corrupt account storage.
        """
