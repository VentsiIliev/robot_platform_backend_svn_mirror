"""Salted scrypt password hashing, using the Python/OpenSSL implementation."""
import base64
import binascii
import hashlib
import hmac
import secrets

from src.engine.auth.i_password_hasher import IPasswordHasher
from src.shared_contracts.authorization.errors import ServiceUnavailableError, StorageIntegrityError


class ScryptPasswordHasher(IPasswordHasher):
    _N = 2 ** 17
    _R = 8
    _P = 1

    def hash_password(self, password: str) -> str:
        salt = secrets.token_bytes(16)
        digest = self._derive(password, salt)
        return "scrypt-v1$" + base64.urlsafe_b64encode(salt).decode() + "$" + base64.urlsafe_b64encode(digest).decode()

    def verify_password(self, password: str, encoded_hash: str) -> bool:
        try:
            version, salt, expected = encoded_hash.split("$")
            if version != "scrypt-v1":
                raise ValueError("Unsupported password hash")
            salt_bytes = base64.b64decode(salt, altchars=b"-_", validate=True)
            expected_bytes = base64.b64decode(expected, altchars=b"-_", validate=True)
            if len(salt_bytes) != 16 or len(expected_bytes) != 32:
                raise ValueError("Invalid password hash structure")
        except (ValueError, TypeError, binascii.Error) as exc:
            raise StorageIntegrityError() from exc
        return hmac.compare_digest(self._derive(password, salt_bytes), expected_bytes)

    def _derive(self, password: str, salt: bytes) -> bytes:
        try:
            return hashlib.scrypt(password.encode("utf-8"), salt=salt, n=self._N,
                                  r=self._R, p=self._P, dklen=32, maxmem=256 * 1024 * 1024)
        except (ValueError, OSError) as exc:
            raise ServiceUnavailableError() from exc
