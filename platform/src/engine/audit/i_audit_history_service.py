from abc import ABC, abstractmethod

from src.shared_contracts.accounts.events import AuditEvent, HistoryQuery
from src.shared_contracts.authorization.results import Result


class IAuditHistoryService(ABC):
    @abstractmethod
    def list_events(self, query: HistoryQuery) -> Result[tuple[AuditEvent, ...]]:
        """Read redacted history, newest first, including deleted account IDs.

        Requires target-scoped audit.view: Admin can read self/current Operators;
        Manufacturer can also read other privileged and deleted identities.
        Invalid paging and denied access return Failure;
        storage errors raise shared ServiceException subclasses. No edit/delete
        methods are exposed, even for Manufacturer. Storage reads may block.
        """
