"""Linux file durability primitives; no domain defaults or recovery policy."""
from contextlib import contextmanager
import fcntl
import json
import os
from pathlib import Path
import stat
import tempfile
from threading import RLock


class DurabilityError(OSError):
    """Replacement is visible, but directory durability could not be confirmed."""
    published = True


def sync_directory(path: Path) -> None:
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def ensure_directory(path: Path) -> None:
    path = Path(path)
    if path.is_dir():
        return
    ensure_directory(path.parent)
    try:
        path.mkdir()
    except FileExistsError:
        if not path.is_dir():
            raise
    sync_directory(path.parent)


def atomic_write_bytes(path: Path, data: bytes, *, mode: int | None = None) -> None:
    path = Path(path)
    ensure_directory(path.parent)
    try:
        previous = path.lstat()
    except FileNotFoundError:
        previous = None
    if previous is not None and not stat.S_ISREG(previous.st_mode):
        raise ValueError(f"Refusing to replace non-regular file: {path}")
    fd, temporary = tempfile.mkstemp(dir=path.parent, prefix=f'.{path.name}-')
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(data)
            stream.flush()
            if previous is not None:
                current = os.fstat(stream.fileno())
                if (current.st_uid, current.st_gid) != (previous.st_uid, previous.st_gid):
                    os.fchown(stream.fileno(), previous.st_uid, previous.st_gid)
            os.fchmod(stream.fileno(), mode if mode is not None else
                      stat.S_IMODE(previous.st_mode) if previous is not None else 0o600)
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        try:
            sync_directory(path.parent)
        except OSError as exc:
            raise DurabilityError(f"Replacement visible at {path}; durability unconfirmed: {exc}") from exc
    finally:
        Path(temporary).unlink(missing_ok=True)


def atomic_write_json(path: Path, value: object, *, mode: int | None = None) -> None:
    # Serialize before touching any destination; reject nonstandard NaN/Infinity.
    data = json.dumps(value, indent=2, allow_nan=False).encode('utf-8')
    atomic_write_bytes(path, data, mode=mode)


_registry_guard = RLock()
_store_locks: dict[str, RLock] = {}


@contextmanager
def store_lock(path: Path):
    """Serialize complete mutations across instances, threads and processes.

    Call once at the transaction boundary; nested acquisitions are unsupported.
    The stable sidecar is never replaced or removed.
    """
    path = Path(path).absolute()
    key = str(path.resolve())
    with _registry_guard:
        thread_lock = _store_locks.setdefault(key, RLock())
    with thread_lock:
        ensure_directory(path.parent)
        fd = os.open(str(path) + '.lock', os.O_CREAT | os.O_RDWR, 0o600)
        with os.fdopen(fd, 'a+b') as stream:
            fcntl.flock(stream.fileno(), fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(stream.fileno(), fcntl.LOCK_UN)
