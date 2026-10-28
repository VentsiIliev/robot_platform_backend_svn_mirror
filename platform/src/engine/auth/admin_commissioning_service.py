"""Create the customer Admin once, independently of Manufacturer provisioning."""
from datetime import datetime, timezone
from uuid import uuid4

from src.engine.auth.account_store import IAccountStore, StoredAccount
from src.engine.auth.i_admin_commissioning_service import IAdminCommissioningService
from src.engine.auth.i_password_hasher import IPasswordHasher
from src.shared_contracts.accounts.commissioning import AdminSetupStatus, CreateFirstAdmin
from src.shared_contracts.accounts.events import AuditEvent, FieldChange
from src.shared_contracts.accounts.records import AccountSummary, UserRole
from src.shared_contracts.authorization.errors import ErrorCode, ServiceError, StorageIntegrityError
from src.shared_contracts.authorization.results import Failure, Success


class AdminCommissioningService(IAdminCommissioningService):
    def __init__(self, store: IAccountStore, passwords: IPasswordHasher) -> None:
        self._store, self._passwords = store, passwords

    def status(self):
        with self._store.transaction() as transaction:
            required = self._required(transaction)
            if required and any(account.summary.role == UserRole.ADMIN for account in transaction.list_accounts()):
                raise StorageIntegrityError()
            return AdminSetupStatus(required)

    def create_first_admin(self, command: CreateFirstAdmin):
        if (not all(isinstance(getattr(command, name), str) for name in
                    ("login_id", "first_name", "last_name", "password", "email"))
                or not command.login_id or not command.first_name.strip()
                or not command.last_name.strip() or not command.password):
            return self._failure(ErrorCode.INVALID_INPUT)
        with self._store.transaction() as transaction:
            if not self._required(transaction):
                return self._failure(ErrorCode.POLICY_VIOLATION)
            if any(account.summary.role == UserRole.ADMIN for account in transaction.list_accounts()):
                return self._failure(ErrorCode.POLICY_VIOLATION)
            if transaction.get_by_login(command.login_id) is not None:
                return self._failure(ErrorCode.ALREADY_EXISTS)
            now = datetime.now(timezone.utc).isoformat()
            summary = AccountSummary(uuid4().hex, command.login_id, command.first_name,
                                     command.last_name, UserRole.ADMIN.value, command.email,
                                     True, 1, now, None, now, None)
            transaction.insert(StoredAccount(summary, 1, self._passwords.hash_password(command.password)))
            transaction.set_metadata("commissioned", "1")
            transaction.append_event(AuditEvent(
                uuid4().hex, now, None, None, "commissioning", summary.account_id,
                "commissioning.admin_created", "succeeded", (
                    FieldChange("login_id", None, summary.login_id),
                    FieldChange("role", None, summary.role),
                ), password_changed=True,
            ))
            return Success(summary)

    @staticmethod
    def _required(transaction):
        state = transaction.metadata("commissioned")
        if state not in {"0", "1"}:
            raise StorageIntegrityError()
        return state == "0"

    @staticmethod
    def _failure(code):
        return Failure(ServiceError(code, "account." + code.value, uuid4().hex))
