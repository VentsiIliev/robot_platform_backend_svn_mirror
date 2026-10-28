"""Manufacturer-controlled grants, with immutable folder and protected-role limits."""
import json

from src.engine.auth.account_operation_runner import AccountOperationRunner
from src.engine.auth.account_store import IAccountStore
from src.engine.auth.i_access_policy import IAccessPolicy
from src.engine.auth.i_permission_service import IPermissionService
from src.engine.auth.i_session_service import ISessionService
from src.engine.auth.i_access_change_guard import IAccessChangeGuard
from src.shared_contracts.accounts.events import FieldChange
from src.shared_contracts.accounts.records import UserRole
from src.shared_contracts.authorization.actions import PermissionAction
from src.shared_contracts.authorization.errors import ErrorCode, StorageIntegrityError
from src.shared_contracts.authorization.permissions import (
    ApplicationGrant, PermissionSnapshot, UpdateAppPermissions,
)
from src.shared_contracts.authorization.results import Success


class PermissionService(IPermissionService):
    def __init__(self, store: IAccountStore, session: ISessionService, policy: IAccessPolicy,
                 *, app_ids: frozenset[str], protected_roles=None, denied_roles=None,
                 default_roles: tuple[str, ...] = ("Admin",), default_app_roles=None,
                 activity_guard: IAccessChangeGuard | None = None) -> None:
        self._operations = AccountOperationRunner(store, session, policy, activity_guard=activity_guard)
        self._app_ids = frozenset(app_ids)
        self._protected = {key: frozenset(value) for key, value in (protected_roles or {}).items()}
        self._denied = {key: frozenset(value) for key, value in (denied_roles or {}).items()}
        self._defaults = tuple(default_roles)
        self._default_apps = {key: tuple(value) for key, value in (default_app_roles or {}).items()}

    def read_permissions(self):
        def read(transaction, actor, target):
            return Success(self._snapshot(transaction))
        return self._operations.execute(PermissionAction.MANAGE, None, None, read)

    def update_permissions(self, command: UpdateAppPermissions):
        known_roles = {role.value for role in UserRole}
        if (command.app_id not in self._app_ids or not set(command.roles) <= known_roles
                or type(command.expected_revision) is not int or command.expected_revision < 1):
            return self._operations.failure(ErrorCode.INVALID_INPUT)

        def update(transaction, actor, target):
            before = self._snapshot(transaction)
            if before.revision != command.expected_revision:
                return self._operations.failure(ErrorCode.CONFLICT)
            selected = set(command.roles) | {UserRole.MANUFACTURER.value}
            if (selected & self._denied.get(command.app_id, frozenset())
                    or not self._protected.get(command.app_id, frozenset()) <= selected):
                return self._operations.failure(ErrorCode.POLICY_VIOLATION)
            old = next(grant.roles for grant in before.grants if grant.app_id == command.app_id)
            roles = tuple(sorted(selected))
            if tuple(sorted(old)) == roles:
                return Success(before)
            transaction.write_permissions(command.app_id, roles)
            transaction.set_metadata("permission_revision", str(before.revision + 1))
            self._operations.record(transaction, actor, command.app_id, PermissionAction.MANAGE,
                                    changes=(FieldChange("allowed_roles", json.dumps(old), json.dumps(roles)),))
            return Success(self._snapshot(transaction))
        return self._operations.execute_change(PermissionAction.MANAGE, None, None, update)

    def _snapshot(self, transaction):
        grants = transaction.read_permissions()
        try:
            revision = int(transaction.metadata("permission_revision") or "1")
            if revision < 1:
                raise ValueError("Invalid permission revision")
        except ValueError as exc:
            raise StorageIntegrityError() from exc
        known = {role.value for role in UserRole}
        applications = []
        for app_id in sorted(self._app_ids):
            protected = self._protected.get(app_id, frozenset()) | {UserRole.MANUFACTURER.value}
            denied = self._denied.get(app_id, frozenset())
            selected = set(grants.get(app_id, self._default_apps.get(app_id, self._defaults))) & known
            applications.append(ApplicationGrant(app_id, tuple(sorted((selected | protected) - denied)),
                                                 tuple(sorted(known - protected - denied))))
        return PermissionSnapshot(revision, tuple(applications))
