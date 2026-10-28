from abc import ABC, abstractmethod

from src.shared_contracts.authorization.access import (
    AccessContext, AccessDecision, AccessRequest,
)


class IAccessPolicy(ABC):
    """Pure policy boundary; replacement must preserve deny-by-default semantics."""

    @property
    @abstractmethod
    def revision(self) -> int:
        """Revision of this immutable policy snapshot."""

    @abstractmethod
    def decide(self, request: AccessRequest, context: AccessContext) -> AccessDecision:
        """Evaluate trusted facts without performing I/O."""
