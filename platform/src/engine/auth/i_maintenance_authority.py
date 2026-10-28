from abc import ABC, abstractmethod

from src.shared_contracts.accounts.maintenance import OperatingSystemActor
from src.shared_contracts.authorization.results import Result


class IMaintenanceAuthority(ABC):
    @abstractmethod
    def current_actor(self) -> Result[OperatingSystemActor]:
        """Verify host-level maintenance authority; never accept platform roles.

        ACCESS_DENIED means no OS authority. Unexpected infrastructure failures
        use the shared ServiceException hierarchy. Request DTOs cannot supply
        or override the returned actor.
        """
