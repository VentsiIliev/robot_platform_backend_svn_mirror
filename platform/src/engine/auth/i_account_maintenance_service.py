from abc import ABC, abstractmethod

from src.shared_contracts.accounts.maintenance import CreateManufacturer, ResetManufacturerPassword
from src.shared_contracts.accounts.records import AccountSummary
from src.shared_contracts.authorization.results import Result


class IAccountMaintenanceService(ABC):
    """Host-authorized service, never injected into normal application screens.

    Each method checks OS authority independently. No platform session or role
    grants it. Mutations are atomic with audit and return typed failures; storage
    and cryptography failures use shared infrastructure exceptions. May block.
    """
    @abstractmethod
    def inspect_manufacturer(self, login_id: str) -> Result[AccountSummary]: ...

    @abstractmethod
    def create_manufacturer(self, command: CreateManufacturer) -> Result[AccountSummary]: ...

    @abstractmethod
    def reset_manufacturer_password(self, command: ResetManufacturerPassword) -> Result[AccountSummary]: ...
