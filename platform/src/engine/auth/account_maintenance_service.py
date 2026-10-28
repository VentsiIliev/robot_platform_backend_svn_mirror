"""OS-authorized Manufacturer provisioning and last-resort password reset."""
from dataclasses import replace
from datetime import datetime, timezone
from uuid import uuid4

from src.engine.auth.account_store import IAccountStore, StoredAccount
from src.engine.auth.i_account_maintenance_service import IAccountMaintenanceService
from src.engine.auth.i_maintenance_authority import IMaintenanceAuthority
from src.engine.auth.i_password_hasher import IPasswordHasher
from src.shared_contracts.accounts.events import AuditEvent, FieldChange
from src.shared_contracts.accounts.maintenance import CreateManufacturer, ResetManufacturerPassword
from src.shared_contracts.accounts.records import AccountSummary, UserRole
from src.shared_contracts.authorization.errors import ErrorCode, ServiceError
from src.shared_contracts.authorization.results import Failure, Success


class AccountMaintenanceService(IAccountMaintenanceService):
    def __init__(self, store: IAccountStore, authority: IMaintenanceAuthority,
                 passwords: IPasswordHasher, *, clock=None) -> None:
        self._store, self._authority, self._passwords = store, authority, passwords
        self._clock = clock or (lambda: datetime.now(timezone.utc).isoformat())

    def inspect_manufacturer(self, login_id):
        authorized = self._authority.current_actor()
        if isinstance(authorized, Failure):
            return authorized
        if not isinstance(login_id, str) or not login_id:
            return self._failure(ErrorCode.INVALID_INPUT)
        with self._store.transaction() as transaction:
            account = transaction.get_by_login(login_id)
            if account is None:
                return self._failure(ErrorCode.NOT_FOUND)
            if account.summary.role != UserRole.MANUFACTURER:
                return self._failure(ErrorCode.POLICY_VIOLATION)
            return Success(account.summary)

    def create_manufacturer(self, command: CreateManufacturer):
        authorized = self._authority.current_actor()
        if isinstance(authorized, Failure):
            return authorized
        if (not all(isinstance(getattr(command, name), str) for name in
                    ("login_id", "first_name", "last_name", "password", "email"))
                or not command.login_id or not command.first_name.strip()
                or not command.last_name.strip() or not command.password):
            return self._failure(ErrorCode.INVALID_INPUT)
        actor = authorized.value
        with self._store.transaction() as transaction:
            if transaction.get_by_login(command.login_id) is not None:
                return self._failure(ErrorCode.ALREADY_EXISTS)
            now = self._clock()
            summary = AccountSummary(uuid4().hex, command.login_id, command.first_name,
                                     command.last_name, UserRole.MANUFACTURER.value, command.email,
                                     True, 1, now, actor.reference, now, actor.reference)
            transaction.insert(StoredAccount(summary, 1, self._passwords.hash_password(command.password)))
            transaction.append_event(AuditEvent(
                uuid4().hex, now, actor.reference, None, "os_maintenance", summary.account_id,
                "maintenance.manufacturer_created", "succeeded", (
                    FieldChange("login_id", None, summary.login_id),
                    FieldChange("role", None, summary.role),
                ), True, actor,
            ))
            return Success(summary)

    def reset_manufacturer_password(self, command: ResetManufacturerPassword):
        authorized = self._authority.current_actor()
        if isinstance(authorized, Failure):
            return authorized
        if (not isinstance(command.account_id, str) or not command.account_id
                or type(command.expected_revision) is not int or command.expected_revision < 1
                or not isinstance(command.new_password, str) or not command.new_password):
            return self._failure(ErrorCode.INVALID_INPUT)
        actor = authorized.value
        with self._store.transaction() as transaction:
            account = transaction.get(command.account_id)
            if account is None:
                return self._failure(ErrorCode.NOT_FOUND)
            if account.summary.role != UserRole.MANUFACTURER:
                return self._failure(ErrorCode.POLICY_VIOLATION)
            if not account.summary.enabled:
                return self._failure(ErrorCode.POLICY_VIOLATION, "maintenance.account_disabled")
            if account.summary.revision != command.expected_revision:
                return self._failure(ErrorCode.CONFLICT)
            now = self._clock()
            summary = replace(account.summary, revision=account.summary.revision + 1,
                              updated_by=actor.reference, updated_at=now)
            transaction.replace(StoredAccount(summary, account.credential_version + 1,
                                               self._passwords.hash_password(command.new_password)))
            transaction.replace_recovery_verifiers(summary.account_id, ())
            transaction.append_event(AuditEvent(
                uuid4().hex, now, actor.reference, None, "os_maintenance", summary.account_id,
                "maintenance.manufacturer_password_reset", "succeeded",
                password_changed=True, os_actor=actor,
            ))
            return Success(summary)

    @staticmethod
    def _failure(code, message_key=None):
        return Failure(ServiceError(code, message_key or "maintenance." + code.value, uuid4().hex))
