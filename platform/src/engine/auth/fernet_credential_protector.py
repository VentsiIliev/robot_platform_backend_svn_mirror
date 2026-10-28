"""Password verification and authenticated Operator-secret encryption are separate."""
import hmac

from cryptography.fernet import Fernet, InvalidToken

from src.engine.auth.i_credential_protector import ICredentialProtector
from src.engine.auth.i_encryption_key_provider import IEncryptionKeyProvider
from src.engine.auth.i_password_hasher import IPasswordHasher
from src.engine.auth.password_hasher import ScryptPasswordHasher
from src.shared_contracts.authorization.errors import (
    CredentialIntegrityError, KeyIntegrityError, KeyMismatchError, KeyUnavailableError,
)


class FernetCredentialProtector(ICredentialProtector):
    _PREFIX = b"fernet-v1:"

    def __init__(self, key_provider: IEncryptionKeyProvider, *, key_fingerprint: str | None,
                 passwords: IPasswordHasher | None = None) -> None:
        self._keys = key_provider
        self._fingerprint = key_fingerprint
        self._passwords = passwords or ScryptPasswordHasher()

    def hash_password(self, password):
        return self._passwords.hash_password(password)

    def verify_password(self, password, encoded_hash):
        return self._passwords.verify_password(password, encoded_hash)

    def encrypt_operator_password(self, password):
        return self._PREFIX + self._fernet().encrypt(password.encode("utf-8"))

    def decrypt_operator_password(self, ciphertext):
        if not isinstance(ciphertext, bytes) or not ciphertext.startswith(self._PREFIX):
            raise CredentialIntegrityError()
        try:
            return self._fernet().decrypt(ciphertext[len(self._PREFIX):]).decode("utf-8")
        except (InvalidToken, UnicodeError, TypeError) as exc:
            raise CredentialIntegrityError() from exc

    def _fernet(self):
        # Do not cache a key: loss/replacement must be detected on the next secret
        # operation. Admin/Manufacturer hashing never calls this method.
        if not self._fingerprint:
            raise KeyUnavailableError()
        key = self._keys.load_key()
        if not hmac.compare_digest(key.fingerprint, self._fingerprint):
            raise KeyMismatchError()
        try:
            return Fernet(key.encoded)
        except (ValueError, TypeError) as exc:
            raise KeyIntegrityError() from exc
