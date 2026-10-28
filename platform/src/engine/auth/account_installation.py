"""Explicit fresh setup and fail-closed opening of an established install."""
from dataclasses import dataclass
from contextlib import contextmanager
from datetime import datetime, timezone
import json
from pathlib import Path
from uuid import uuid4

from src.engine.auth.account_store import IAccountStore
from src.engine.auth.fernet_credential_protector import FernetCredentialProtector
from src.engine.auth.i_credential_protector import ICredentialProtector
from src.engine.auth.protected_file_key_provider import ProtectedFileKeyProvider
from src.engine.auth.sqlite_account_store import SQLiteAccountStore
from src.engine.core.durable_files import atomic_write_json, store_lock
from src.shared_contracts.accounts.events import AuditEvent
from src.shared_contracts.authorization.errors import (
    ErrorCode, KeyMismatchError, ServiceError, ServiceUnavailableError, StorageIntegrityError,
)
from src.shared_contracts.authorization.results import Failure, Result, Success


@dataclass(frozen=True)
class AccountInstallationPaths:
    database: Path
    state: Path
    operator_key: Path

    def __post_init__(self):
        for name in self.__dataclass_fields__:
            object.__setattr__(self, name, Path(getattr(self, name)).absolute())
        paths = [getattr(self, name) for name in self.__dataclass_fields__]
        if (len(set(paths)) != len(paths)
                or self.database.parent == self.operator_key.parent):
            raise ValueError("Use distinct account/state paths and a separate private key directory")


@dataclass(frozen=True)
class PreparedAccountInstallation:
    installation_id: str
    store: IAccountStore
    credentials: ICredentialProtector


class AccountInstallation:
    """Composition helper; never select initialization merely because opening fails.

    initialize_new() provides empty-store setup: no credentials or grants are
    read from legacy files. Account import is deliberately unsupported.
    open_existing() is the ordinary startup path and creates no missing store/key.
    The state marker lives separately from SQLite to detect established-store loss.
    """
    _STAGES = {"creating_store", "store_ready", "key_ready", "active"}

    def __init__(self, paths: AccountInstallationPaths) -> None:
        self._paths = paths
        self._keys = ProtectedFileKeyProvider(paths.operator_key)

    def open_existing(self) -> PreparedAccountInstallation:
        if not self._paths.state.is_file():
            raise StorageIntegrityError()
        with self._state_lock():
            state = self._read_state()
            if state["stage"] != "active":
                raise StorageIntegrityError()
            return self._open_bound(state)

    def initialize_new(self) -> Result[PreparedAccountInstallation]:
        """Prepare an empty installation for new Manufacturer/Admin provisioning.

        Never deletes or replaces existing material. Repeated calls only resume
        this same setup, preserving accounts and credentials already committed.
        """
        with self._state_lock():
            if self._paths.state.exists():
                state = self._read_state()
            else:
                if self._paths.database.exists() or self._paths.operator_key.exists():
                    return Failure(ServiceError(ErrorCode.POLICY_VIOLATION,
                                                "installation.existing_material", uuid4().hex))
                state = {"schema_version": 1, "setup_mode": "fresh",
                         "stage": "creating_store", "installation_id": uuid4().hex,
                         "key_fingerprint": None}
                self._write_state(state)
            if state["stage"] == "active":
                return Success(self._open_bound(state))
            if state["stage"] == "creating_store":
                if self._paths.database.exists():
                    store = SQLiteAccountStore(self._paths.database)
                    with store.transaction() as transaction:
                        # No accounts can exist before this stage advances.
                        if transaction.list_accounts() or transaction.metadata("fresh_setup"):
                            raise StorageIntegrityError()
                else:
                    store = SQLiteAccountStore.initialize(self._paths.database)
                with store.transaction() as transaction:
                    transaction.set_metadata("installation_id", state["installation_id"])
                state["stage"] = "store_ready"
                self._write_state(state)
            store = SQLiteAccountStore(self._paths.database)
            with store.transaction() as transaction:
                if transaction.metadata("installation_id") != state["installation_id"]:
                    raise StorageIntegrityError()
                bound = transaction.metadata("operator_key_fingerprint")
            if state["stage"] == "store_ready":
                if bound is None:
                    provisioned = self._keys.provision_new()
                    if isinstance(provisioned, Failure) and provisioned.error.code != ErrorCode.ALREADY_EXISTS:
                        return provisioned
                    fingerprint = self._keys.load_key().fingerprint
                    with store.transaction() as transaction:
                        transaction.set_metadata("operator_key_fingerprint", fingerprint)
                    bound = fingerprint
                elif self._keys.load_key().fingerprint != bound:
                    raise KeyMismatchError()
                state.update(stage="key_ready", key_fingerprint=bound)
                self._write_state(state)
            prepared = self._open_bound(state)
            # Explicit setup verifies the key. Ordinary startup loads it lazily.
            if self._keys.load_key().fingerprint != state["key_fingerprint"]:
                raise KeyMismatchError()
            self._record_fresh_setup(prepared.store)
            state["stage"] = "active"
            self._write_state(state)
            return Success(prepared)

    @staticmethod
    def _record_fresh_setup(store):
        with store.transaction() as transaction:
            completed = transaction.metadata("fresh_setup")
            if completed == "1":
                return
            if completed is not None or transaction.list_accounts():
                raise StorageIntegrityError()
            transaction.append_event(AuditEvent(
                uuid4().hex, datetime.now(timezone.utc).isoformat(), None, None,
                "installation", transaction.metadata("installation_id"),
                "installation.created", "succeeded",
            ))
            transaction.set_metadata("fresh_setup", "1")

    def _open_bound(self, state):
        store = SQLiteAccountStore(self._paths.database)
        with store.transaction() as transaction:
            if (transaction.metadata("installation_id") != state["installation_id"]
                    or not state["key_fingerprint"]
                    or transaction.metadata("operator_key_fingerprint") != state["key_fingerprint"]):
                raise StorageIntegrityError()
        return PreparedAccountInstallation(state["installation_id"], store, FernetCredentialProtector(
            self._keys, key_fingerprint=state["key_fingerprint"],
        ))

    def _read_state(self):
        try:
            state = json.loads(self._paths.state.read_text(encoding="utf-8"))
            if (not isinstance(state, dict)
                    or not {"schema_version", "stage", "installation_id", "key_fingerprint"} <= state.keys()
                    or type(state.get("schema_version")) is not int or state["schema_version"] != 1
                    or state.get("setup_mode") != "fresh"
                    or state.get("stage") not in self._STAGES
                    or not isinstance(state.get("installation_id"), str) or not state["installation_id"]
                    or state.get("key_fingerprint") is not None and (
                        not isinstance(state["key_fingerprint"], str) or len(state["key_fingerprint"]) != 64
                        or any(c not in "0123456789abcdef" for c in state["key_fingerprint"])
                    )):
                raise ValueError("Invalid account installation state")
            return state
        except (OSError, ValueError, UnicodeError) as exc:
            raise StorageIntegrityError() from exc

    def _write_state(self, state):
        try:
            atomic_write_json(self._paths.state, state, mode=0o600)
        except OSError as exc:
            raise ServiceUnavailableError() from exc

    @contextmanager
    def _state_lock(self):
        try:
            with store_lock(self._paths.state):
                yield
        except OSError as exc:
            raise ServiceUnavailableError() from exc
