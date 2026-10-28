from abc import ABC, abstractmethod
from contextlib import AbstractContextManager

from src.shared_contracts.authorization.access import ResourceRef
from src.shared_contracts.authorization.results import Result


class IAccessChangeLease(ABC):
    @abstractmethod
    def validate(self) -> Result[None]:
        """Recheck operational readiness immediately before account-store commit."""


class IAccessChangeGuard(ABC):
    @abstractmethod
    def hold(self, action: str, target: ResourceRef | None) -> AbstractContextManager[Result[IAccessChangeLease]]:
        """Reserve idle execution while a change affecting the active session commits.

        BUSY is an expected refusal. The lease outlives database commit/rollback.
        Implementations never stop a process or robot. Infrastructure errors use
        structured service exceptions. Queries must run outside the GUI thread.
        """
