from dataclasses import asdict
from io import BytesIO

from src.applications.user_management.service.i_user_management_service import (
    IUserManagementService, UserEntry, UserPage, UserError, UserErrorCode, UserFailure, UserSuccess,
    ControlAccess, ScreenAccess, SecretDisplay, QrDisplay, HistoryEntry, PermissionsPage,
)
from src.engine.auth.i_account_service import IAccountService
from src.engine.auth.i_access_service import IAccessService
from src.engine.auth.i_login_token_service import ILoginTokenService
from src.engine.auth.i_recovery_service import IRecoveryService
from src.engine.auth.i_permission_service import IPermissionService
from src.engine.auth.i_session_service import ISessionService
from src.engine.audit.i_audit_history_service import IAuditHistoryService
from src.shared_contracts.accounts.commands import (
    CreateAccount, EditProfile, ChangePassword, ChangeRole, DeleteAccount, RevealPassword,
)
from src.shared_contracts.accounts.events import HistoryQuery
from src.shared_contracts.accounts.login_tokens import IssueLoginToken
from src.shared_contracts.accounts.recovery import GenerateRecoveryCodes
from src.shared_contracts.accounts.records import UserRole
from src.shared_contracts.authorization.access import AccessKind, AccessRequest, ResourceRef
from src.shared_contracts.authorization.actions import UserAction, RecoveryAction, AuditAction
from src.shared_contracts.authorization.features import UserFeature
from src.shared_contracts.authorization.permissions import UpdateAppPermissions
from src.shared_contracts.authorization.errors import ErrorCode, ServiceException
from src.shared_contracts.authorization.results import Failure


