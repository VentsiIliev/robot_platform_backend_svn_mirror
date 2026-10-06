from abc import ABC, abstractmethod


class IRemoteSupportService(ABC):
    @abstractmethod
    def get_remote_support_status(self) -> dict: ...

    @abstractmethod
    def set_remote_support_enabled(self, enabled: bool, duration_seconds: int = 900) -> None: ...

    @abstractmethod
    def get_password_status(self) -> dict: ...

    @abstractmethod
    def set_unattended_password(self, admin_id: str, admin_password: str, password: str) -> None: ...

    @abstractmethod
    def remove_unattended_password(self, admin_id: str, admin_password: str) -> None: ...
