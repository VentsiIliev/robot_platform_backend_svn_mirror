from abc import ABC, abstractmethod
from src.shared_contracts.accounts.sessions import AccountSessionStatus
from src.shared_contracts.authorization.results import Result


class IAccountSessionService(ABC):
    @abstractmethod
    def status(self) -> Result[AccountSessionStatus]:
        """Revalidate stored account/version claims without an audited user action.

        May block for storage. A racing session returns CONFLICT; infrastructure
        failures use shared exceptions. Never authenticates or creates a session.
        """
