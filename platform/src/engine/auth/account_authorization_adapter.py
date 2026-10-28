"""Legacy navigation contract adapted to the current-session typed access service."""
from src.engine.auth.account_principal import IAccountPrincipal
from src.engine.auth.i_access_service import IAccessService
from src.engine.auth.i_authorization_service import IAuthorizationService
from src.engine.auth.i_session_service import ISessionService
from src.shared_contracts.authorization.access import AccessKind, AccessRequest
from src.shared_contracts.authorization.results import Success


class AccountAuthorizationAdapter(IAuthorizationService):
    def __init__(self, session: ISessionService, access: IAccessService) -> None:
        self._session, self._access = session, access

    def get_visible_apps(self, user, all_specs):
        revision = self._current_revision(user)
        if revision is None:
            return []
        specs = list(all_specs)
        result = self._access.evaluate(tuple(AccessRequest(AccessKind.APPLICATION, spec.app_id) for spec in specs))
        if not self._fresh(result, revision):
            return []
        return [spec for spec, decision in zip(specs, result.value.decisions) if decision.allowed]

    def can_access(self, user, app_id):
        revision = self._current_revision(user)
        if revision is None:
            return False
        result = self._access.evaluate((AccessRequest(AccessKind.APPLICATION, app_id),))
        return self._fresh(result, revision) and result.value.decisions[0].allowed

    def _current_revision(self, user):
        snapshot = self._session.snapshot()
        current = snapshot.user
        if (isinstance(user, IAccountPrincipal) and isinstance(current, IAccountPrincipal)
                and (user.account_id, user.credential_version) == (current.account_id, current.credential_version)):
            return snapshot.revision
        return None

    def _fresh(self, result, revision):
        return (isinstance(result, Success) and result.value.session_revision == revision
                and self._session.snapshot().revision == revision)
