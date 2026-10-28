from abc import abstractmethod

from src.engine.auth.i_password_hasher import IPasswordHasher


class ICredentialProtector(IPasswordHasher):
    """Credential cryptography seam. Implementations must not log their inputs."""

    @abstractmethod
    def encrypt_operator_password(self, password: str) -> bytes: ...

    @abstractmethod
    def decrypt_operator_password(self, ciphertext: bytes) -> str: ...
