from dataclasses import dataclass
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from src.engine.auth.access_policy import AccessRule, RoleGrant
from src.engine.auth.account_installation import PreparedAccountInstallation
from src.engine.auth.account_principal import AccountPrincipal
from src.engine.auth.account_runtime import AccountRuntime
from src.engine.auth.i_access_resource_resolver import IAccessResourceResolver
from src.shared_contracts.accounts.authentication import LoginCredentials
from src.shared_contracts.authorization.access import AccessKind, AccessRequest, ResourceFacts, ResourceRef
from src.shared_contracts.authorization.applications import ApplicationAccess
from src.shared_contracts.authorization.errors import ErrorCode
from src.shared_contracts.authorization.permissions import UpdateAppPermissions
from src.shared_contracts.authorization.results import Failure, Success
import tests.engine.auth.test_account_service as fixtures


APPLICATIONS = (
    ApplicationAccess("dashboard", default_roles=frozenset({"Admin", "Operator"})),
    ApplicationAccess("service", default_roles=frozenset({"Admin", "Operator"}), denied_roles=frozenset({"Operator"})),
    ApplicationAccess("administration", default_roles=frozenset({"Admin", "Operator"}), denied_roles=frozenset({"Operator"})),
    ApplicationAccess("future_app", default_roles=frozenset()),
)


class AccountRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.AccountServiceTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.prepared = PreparedAccountInstallation("fixture", self.fixture.store, self.fixture.credentials)
        self.runtime = AccountRuntime(self.prepared, self.fixture.session, APPLICATIONS)

    def test_shared_session_connects_login_accounts_permissions_and_navigation(self):
        self.fixture.session.logout()
        self.assertIsInstance(self.runtime.accounts.list_users(), Failure)
        identity = self.runtime.login.login(LoginCredentials("1", "initial-secret")).value
        self.runtime.session.login(AccountPrincipal(identity.account, identity.credential_version))
        self.assertIsInstance(self.runtime.accounts.list_users(), Success)
        self.assertIsInstance(self.runtime.permissions.read_permissions(), Failure)
        self.assertTrue(self.runtime.authorization.can_access(self.runtime.session.current_user, "dashboard"))

    def test_operator_cannot_open_restricted_apps_even_when_grants_allow(self):
        self.fixture.login(self.fixture.operator)
        user = self.fixture.session.current_user
        self.assertTrue(self.runtime.authorization.can_access(user, "dashboard"))
        self.assertFalse(self.runtime.authorization.can_access(user, "service"))
        self.assertFalse(self.runtime.authorization.can_access(user, "administration"))

    def test_manufacturer_sees_all_registered_apps_without_per_app_grants(self):
        self.fixture.login(self.fixture.manufacturer)
        specs = [SimpleNamespace(app_id=app.app_id) for app in APPLICATIONS]
        self.assertEqual(self.runtime.authorization.get_visible_apps(self.fixture.session.current_user, specs), specs)
        self.assertFalse(self.runtime.authorization.can_access(self.fixture.session.current_user, "not_registered"))

    def test_permission_updates_take_effect_in_fresh_access_snapshots(self):
        self.fixture.login(self.fixture.operator)
        request = (AccessRequest(AccessKind.APPLICATION, "dashboard"),)
        before = self.runtime.access.evaluate(request).value
        self.assertTrue(before.decisions[0].allowed)
        self.fixture.login(self.fixture.manufacturer)
        revision = self.runtime.permissions.read_permissions().value.revision
        self.runtime.permissions.update_permissions(UpdateAppPermissions("dashboard", ("Admin",), revision))
        self.fixture.login(self.fixture.operator)
        after = self.runtime.access.evaluate(request).value
        self.assertFalse(after.decisions[0].allowed)
        self.assertGreater(after.policy_revision, before.policy_revision)

    def test_permissions_editor_effective_defaults_match_navigation(self):
        self.fixture.login(self.fixture.manufacturer)
        snapshot = self.runtime.permissions.read_permissions().value
        grants = {grant.app_id: set(grant.roles) for grant in snapshot.grants}
        for account in (self.fixture.admin, self.fixture.operator, self.fixture.manufacturer):
            self.fixture.login(account)
            user = self.fixture.session.current_user
            for app in APPLICATIONS:
                self.assertEqual(self.runtime.authorization.can_access(user, app.app_id), account.summary.role in grants[app.app_id])

    def test_policy_change_during_query_returns_conflict_instead_of_stale_grant(self):
        original = self.runtime.policies.capture
        calls = [0]
        def capture_then_change():
            calls[0] += 1
            if calls[0] == 2:
                with self.fixture.store.transaction() as transaction:
                    transaction.set_metadata("permission_revision", "2")
            return original()
        with patch.object(self.runtime.policies, "capture", side_effect=capture_then_change):
            result = self.runtime.access.evaluate((AccessRequest(AccessKind.APPLICATION, "dashboard"),))
        self.assertIsInstance(result, Failure)
        self.assertEqual(result.error.code, ErrorCode.CONFLICT)

    def test_navigation_adapter_rejects_stale_session_results(self):
        user = self.fixture.session.current_user
        original = self.runtime.access.evaluate
        def evaluate_then_switch(requests):
            result = original(requests)
            self.fixture.login(self.fixture.manufacturer)
            return result
        with patch.object(self.runtime.access, "evaluate", side_effect=evaluate_then_switch):
            self.assertFalse(self.runtime.authorization.can_access(user, "dashboard"))

    def test_domain_action_and_resource_extension_needs_no_engine_policy_edits(self):
        @dataclass(frozen=True)
        class RecipeFacts(ResourceFacts):
            editable: bool = True
        reference = ResourceRef("recipe", "recipe-1")
        class Recipes(IAccessResourceResolver):
            def resolve(self, requested):
                return RecipeFacts(reference) if requested == reference else None
        runtime = AccountRuntime(self.prepared, self.fixture.session, APPLICATIONS,
                                 extra_rules=(AccessRule(AccessKind.ACTION, "paint.edit", (RoleGrant("Admin"),),
                                                         target_kind="recipe"),), resources=Recipes())
        result = runtime.access.evaluate((AccessRequest(AccessKind.ACTION, "paint.edit", reference),))
        self.assertTrue(result.value.decisions[0].allowed)


if __name__ == "__main__":
    unittest.main()
