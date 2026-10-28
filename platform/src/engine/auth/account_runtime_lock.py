"""Cooperative Linux exclusion between one account runtime and offline maintenance."""
import fcntl
import os
from pathlib import Path
import stat

from src.shared_contracts.authorization.errors import (
    AccountRuntimeInUseError, ServiceUnavailableError, StorageIntegrityError,
)


class AccountRuntimeLock:
    def __init__(self, descriptor: int) -> None:
        self._descriptor = descriptor

    @classmethod
    def acquire(cls, database: Path) -> "AccountRuntimeLock":
        descriptor = None
        try:
            database = Path(database).resolve(strict=True)
            owner = database.stat()
            path = database.with_name(database.name + ".runtime.lock")
            flags = os.O_RDWR | os.O_NOFOLLOW | os.O_CLOEXEC | os.O_NONBLOCK
            try:
                descriptor = os.open(path, flags | os.O_CREAT | os.O_EXCL, 0o600)
                if os.geteuid() == 0:
                    # Root maintenance must not prevent the platform OS account
                    # from acquiring its own lock after the tool exits.
                    os.fchown(descriptor, owner.st_uid, owner.st_gid)
            except FileExistsError:
                descriptor = os.open(path, flags)
            if not stat.S_ISREG(os.fstat(descriptor).st_mode):
                raise StorageIntegrityError()
            fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return cls(descriptor)
        except BlockingIOError as exc:
            if descriptor is not None:
                os.close(descriptor)
            raise AccountRuntimeInUseError() from exc
        except (OSError, StorageIntegrityError) as exc:
            if descriptor is not None:
                os.close(descriptor)
            if isinstance(exc, StorageIntegrityError):
                raise
            raise ServiceUnavailableError() from exc

    def close(self) -> None:
        if self._descriptor is not None:
            descriptor, self._descriptor = self._descriptor, None
            os.close(descriptor)

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        self.close()
