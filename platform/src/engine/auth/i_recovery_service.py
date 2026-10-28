from abc import ABC, abstractmethod

from src.shared_contracts.accounts.recovery import GenerateRecoveryCodes, RecoverAdminAccount, RecoveryCodes
from src.shared_contracts.authorization.results import Result


class IRecoveryService(ABC):
    @abstractmethod
    def generate_codes(self, command: GenerateRecoveryCodes) -> Result[RecoveryCodes]:
        """Reauthenticate current Admin, revoke old codes, and return a new set once.

        Only the authenticated Admin's own account is eligible. This may block.
        Failure uses typed codes; infrastructure errors use ServiceException.
        """

    @abstractmethod
    def recover_admin(self, command: RecoverAdminAccount) -> Result[RecoveryCodes]:
        """Verify a saved code, reset only its Admin account, and replace all codes.

        Does not log the user in. Password/version, code consumption/replacement,
        and audit commit together. Invalid proofs are generic; throttling persists
        across restart. Returned codes are secret and must be shown once, not logged.
        """
