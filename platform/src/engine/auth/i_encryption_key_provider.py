"""Secret-key loading/provisioning seams; implementations may use files or hardware."""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import hashlib

from src.shared_contracts.authorization.results import Result


@dataclass(frozen=True)
class EncryptionKey:
    encoded: bytes = field(repr=False)

    @property
    def fingerprint(self) -> str:
        """Safe identifier for matching a key with its installation/database."""
        return hashlib.sha256(self.encoded).hexdigest()


@dataclass(frozen=True)
class KeyDescriptor:
    fingerprint: str


class IEncryptionKeyProvider(ABC):
    @abstractmethod
    def load_key(self) -> EncryptionKey:
        """Load a secret or raise a shared key exception; never create/fallback.

        May block. The returned material must never reach UI, logs, or exports.
        """


class IEncryptionKeyProvisioner(ABC):
    @abstractmethod
    def provision_new(self) -> Result[KeyDescriptor]:
        """Explicit trusted setup only; existing key returns ALREADY_EXISTS.

        Never overwrite a key, even when it is corrupt. Infrastructure failures
        use structured key exceptions; success returns an identifier, not a key.
        """
