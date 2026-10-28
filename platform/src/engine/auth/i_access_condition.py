"""Extension seam for domain-owned target authorization without Qt or I/O."""
from abc import ABC, abstractmethod

from src.shared_contracts.authorization.access import Actor, ResourceFacts


class IAccessCondition(ABC):
    @abstractmethod
    def matches(self, actor: Actor, target: ResourceFacts | None) -> bool:
        """Restrict an existing grant using trusted, possibly domain-specific facts.

        Cannot grant a role access on its own. Operational/safety constraints
        belong in the operation service, since Manufacturer bypasses this
        authorization condition along with other role-specific restrictions.
        """
