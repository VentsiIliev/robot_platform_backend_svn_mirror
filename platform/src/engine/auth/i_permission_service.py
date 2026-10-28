from abc import ABC, abstractmethod

from src.shared_contracts.authorization.permissions import PermissionSnapshot, UpdateAppPermissions
from src.shared_contracts.authorization.results import Result


class IPermissionService(ABC):
    """Session-authorized permission administration; may block for durable storage.

    Both reads and writes require permissions.manage. Business failures return
    Failure; infrastructure errors use the shared ServiceException hierarchy.
    Updates are revision-checked and commit with redacted grant-change history.
    """
    @abstractmethod
    def read_permissions(self) -> Result[PermissionSnapshot]: ...

    @abstractmethod
    def update_permissions(self, command: UpdateAppPermissions) -> Result[PermissionSnapshot]: ...
