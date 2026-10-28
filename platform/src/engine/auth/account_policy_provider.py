"""Merge editable application grants with immutable system role constraints."""
from src.engine.auth.access_policy import AccessPolicy, AccessRule, RoleGrant
from src.engine.auth.account_store import IAccountStore
from src.engine.auth.i_access_policy_provider import IAccessPolicyProvider
from src.engine.auth.user_access_rules import user_access_rules
from src.shared_contracts.accounts.records import UserRole
from src.shared_contracts.authorization.access import AccessKind
from src.shared_contracts.authorization.applications import ApplicationAccess
from src.shared_contracts.authorization.errors import StorageIntegrityError


class AccountPolicyProvider(IAccessPolicyProvider):
    def __init__(self, store: IAccountStore, applications: tuple[ApplicationAccess, ...],
                 extra_rules: tuple[AccessRule, ...] = ()) -> None:
        self._store = store
        self._applications = tuple(applications)
        self._extra = tuple(extra_rules)
        known_roles = {role.value for role in UserRole}
        if (len({app.app_id for app in self._applications}) != len(self._applications)
                or any(not (app.default_roles | app.protected_roles | app.denied_roles) <= known_roles
                       for app in self._applications)):
            raise ValueError("Application catalog contains duplicates or unknown roles")

    def capture(self):
        with self._store.transaction() as transaction:
            grants = transaction.read_permissions()
            try:
                revision = int(transaction.metadata("permission_revision") or "1")
                if revision < 1:
                    raise ValueError("Invalid permission revision")
            except ValueError as exc:
                raise StorageIntegrityError() from exc
        roles = frozenset(role.value for role in UserRole)
        rules = list(user_access_rules(admin_role=UserRole.ADMIN.value, operator_role=UserRole.OPERATOR.value))
        rules.extend(self._extra)
        for app in self._applications:
            allowed = (set(grants.get(app.app_id, app.default_roles)) | app.protected_roles) & roles
            rules.append(AccessRule(AccessKind.APPLICATION, app.app_id,
                                    tuple(RoleGrant(role) for role in sorted(allowed)), denied_roles=app.denied_roles))
        return AccessPolicy(roles=roles, manufacturer_role=UserRole.MANUFACTURER.value,
                            rules=tuple(rules), revision=revision)
