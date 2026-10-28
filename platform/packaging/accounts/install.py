#!/usr/bin/env python3
"""Install an administrator-reviewed maintenance payload into fixed root-owned paths."""
import argparse
import hashlib
import os
from pathlib import Path
import stat
import tempfile


def _trusted_directory(path, root, uid, gid):
    relative = path.relative_to(root)
    current = root
    for part in (None, *relative.parts):
        if part is not None:
            current = current / part
            try:
                current.mkdir(mode=0o755)
                os.chown(current, uid, gid)
            except FileExistsError:
                pass
        details = current.lstat()
        if (not stat.S_ISDIR(details.st_mode) or details.st_uid != uid
                or details.st_mode & 0o022):
            raise ValueError("Installation path must be administrator-owned and not writable by others")


def _publish(path, content, mode, uid, gid):
    if path.is_symlink():
        raise ValueError("Refusing a symlink installation file")
    if path.exists():
        details = path.stat()
        if not stat.S_ISREG(details.st_mode) or details.st_uid != uid or details.st_mode & 0o022:
            raise ValueError("Existing installation file has unsafe ownership or permissions")
    descriptor, temporary = tempfile.mkstemp(prefix=".account-tool-", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as output:
            output.write(content)
            output.flush()
            os.fchown(output.fileno(), uid, gid)
            os.fchmod(output.fileno(), mode)
            os.fsync(output.fileno())
        os.replace(temporary, path)
        directory = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        Path(temporary).unlink(missing_ok=True)


def install_payload(payload, root=Path("/"), *, uid=0, gid=0):
    """Stage parameters support isolated tests; the CLI always uses / and UID 0."""
    payload, root = Path(payload), Path(root)
    archive = payload / "account-maintenance.pyz"
    if archive.is_symlink() or not archive.is_file():
        raise ValueError("Expected a regular maintenance archive")
    content = archive.read_bytes()
    digest = hashlib.sha256(content).hexdigest()
    expected = (payload / "account-maintenance.pyz.sha256").read_text().split()
    if expected != [digest, "account-maintenance.pyz"]:
        raise ValueError("Maintenance archive checksum mismatch")
    directory = root / "usr/local/lib/robot-platform/accounts" / digest
    commands = root / "usr/local/sbin"
    _trusted_directory(directory, root, uid, gid)
    _trusted_directory(commands, root, uid, gid)
    installed = directory / archive.name
    _publish(installed, content, 0o444, uid, gid)
    executable = "/" + str(installed.relative_to(root))
    wrapper = commands / "robot-account-maintenance"
    _publish(wrapper, ('#!/bin/sh\nexec /usr/bin/python3 -I ' + executable + ' "$@"\n').encode(),
             0o755, uid, gid)
    return wrapper


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args(argv)
    if os.geteuid() != 0:
        print("Installation requires an OS administrator.")
        return 3
    try:
        print(f"Installed: {install_payload(Path(__file__).resolve().parent)}")
        return 0
    except (OSError, ValueError) as exc:
        print(f"Installation refused: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
