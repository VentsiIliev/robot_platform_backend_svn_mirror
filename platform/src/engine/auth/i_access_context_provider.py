from abc import ABC, abstractmethod

from src.shared_contracts.authorization.access import AccessContext, ResourceRef


class IAccessContextProvider(ABC):
    """Trusted actor/target snapshots; implementations validate session freshness."""

    @abstractmethod
    def capture(self, target: ResourceRef | None = None) -> AccessContext:
        """Read current actor and target consistently; missing target stays None.

        Session revisions increase on login/logout/invalidation, including a
        relogin by the same account. Storage exceptions must be mapped to the
        shared structured infrastructure exceptions inside this adapter.
        """
