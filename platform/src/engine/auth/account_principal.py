"""Authenticated account claims contain identity/version, never credential material."""
from abc import abstractmethod

from src.engine.auth.auth_user_record import AuthUserRecord
from src.engine.auth.i_authenticated_user import IAuthenticatedUser
from src.shared_contracts.accounts.records import AccountSummary, UserRole


class IAccountPrincipal(IAuthenticatedUser):
    @property
    @abstractmethod
    def account_id(self) -> str: ...

    @property
    @abstractmethod
    def credential_version(self) -> int: ...


class AccountPrincipal(IAccountPrincipal):
    def __init__(self, account: AccountSummary, credential_version: int) -> None:
        self._account = account
        self._version = credential_version

    @property
    def account_id(self):
        return self._account.account_id

    @property
    def credential_version(self):
        return self._version

    @property
    def user_id(self):
        return self._account.login_id

    @property
    def role(self):
        return UserRole(self._account.role)

    @property
    def record(self) -> AuthUserRecord:
        """Safe compatibility payload for the existing shell session drawer."""
        return AuthUserRecord(self.user_id, "", self.role, {
            "firstName": self._account.first_name,
            "lastName": self._account.last_name,
            "email": self._account.email,
        })
