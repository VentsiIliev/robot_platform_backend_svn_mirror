"""Composition bundle for bootstrap; inject individual contracts into applications."""
from src.engine.audit.audit_history_service import AuditHistoryService
from src.engine.auth.account_access_context import AccountAccessContext
from src.engine.auth.account_authorization_adapter import AccountAuthorizationAdapter
from src.engine.auth.account_installation import PreparedAccountInstallation
from src.engine.auth.account_login_service import AccountLoginService
from src.engine.auth.account_policy_provider import AccountPolicyProvider
from src.engine.auth.account_service import AccountService
from src.engine.auth.account_session_service import AccountSessionService
from src.engine.auth.access_policy import AccessRule
from src.engine.auth.admin_commissioning_service import AdminCommissioningService
from src.engine.auth.login_token_service import LoginTokenService
from src.engine.auth.i_session_service import ISessionService
from src.engine.auth.i_access_resource_resolver import IAccessResourceResolver
from src.engine.auth.i_access_change_guard import IAccessChangeGuard
from src.engine.auth.permission_service import PermissionService
from src.engine.auth.recovery_service import RecoveryService
from src.engine.auth.versioned_access_service import VersionedAccessService
from src.shared_contracts.authorization.applications import ApplicationAccess


class AccountRuntime:
    """One session/authority source; no global lookup or Qt dependency.

    Bootstrap owns this bundle. Views/models/controllers never receive it; their
    application service adapters get only the specific service contracts needed.
    Application catalogs and domain rules come from robot-system composition.
    """
    def __init__(self, installation: PreparedAccountInstallation, session: ISessionService,
                 applications: tuple[ApplicationAccess, ...], extra_rules: tuple[AccessRule, ...] = (),
                 resources: IAccessResourceResolver | None = None,
                 activity_guard: IAccessChangeGuard | None = None) -> None:
        self.session = session
        self.policies = AccountPolicyProvider(installation.store, applications, extra_rules)
        contexts = AccountAccessContext(installation.store, session, resources)
        self.sessions = AccountSessionService(contexts, session)
        self.access = VersionedAccessService(contexts, self.policies)
        self.authorization = AccountAuthorizationAdapter(session, self.access)
        policy = self.policies.capture()
        # Account/permission/history rules are immutable system policy. Editable
        # application grants are captured afresh by the access-query service.
        self.accounts = AccountService(installation.store, session, policy, installation.credentials,
                                       activity_guard=activity_guard)
        self.login = AccountLoginService(installation.store, installation.credentials)
        self.login_tokens = LoginTokenService(installation.store, session, policy)
        self.commissioning = AdminCommissioningService(installation.store, installation.credentials)
        self.recovery = RecoveryService(installation.store, session, policy, installation.credentials,
                                         activity_guard=activity_guard)
        self.history = AuditHistoryService(installation.store, session, policy)
        self.permissions = PermissionService(
            installation.store, session, policy,
            app_ids=frozenset(app.app_id for app in applications),
            protected_roles={app.app_id: app.protected_roles for app in applications},
            denied_roles={app.app_id: app.denied_roles for app in applications},
            default_roles=(),
            default_app_roles={app.app_id: app.default_roles for app in applications},
            activity_guard=activity_guard,
        )
