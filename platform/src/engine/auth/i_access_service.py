"""Replaceable read-only access boundary. No Qt or application dependencies."""
from abc import ABC, abstractmethod

from src.shared_contracts.authorization.access import AccessRequest, AccessSnapshot
from src.shared_contracts.authorization.results import Result


class IAccessService(ABC):
    @abstractmethod
    def evaluate(self, requests: tuple[AccessRequest, ...]) -> Result[AccessSnapshot]:
        """Evaluate against one session revision; denial is a normal decision.

        Invalid requests return INVALID_INPUT; a changed session returns CONFLICT.
        Infrastructure failures raise contract-defined ServiceException subclasses.
        This may perform storage reads; UI callers must respect blocking adapters.
        No mutation, audit-write, or implicit permission grant occurs here.
        """
