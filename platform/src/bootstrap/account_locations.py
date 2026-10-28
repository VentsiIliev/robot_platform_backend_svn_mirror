"""Shared source/frozen account paths and a secret-free deployment record."""
import argparse
import hashlib
import json
import os
from pathlib import Path

from src.engine.auth.account_installation import AccountInstallation, AccountInstallationPaths
from src.shared_contracts.authorization.errors import ServiceException


def paths_for_users_directory(users_directory: Path) -> AccountInstallationPaths:
    users_directory = Path(users_directory).absolute()
    database = users_directory / "accounts.sqlite3"
    explicit_key = os.environ.get("ROBOT_PLATFORM_ACCOUNT_KEY_FILE")
    if explicit_key:
        key = Path(explicit_key)
        if not key.is_absolute():
            raise ValueError("ROBOT_PLATFORM_ACCOUNT_KEY_FILE must be absolute")
    else:
        state_home = Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local" / "state"))
        if not state_home.is_absolute():
            raise ValueError("XDG_STATE_HOME must be absolute")
        identity = hashlib.sha256(str(database).encode()).hexdigest()[:24]
        key = state_home / "robot-platform/account-keys" / identity / "operator.key"
    return AccountInstallationPaths(database, users_directory / "account-installation.json", key)


def installed_account_paths(data_root: Path, target: dict) -> AccountInstallationPaths:
    system = target["robot_system"]
    if not isinstance(system, str) or not system or any(c not in "abcdefghijklmnopqrstuvwxyz0123456789_" for c in system):
        raise ValueError("Invalid installed robot-system identity")
    return paths_for_users_directory(Path(data_root).resolve() / system / "storage/users")


def deployment_record(paths: AccountInstallationPaths, backup_location: Path | None = None) -> dict:
    if backup_location is not None and not backup_location.is_absolute():
        raise ValueError("Backup location must be absolute")
    installation_id = None
    if paths.state.exists() or paths.database.exists():
        installation_id = AccountInstallation(paths).open_existing().installation_id
    return {"format": 1, "database": str(paths.database), "state": str(paths.state),
            "operator_key": str(paths.operator_key), "platform_uid": os.getuid(),
            "installation_id": installation_id, "backup_location": str(backup_location) if backup_location else None,
            "maintenance_command": "/usr/local/sbin/robot-account-maintenance"}


def main(argv=None, *, paths: AccountInstallationPaths):
    parser = argparse.ArgumentParser(description="Report account installation paths without starting hardware")
    parser.add_argument("--backup-location", type=Path)
    args = parser.parse_args(argv)
    try:
        print(json.dumps(deployment_record(paths, args.backup_location), indent=2))
        return 0
    except ServiceException as exc:
        print(f"Account record failed: {exc.error.code.value}; reference {exc.error.correlation_id}.")
        return 4
    except ValueError:
        print("Specify an absolute backup location.")
        return 2
