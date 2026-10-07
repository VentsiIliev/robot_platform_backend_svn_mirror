"""Dedicated kiosk password: PBKDF2 hash only, provisioned outside application code."""
import argparse
import getpass
import grp
import hashlib
import hmac
import json
import os
from pathlib import Path
import secrets
import stat
import tempfile
import time

DEFAULT_PASSWORD_FILE = Path('/etc/robot-platform/kiosk-password.json')
ITERATIONS = 600_000


def password_record(password: str) -> dict:
    if len(password) < 12:
        raise ValueError('Use a kiosk password of at least 12 characters')
    salt = secrets.token_bytes(32)
    digest = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, ITERATIONS)
    return {'version': 1, 'algorithm': 'pbkdf2-sha256', 'iterations': ITERATIONS,
            'salt': salt.hex(), 'digest': digest.hex()}


def write_password_file(path: Path, password: str, *, read_group: str | None = None) -> None:
    """Atomically replace the hash. The caller must provision the parent directory."""
    record = password_record(password)
    gid = grp.getgrnam(read_group).gr_gid if read_group else None
    fd, name = tempfile.mkstemp(prefix='.kiosk-password-', dir=path.parent)
    temporary = Path(name)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            if gid is not None:
                os.fchown(stream.fileno(), -1, gid)
                os.fchmod(stream.fileno(), 0o640)
            json.dump(record, stream)
            stream.write('\n')
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


class KioskPassword:
    def __init__(self, path: Path, *, clock=time.monotonic):
        self._path = path
        self._clock = clock
        self._failures = 0
        self._blocked_until = 0.0
        # Validate before starting hardware when kiosk mode is enabled.
        self._record = self._load()

    def _load(self):
        fd = os.open(self._path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        with os.fdopen(fd, 'r', encoding='utf-8') as stream:
            metadata = os.fstat(stream.fileno())
            if not stat.S_ISREG(metadata.st_mode) or metadata.st_size > 4096:
                raise ValueError('Kiosk password file must be a small regular file')
            if metadata.st_mode & 0o027:
                raise ValueError('Kiosk password file must not be group-writable or accessible to others')
            record = json.load(stream)
        if (not isinstance(record, dict) or record.get('version') != 1
                or record.get('algorithm') != 'pbkdf2-sha256'
                or record.get('iterations') != ITERATIONS):
            raise ValueError('Unsupported kiosk password file')
        salt = bytes.fromhex(record['salt'])
        digest = bytes.fromhex(record['digest'])
        if len(salt) != 32 or len(digest) != 32:
            raise ValueError('Invalid kiosk password hash')
        return salt, digest

    def verify(self, password: str) -> bool:
        if self._clock() < self._blocked_until:
            return False
        salt, expected = self._record
        actual = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, ITERATIONS)
        allowed = bool(password) and hmac.compare_digest(actual, expected)
        if allowed:
            self._failures = 0
        else:
            self._failures += 1
            if self._failures >= 5:
                self._blocked_until = self._clock() + 30
                self._failures = 0
        return allowed


def main(argv=None):
    parser = argparse.ArgumentParser(description='Set/rotate the dedicated kiosk exit password')
    parser.add_argument('--file', type=Path, default=DEFAULT_PASSWORD_FILE,
                        help='Hash file path (default: /etc/robot-platform/kiosk-password.json)')
    parser.add_argument("--read-group", help="Allow this OS group to read the hash (mode 0640)")
    args = parser.parse_args(argv)
    # Refuse redirected input rather than echoing a password through getpass fallback.
    if not os.isatty(0):
        parser.error('Run interactively in a terminal; password input must be hidden')
    password = getpass.getpass('New kiosk exit password (at least 12 characters): ')
    confirmation = getpass.getpass('Confirm password: ')
    if password != confirmation:
        parser.error('Passwords do not match')
    try:
        write_password_file(args.file, password, read_group=args.read_group)
    except (OSError, ValueError, KeyError) as exc:
        parser.error(str(exc))
    print(f'Kiosk password hash saved to {args.file}. Restart the application after rotation.')


if __name__ == '__main__':
    main()
