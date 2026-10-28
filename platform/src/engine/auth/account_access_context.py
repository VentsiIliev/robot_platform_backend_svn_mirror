"""Revalidate account/version claims against storage rather than cached login roles."""
from src.engine.auth.account_principal import IAccountPrincipal
from src.engine.auth.account_store import IAccountStore, IAccountTransaction, StoredAccount
from src.engine.auth.i_access_context_provider import IAccessContextProvider
from src.engine.auth.i_access_resource_resolver import IAccessResourceResolver
from src.engine.auth.i_session_service import ISessionService, SessionSnapshot
from src.shared_contracts.accounts.records import UserRole
from src.shared_contracts.authorization.access import (
    AccessContext, Actor, ResourceFacts, ResourceRef,
)


def verified_session_account(transaction: IAccountTransaction, snapshot: SessionSnapshot) -> StoredAccount | None:
    user = snapshot.user
    if not isinstance(user, IAccountPrincipal):
        return None
    account = transaction.get(user.account_id)
    if (account is None or not account.summary.enabled
            or account.summary.login_id != user.user_id
            or account.credential_version != user.credential_version
            or account.summary.role not in {role.value for role in UserRole}):
        return None
    return account


class AccountAccessContext(IAccessContextProvider):
    def __init__(self, store: IAccountStore, session: ISessionService,
                 resources: IAccessResourceResolver | None = None) -> None:
        self._store = store
        self._session = session
        self._resources = resources

    def capture(self, target: ResourceRef | None = None) -> AccessContext:
        snapshot = self._session.snapshot()
        with self._store.transaction() as transaction:
            account = verified_session_account(transaction, snapshot)
            actor = Actor(account.summary.account_id, account.summary.role) if account else None
            facts = None
            if actor is not None and target is not None:
                if target.kind == "account":
                    stored = transaction.get(target.resource_id)
                    if stored is not None:
                        facts = ResourceFacts(target, stored.summary.account_id, stored.summary.role)
                elif target.kind == "new_account_role" and target.resource_id in {r.value for r in UserRole}:
                    facts = ResourceFacts(target, role=target.resource_id)
        if (actor is not None and target is not None and target.kind not in {"account", "new_account_role"}
                and self._resources is not None):
            facts = self._resources.resolve(target)
        return AccessContext(actor, snapshot.revision, facts)
