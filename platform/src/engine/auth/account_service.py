"""Authorized account commands with atomic profile, credential, and history writes."""
from dataclasses import replace
from uuid import uuid4

from src.engine.auth.account_operation_runner import AccountOperationRunner
from src.engine.auth.account_store import IAccountStore, StoredAccount
from src.engine.auth.i_access_policy import IAccessPolicy
from src.engine.auth.i_account_service import IAccountService
from src.engine.auth.i_credential_protector import ICredentialProtector
from src.engine.auth.i_access_change_guard import IAccessChangeGuard
from src.engine.auth.i_session_service import ISessionService
from src.shared_contracts.accounts.commands import (
    ChangePassword, ChangeRole, CreateAccount, DeleteAccount, EditProfile,
    RevealPassword, RevealedPassword,
)
from src.shared_contracts.accounts.events import FieldChange
from src.shared_contracts.accounts.records import AccountChange, AccountSummary, UserRole
from src.shared_contracts.authorization.access import ResourceRef
from src.shared_contracts.authorization.actions import UserAction
from src.shared_contracts.authorization.errors import ErrorCode
from src.shared_contracts.authorization.results import Success


class AccountService(IAccountService):
    def __init__(self, store: IAccountStore, session: ISessionService,
                 policy: IAccessPolicy, credentials: ICredentialProtector, *, clock=None,
                 activity_guard: IAccessChangeGuard | None = None) -> None:
        self._credentials = credentials
        self._operations = AccountOperationRunner(store, session, policy, clock=clock, activity_guard=activity_guard)
        self._clock = self._operations.clock

    def list_users(self):
        def read(transaction, actor, target):
            return Success(tuple(account.summary for account in transaction.list_accounts()))
        return self._execute(UserAction.VIEW, None, None, read)

    def create_user(self, command: CreateAccount):
        if (not all(isinstance(getattr(command, name), str) for name in
                    ("login_id", "first_name", "last_name", "role", "password", "email"))
                or not command.login_id or not command.first_name.strip() or not command.last_name.strip()
                or not command.password or command.role not in {r.value for r in UserRole}):
            return self._failure(ErrorCode.INVALID_INPUT)

        def create(transaction, actor, target):
            if transaction.get_by_login(command.login_id) is not None:
                return self._failure(ErrorCode.ALREADY_EXISTS)
            now = self._clock()
            summary = AccountSummary(
                uuid4().hex, command.login_id, command.first_name, command.last_name,
                command.role, command.email, True, 1, now, actor.summary.account_id,
                now, actor.summary.account_id,
            )
            stored = StoredAccount(summary, 1, self._credentials.hash_password(command.password),
                                   self._encrypt(command.role, command.password))
            transaction.insert(stored)
            if command.role == UserRole.ADMIN and transaction.metadata("commissioned") == "0":
                transaction.set_metadata("commissioned", "1")
            changes = tuple(FieldChange(name, None, str(getattr(summary, name)))
                            for name in ("login_id", "first_name", "last_name", "role", "email"))
            self._audit(transaction, actor, summary.account_id, UserAction.CREATE,
                        changes=changes, password_changed=True)
            return Success(summary)
        return self._execute(UserAction.CREATE, ResourceRef("new_account_role", command.role), None, create)

    def edit_profile(self, command: EditProfile):
        if (not self._valid_target(command)
                or not all(isinstance(getattr(command, name), str) for name in ("first_name", "last_name", "email"))
                or not command.first_name.strip() or not command.last_name.strip()):
            return self._failure(ErrorCode.INVALID_INPUT)

        def edit(transaction, actor, target):
            changes = tuple(FieldChange(name, getattr(target.summary, name), getattr(command, name))
                            for name in ("first_name", "last_name", "email")
                            if getattr(target.summary, name) != getattr(command, name))
            if not changes:
                return Success(AccountChange(target.summary, False))
            summary = self._edited(target.summary, actor, **{
                name: getattr(command, name) for name in ("first_name", "last_name", "email")
            })
            transaction.replace(replace(target, summary=summary))
            self._audit(transaction, actor, summary.account_id, UserAction.EDIT_PROFILE, changes=changes)
            return Success(AccountChange(summary, True))
        return self._execute(UserAction.EDIT_PROFILE, ResourceRef("account", command.account_id),
                             command.expected_revision, edit)

    def change_password(self, command: ChangePassword):
        if (not self._valid_target(command) or not isinstance(command.new_password, str)
                or not command.new_password or not isinstance(command.current_password, str)):
            return self._failure(ErrorCode.INVALID_INPUT)

        def change(transaction, actor, target):
            if (target.summary.account_id == actor.summary.account_id
                    and not self._credentials.verify_password(command.current_password, target.password_hash)):
                return self._failure(ErrorCode.INVALID_PROOF)
            summary = self._edited(target.summary, actor)
            transaction.replace(StoredAccount(
                summary, target.credential_version + 1,
                self._credentials.hash_password(command.new_password),
                self._encrypt(summary.role, command.new_password),
            ))
            self._audit(transaction, actor, summary.account_id, UserAction.CHANGE_PASSWORD,
                        password_changed=True)
            return Success(summary)
        return self._execute(UserAction.CHANGE_PASSWORD, ResourceRef("account", command.account_id),
                             command.expected_revision, change)

    def change_role(self, command: ChangeRole):
        if (not self._valid_target(command) or command.role not in {r.value for r in UserRole}
                or command.new_password is not None and not isinstance(command.new_password, str)):
            return self._failure(ErrorCode.INVALID_INPUT)

        def change(transaction, actor, target):
            if command.role == target.summary.role:
                return Success(AccountChange(target.summary, False))
            if self._last_admin(transaction, target) and command.role != UserRole.ADMIN:
                return self._failure(ErrorCode.POLICY_VIOLATION)
            # Cross the recoverable/non-recoverable credential boundary with a
            # fresh secret: a previously revealed Operator password must not
            # become a valid Admin/Manufacturer credential after promotion.
            needs_password = (command.role == UserRole.OPERATOR
                              or target.summary.role == UserRole.OPERATOR)
            if needs_password and not command.new_password:
                return self._failure(ErrorCode.INVALID_INPUT)
            if needs_password and self._credentials.verify_password(command.new_password, target.password_hash):
                return self._failure(ErrorCode.INVALID_INPUT)
            summary = self._edited(target.summary, actor, role=command.role)
            transaction.replace(replace(target, summary=summary,
                                        credential_version=target.credential_version + 1,
                                        password_hash=self._credentials.hash_password(command.new_password)
                                        if command.new_password else target.password_hash,
                                        operator_ciphertext=self._encrypt(command.role, command.new_password)
                                        if command.role == UserRole.OPERATOR else None))
            self._audit(transaction, actor, summary.account_id, UserAction.CHANGE_ROLE,
                        changes=(FieldChange("role", target.summary.role, command.role),),
                        password_changed=bool(command.new_password))
            return Success(AccountChange(summary, True))
        return self._execute(UserAction.CHANGE_ROLE, ResourceRef("account", command.account_id),
                             command.expected_revision, change)

    def delete_user(self, command: DeleteAccount):
        if not self._valid_target(command):
            return self._failure(ErrorCode.INVALID_INPUT)
        def delete(transaction, actor, target):
            if self._last_admin(transaction, target):
                return self._failure(ErrorCode.POLICY_VIOLATION)
            transaction.delete(target.summary.account_id)
            self._audit(transaction, actor, target.summary.account_id, UserAction.DELETE)
            return Success(None)
        return self._execute(UserAction.DELETE, ResourceRef("account", command.account_id),
                             command.expected_revision, delete)

    def reveal_operator_password(self, command: RevealPassword):
        if not isinstance(command.account_id, str) or not command.account_id:
            return self._failure(ErrorCode.INVALID_INPUT)
        def reveal(transaction, actor, target):
            if target.summary.role != UserRole.OPERATOR or target.operator_ciphertext is None:
                return self._failure(ErrorCode.POLICY_VIOLATION)
            password = self._credentials.decrypt_operator_password(target.operator_ciphertext)
            self._audit(transaction, actor, target.summary.account_id, UserAction.REVEAL_PASSWORD)
            return Success(RevealedPassword(password))
        return self._execute(UserAction.REVEAL_PASSWORD, ResourceRef("account", command.account_id), None, reveal)

    def _execute(self, action, reference, expected_revision, operation):
        if action in {UserAction.CHANGE_PASSWORD, UserAction.CHANGE_ROLE, UserAction.DELETE}:
            return self._operations.execute_change(action, reference, expected_revision, operation)
        return self._operations.execute(action, reference, expected_revision, operation)

    def _encrypt(self, role, password):
        return self._credentials.encrypt_operator_password(password) if role == UserRole.OPERATOR else None

    def _edited(self, summary, actor, **fields):
        return replace(summary, revision=summary.revision + 1, updated_at=self._clock(),
                       updated_by=actor.summary.account_id, **fields)

    @staticmethod
    def _last_admin(transaction, target):
        return (target.summary.role == UserRole.ADMIN and target.summary.enabled
                and sum(account.summary.role == UserRole.ADMIN and account.summary.enabled
                        for account in transaction.list_accounts()) <= 1)

    def _audit(self, transaction, actor, target_id, action, *, outcome="succeeded",
               changes=(), password_changed=False):
        self._operations.record(transaction, actor, target_id, action, outcome=outcome,
                                changes=changes, password_changed=password_changed)

    @staticmethod
    def _failure(code):
        return AccountOperationRunner.failure(code)

    @staticmethod
    def _valid_target(command):
        return (isinstance(command.account_id, str) and bool(command.account_id)
                and type(command.expected_revision) is int and command.expected_revision > 0)
