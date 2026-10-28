"""Protected local key storage, explicit provisioning, and no implicit key repair."""
import base64
import binascii
import errno
import os
from pathlib import Path
import secrets
import stat
import tempfile
from uuid import uuid4

from src.engine.auth.i_encryption_key_provider import (
    EncryptionKey, IEncryptionKeyProvider, IEncryptionKeyProvisioner, KeyDescriptor,
)
from src.engine.core.durable_files import store_lock, sync_directory
from src.shared_contracts.authorization.errors import (
    ErrorCode, KeyIntegrityError, KeyUnavailableError, ServiceError, UnsafeKeyStorageError,
)
from src.shared_contracts.authorization.results import Failure, Success


class ProtectedFileKeyProvider(IEncryptionKeyProvider, IEncryptionKeyProvisioner):
    """Key file 0600/0400, private parent directory, no final-component symlinks.

    File ownership is the platform OS account (or accessible to root maintenance).
    These are OS permissions, not isolation from arbitrary code running as that
    same account. Keep the key outside software, source control, and the database.
    """

    def __init__(self, path: str | Path) -> None:
        self._path = Path(path).absolute()

    def load_key(self) -> EncryptionKey:
        directory = self._open_directory()
        try:
            with store_lock(self._path):
                try:
                    descriptor = os.open(self._path.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK,
                                         dir_fd=directory)
                    with os.fdopen(descriptor, "rb") as stream:
                        info = os.fstat(stream.fileno())
                        self._check_private(info, directory=False)
                        raw = stream.read(129)
                except OSError as exc:
                    self._raise_io(exc)
                return self._validate(raw)
        except OSError as exc:
            self._raise_io(exc)
        finally:
            os.close(directory)

    def provision_new(self):
        try:
            self._path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        except OSError as exc:
            self._raise_io(exc)
        directory = self._open_directory()
        temporary = None
        try:
            with store_lock(self._path):
                try:
                    os.stat(self._path.name, dir_fd=directory, follow_symlinks=False)
                except FileNotFoundError:
                    pass
                else:
                    return Failure(ServiceError(ErrorCode.ALREADY_EXISTS, "credential.key_already_exists", uuid4().hex))
                key = EncryptionKey(base64.urlsafe_b64encode(secrets.token_bytes(32)))
                descriptor, temporary = tempfile.mkstemp(prefix=".operator-key-", dir=self._path.parent)
                with os.fdopen(descriptor, "wb") as stream:
                    os.fchmod(stream.fileno(), 0o600)
                    stream.write(key.encoded + b"\n")
                    stream.flush()
                    os.fsync(stream.fileno())
                # Link publishes a complete file atomically and refuses overwrite,
                # including a key created concurrently by a noncooperating caller.
                try:
                    os.link(temporary, self._path.name, dst_dir_fd=directory, follow_symlinks=False)
                except FileExistsError:
                    return Failure(ServiceError(ErrorCode.ALREADY_EXISTS, "credential.key_already_exists", uuid4().hex))
                os.unlink(temporary)
                temporary = None
                sync_directory(self._path.parent)
                return Success(KeyDescriptor(key.fingerprint))
        except OSError as exc:
            self._raise_io(exc)
        finally:
            if temporary is not None:
                Path(temporary).unlink(missing_ok=True)
            os.close(directory)

    def _open_directory(self):
        try:
            descriptor = os.open(self._path.parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
            try:
                self._check_private(os.fstat(descriptor), directory=True)
            except BaseException:
                os.close(descriptor)
                raise
            return descriptor
        except OSError as exc:
            self._raise_io(exc)

    @staticmethod
    def _check_private(info, *, directory):
        correct_type = stat.S_ISDIR(info.st_mode) if directory else stat.S_ISREG(info.st_mode)
        mode = stat.S_IMODE(info.st_mode)
        valid_mode = mode == 0o700 if directory else mode in (0o400, 0o600)
        if (not correct_type or not valid_mode
                or os.geteuid() != 0 and info.st_uid != os.geteuid()):
            raise UnsafeKeyStorageError()

    @staticmethod
    def _validate(raw):
        try:
            encoded = raw.strip()
            if len(raw) > 128 or len(encoded) != 44 or len(base64.b64decode(encoded, altchars=b"-_", validate=True)) != 32:
                raise ValueError("Invalid encryption key format")
            return EncryptionKey(encoded)
        except (ValueError, binascii.Error) as exc:
            raise KeyIntegrityError() from exc

    @staticmethod
    def _raise_io(exc):
        if exc.errno in (errno.ELOOP, errno.ENOTDIR):
            raise UnsafeKeyStorageError() from exc
        raise KeyUnavailableError() from exc
