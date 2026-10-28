from abc import ABC, abstractmethod

from src.shared_contracts.accounts.commands import (
    ChangePassword, ChangeRole, CreateAccount, DeleteAccount, EditProfile,
    RevealPassword, RevealedPassword,
)
from src.shared_contracts.accounts.records import AccountChange, AccountSummary
from src.shared_contracts.authorization.results import Result


class IAccountService(ABC):
    """Session-authorized account operations; storage and crypto may block.

    Expected denials/input/conflict errors return Failure. Infrastructure errors
    raise ServiceException subclasses. Every effective mutation commits its audit
    history atomically; no-op saves do not update metadata. Commands use stable
    account UUIDs, not reusable login IDs. Returned summaries never contain secrets.
    """

    @abstractmethod
    def list_users(self) -> Result[tuple[AccountSummary, ...]]: ...

    @abstractmethod
    def create_user(self, command: CreateAccount) -> Result[AccountSummary]: ...

    @abstractmethod
    def edit_profile(self, command: EditProfile) -> Result[AccountChange]: ...

    @abstractmethod
    def change_password(self, command: ChangePassword) -> Result[AccountSummary]: ...

    @abstractmethod
    def change_role(self, command: ChangeRole) -> Result[AccountChange]: ...

    @abstractmethod
    def delete_user(self, command: DeleteAccount) -> Result[None]: ...

    @abstractmethod
    def reveal_operator_password(self, command: RevealPassword) -> Result[RevealedPassword]: ...
