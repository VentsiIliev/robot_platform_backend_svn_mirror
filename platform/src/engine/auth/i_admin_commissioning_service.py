from abc import ABC, abstractmethod

from src.shared_contracts.accounts.commissioning import AdminSetupStatus, CreateFirstAdmin
from src.shared_contracts.accounts.records import AccountSummary
from src.shared_contracts.authorization.results import Result


class IAdminCommissioningService(ABC):
    """Initial customer setup only, backed by trusted initialized installation state.

    No session is required for genuine initial setup. A missing/corrupt established
    store is an infrastructure failure, never permission to create another Admin.
    """
    @abstractmethod
    def status(self) -> AdminSetupStatus: ...

    @abstractmethod
    def create_first_admin(self, command: CreateFirstAdmin) -> Result[AccountSummary]: ...