class UserManagementApplicationService(IUserManagementService):
    def __init__(self, *, accounts: IAccountService, access: IAccessService,
                 tokens: ILoginTokenService, recovery: IRecoveryService,
                 permissions: IPermissionService, history: IAuditHistoryService,
                 session: ISessionService):
        self._accounts, self._access, self._tokens = accounts, access, tokens
        self._recovery, self._permissions, self._history = recovery, permissions, history
        self._session = session

    @staticmethod
    def _entry(account):
        return UserEntry(**asdict(account))

    @classmethod
    def _call(cls, operation, convert=lambda value: value):
        try:
            result = operation()
            if isinstance(result, Failure):
                return cls._error(result.error)
            return UserSuccess(convert(result.value))
        except ServiceException as exc:
            return cls._error(exc.error)

    @staticmethod
    def _error(error):
        credential_codes = {ErrorCode.KEY_UNAVAILABLE, ErrorCode.KEY_INTEGRITY, ErrorCode.UNSAFE_KEY_STORAGE,
                            ErrorCode.KEY_MISMATCH, ErrorCode.CREDENTIAL_INTEGRITY}
        if error.code in credential_codes:
            code = UserErrorCode.CREDENTIAL_STORAGE
        elif error.code == ErrorCode.STORAGE_INTEGRITY:
            code = UserErrorCode.INTEGRITY
        else:
            code = {item.value: item for item in UserErrorCode}.get(error.code.value, UserErrorCode.UNAVAILABLE)
        return UserFailure(UserError(code, error.correlation_id))

    def load_users(self):
        snapshot = self._session.snapshot()
        result = self._call(self._accounts.list_users, lambda rows: tuple(self._entry(row) for row in rows))
        if isinstance(result, UserFailure):
            return result
        if self._session.snapshot().revision != snapshot.revision:
            return UserFailure(UserError("conflict"))
        actor = next((row for row in result.value if row.account_id == getattr(snapshot.user, "account_id", None)), None)
        if actor is None:
            return UserFailure(UserError("authentication_required"))
        return UserSuccess(UserPage(result.value, actor.account_id, actor.role, snapshot.revision))

    def session_revision(self) -> int:
        return self._session.snapshot().revision

    def access(self, target_id):
        target = ResourceRef("account", target_id) if target_id else None
        target_role = None
        if target_id:
            summaries = self._call(self._accounts.list_users)
            if isinstance(summaries, UserFailure):
                return summaries
            target_role = next((account.role for account in summaries.value if account.account_id == target_id), None)
        declarations = (
            ("add", AccessRequest(AccessKind.ACTION, UserAction.CREATE, ResourceRef("new_account_role", "Operator"))),
            ("edit", AccessRequest(AccessKind.ACTION, UserAction.EDIT_PROFILE, target)),
            ("delete", AccessRequest(AccessKind.ACTION, UserAction.DELETE, target)),
            ("password", AccessRequest(AccessKind.ACTION, UserAction.CHANGE_PASSWORD, target)),
            ("reveal", AccessRequest(AccessKind.ACTION, UserAction.REVEAL_PASSWORD, target)),
            ("role", AccessRequest(AccessKind.ACTION, UserAction.CHANGE_ROLE, target)),
            ("qr", AccessRequest(AccessKind.ACTION, UserAction.ISSUE_LOGIN_TOKEN, target)),
            ("history", AccessRequest(AccessKind.ACTION, AuditAction.VIEW)),
            ("codes", AccessRequest(AccessKind.ACTION, RecoveryAction.ISSUE)),
            ("permissions", AccessRequest(AccessKind.FEATURE, UserFeature.APP_PERMISSIONS)),
        )
        roles = tuple(role.value for role in UserRole)
        requests = tuple(request for _, request in declarations) + tuple(
            AccessRequest(AccessKind.ACTION, UserAction.CREATE, ResourceRef("new_account_role", role)) for role in roles)
        def convert(snapshot):
            current_role = getattr(getattr(self._session.current_user, "role", None), "value", None)
            controls = tuple(ControlAccess(key,
                decision.role_eligible and (key != "codes" or current_role == "Admin"),
                decision.role_eligible and (key != "codes" or current_role == "Admin"),
                decision.allowed and (key != "reveal" or target_role == "Operator"))
                for (key, _), decision in zip(declarations, snapshot.decisions))
            allowed_roles = tuple(role for role, decision in zip(roles, snapshot.decisions[len(declarations):]) if decision.allowed)
            return ScreenAccess(snapshot.session_revision, snapshot.policy_revision, controls, allowed_roles)
        return self._call(lambda: self._access.evaluate(requests), convert)

    def create(self, command):
        if not isinstance(command.login_id, str) or not command.login_id.isnumeric():
            return UserFailure(UserError("invalid_input"))
        return self._call(lambda: self._accounts.create_user(CreateAccount(
            command.login_id, command.first_name, command.last_name, command.role, command.password, command.email)), self._entry)

    def edit(self, command):
        return self._call(lambda: self._accounts.edit_profile(EditProfile(
            command.account_id, command.revision, command.first_name, command.last_name, command.email)),
            lambda change: self._entry(change.account))

    def change_password(self, command):
        return self._call(lambda: self._accounts.change_password(ChangePassword(
            command.account_id, command.revision, command.new_password, command.current_password)), self._entry)

    def change_role(self, command):
        return self._call(lambda: self._accounts.change_role(ChangeRole(
            command.account_id, command.revision, command.role, command.new_password)),
            lambda change: self._entry(change.account))

    def delete(self, account_id, revision):
        return self._call(lambda: self._accounts.delete_user(DeleteAccount(account_id, revision)))

    def reveal(self, account_id):
        return self._call(lambda: self._accounts.reveal_operator_password(RevealPassword(account_id)),
                          lambda revealed: SecretDisplay(revealed.password))

    def issue_qr(self, account_id, revision):
        result = self._call(lambda: self._tokens.issue(IssueLoginToken(account_id, revision)))
        if isinstance(result, UserFailure):
            return result
        import qrcode
        output = BytesIO()
        qrcode.make(result.value.payload).save(output, format="PNG")
        return UserSuccess(QrDisplay(output.getvalue()))

    def generate_recovery_codes(self, current_password):
        return self._call(lambda: self._recovery.generate_codes(GenerateRecoveryCodes(current_password)),
                          lambda codes: SecretDisplay("\n".join(codes.codes)))

    def history(self, account_id):
        def convert(events):
            return tuple(HistoryEntry(event.occurred_at, event.actor_id or event.actor_method,
                                     event.action_id, event.outcome,
                                     "; ".join(change.field + ": " + str(change.before) + " -> " + str(change.after)
                                               for change in event.changes)
                                     + ("; password changed" if event.password_changed else "")) for event in events)
        return self._call(lambda: self._history.list_events(HistoryQuery(account_id)), convert)

    def _permissions_page(self, snapshot):
        roles = tuple(role.value for role in UserRole)
        locked = tuple((grant.app_id, role) for grant in snapshot.grants for role in roles
                       if role not in grant.editable_roles)
        return PermissionsPage(snapshot.revision, tuple(role.value for role in UserRole),
                               tuple((grant.app_id, grant.roles) for grant in snapshot.grants), locked)

    def permissions(self):
        return self._call(self._permissions.read_permissions, self._permissions_page)

    def set_permission(self, app_id, roles, revision):
        return self._call(lambda: self._permissions.update_permissions(UpdateAppPermissions(app_id, roles, revision)),
                          self._permissions_page)
