from abc import ABC, abstractmethod

from src.shared_contracts.accounts.authentication import AccountIdentity
from src.shared_contracts.accounts.login_tokens import IssueLoginToken, IssuedLoginToken
from src.shared_contracts.authorization.results import Result


class ILoginTokenService(ABC):
    @abstractmethod
    def issue(self, command: IssueLoginToken) -> Result[IssuedLoginToken]:
        """Authorized replacement card, returned once; prior card is revoked."""

    @abstractmethod
    def authenticate(self, payload: str) -> Result[AccountIdentity]:
        """Authenticate an opaque versioned token. Password-based payloads fail.

        Authentication is throttled and audited; reset/role-change/deletion revokes
        cards through credential versions. Infrastructure errors use shared exceptions.
        """
