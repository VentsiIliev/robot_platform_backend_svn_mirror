"""Bootstrap ownership of one account runtime; established storage is opened only."""
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory

from src.engine.auth.account_installation import AccountInstallation, AccountInstallationPaths
from src.engine.auth.account_installation import PreparedAccountInstallation
from src.engine.auth.account_runtime import AccountRuntime
from src.engine.auth.access_change_guard import SystemAccessChangeGuard
from src.engine.auth.account_runtime_lock import AccountRuntimeLock
from src.engine.auth.i_authorization_service import IAuthorizationService
from src.engine.auth.i_session_service import ISessionService
from src.shared_contracts.authorization.applications import ApplicationAccess
from src.shared_contracts.authorization.errors import StorageIntegrityError
from src.shared_contracts.authorization.results import Failure


def application_catalog(system_class) -> tuple[ApplicationAccess, ...]:
    policy = system_class.role_policy
    folders = {folder.folder_id: folder.name for folder in system_class.shell.folders}
    return tuple(ApplicationAccess(
        app.app_id, default_roles=frozenset(policy.default_permission_role_values),
        protected_roles=frozenset(policy.protected_app_role_values.get(app.app_id, ())),
        denied_roles=frozenset(policy.denied_folder_role_values.get(folders.get(app.folder_id, ""), ())),
    ) for app in system_class.shell.applications)


def account_installation_paths(robot_system) -> AccountInstallationPaths:
    from src.bootstrap.account_locations import paths_for_users_directory
    return paths_for_users_directory(Path(robot_system.storage_path("users")))


@dataclass(frozen=True)
class PreparedRuntime:
    installation: PreparedAccountInstallation
    ownership: AccountRuntimeLock

    def close(self) -> None:
        self.ownership.close()


def prepare_account_runtime(system_class, paths: AccountInstallationPaths | None = None) -> PreparedRuntime:
    """Validate storage and reserve one GUI before any robot/backend startup."""
    paths = paths or account_installation_paths(system_class)
    installation = AccountInstallation(paths).open_existing()
    return PreparedRuntime(installation, AccountRuntimeLock.acquire(paths.database))


def configure_account_runtime(robot_system, session: ISessionService,
                              paths: AccountInstallationPaths | None = None,
                              *, prepared: PreparedRuntime | None = None) -> AccountRuntime:
    existing = getattr(robot_system, "_account_runtime", None)
    if existing is not None:
        if existing.session is not session:
            raise ValueError("An account runtime cannot be rebound to a different session")
        return existing
    if robot_system.development_mode:
        if prepared is not None:
            raise ValueError("Development bypass must not adopt persisted account storage")
        # Explicit dev login bypass gets disposable empty storage, never customer data
        # or a hidden persisted privileged account. Account commands still deny the stub.
        temporary = TemporaryDirectory(prefix="robot-platform-dev-accounts-")
        robot_system.register_managed_resource(temporary, temporary.cleanup)
        root = Path(temporary.name)
        paths = AccountInstallationPaths(root / "data" / "accounts.sqlite3",
                                         root / "data" / "installation.json", root / "private" / "operator.key")
        initialized = AccountInstallation(paths).initialize_new()
        if isinstance(initialized, Failure):
            raise StorageIntegrityError(correlation_id=initialized.error.correlation_id)
        installation = initialized.value
        ownership = AccountRuntimeLock.acquire(paths.database)
    else:
        # No missing-store/failed-login fallback, CSV import, or implicit commissioning.
        prepared = prepared or prepare_account_runtime(type(robot_system), paths)
        installation, ownership = prepared.installation, prepared.ownership
    try:
        extensions = robot_system.account_access_extensions()
        activity = SystemAccessChangeGuard(session, robot_system.system_manager,
            extensions.activity_check or robot_system.get_account_access_change_block_reason,
            extensions.idle_reservation)
        runtime = AccountRuntime(installation, session, application_catalog(type(robot_system)),
                                 extra_rules=extensions.rules, resources=extensions.resources, activity_guard=activity)
    except BaseException:
        ownership.close()
        raise
    robot_system._account_runtime_lock = ownership
    robot_system._account_runtime = runtime
    robot_system._account_navigation = (
        _DevelopmentNavigation(session, type(robot_system).shell.applications)
        if robot_system.development_mode else runtime.authorization
    )
    return runtime


def close_account_runtime(robot_system) -> None:
    """Call after the owning robot system has stopped; the OS also releases on exit."""
    ownership = getattr(robot_system, "_account_runtime_lock", None)
    if isinstance(ownership, AccountRuntimeLock):
        ownership.close()


def get_account_runtime(robot_system) -> AccountRuntime:
    runtime = getattr(robot_system, "_account_runtime", None)
    if runtime is None:
        raise RuntimeError("Bootstrap must configure the account runtime with the shared session first")
    return runtime


def get_account_navigation(robot_system) -> IAuthorizationService:
    get_account_runtime(robot_system)
    return robot_system._account_navigation


class _DevelopmentNavigation(IAuthorizationService):
    """Explicit dev navigation bypass; conveys no account-management authority."""
    def __init__(self, session, applications):
        self._session = session
        self._apps = frozenset(app.app_id for app in applications)

    def can_access(self, user, app_id):
        return user is not None and self._session.current_user is user and app_id in self._apps

    def get_visible_apps(self, user, all_specs):
        return [spec for spec in all_specs if self.can_access(user, spec.app_id)]
