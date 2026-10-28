from abc import ABC, abstractmethod

from src.shared_contracts.accounts.authentication import AccountIdentity, LoginCredentials
from src.shared_contracts.authorization.results import Result


class IAccountLoginService(ABC):
    @abstractmethod
    def login(self, credentials: LoginCredentials) -> Result[AccountIdentity]:
        """Verify stored credentials without creating a session or returning secrets.

        Unknown/disabled/retired-role accounts and incorrect passwords all return
        INVALID_PROOF with the same public message. Success/failure is audited
        without changing account edit metadata. Infrastructure failures raise
        shared structured exceptions. Password verification and storage may block.
        Persistent per-identifier/global limits return RATE_LIMITED until expiry;
        successful authentication does not clear the global failure budget.
        """
