from abc import ABC, abstractmethod

from src.shared_contracts.authorization.access import ResourceFacts, ResourceRef


class IAccessResourceResolver(ABC):
    @abstractmethod
    def resolve(self, reference: ResourceRef) -> ResourceFacts | None:
        """Read trusted domain facts, optionally a domain-specific facts subclass.

        Resolves resources only, never the acting user/session. Account targets
        remain owned by the account store. Storage failures use shared exceptions;
        no credentials or secret data may be included in returned facts.
        """
