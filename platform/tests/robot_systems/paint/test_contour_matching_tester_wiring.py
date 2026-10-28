import unittest

from src.robot_systems.paint.paint_robot_system import PaintRobotSystem


class TestContourMatchingTesterWiring(unittest.TestCase):
    def test_paint_exposes_matching_tester_in_tests_folder(self):
        app = next(
            spec
            for spec in PaintRobotSystem.shell.applications
            if spec.name == "ContourMatchingTester"
        )

        self.assertEqual(4, app.folder_id)
        self.assertEqual(
            ["Manufacturer"],
            PaintRobotSystem.role_policy.protected_app_role_values[app.app_id],
        )

    def test_manufacturer_can_revoke_admin_matching_tester_access_and_keep_its_own(self):
        from src.bootstrap.account_runtime import application_catalog
        from src.engine.auth.account_policy_provider import AccountPolicyProvider
        from src.engine.auth.permission_service import PermissionService
        from src.engine.auth.account_access_context import AccountAccessContext
        from src.shared_contracts.authorization.access import AccessKind, AccessRequest
        from src.shared_contracts.authorization.permissions import UpdateAppPermissions
        from tests.engine.auth.test_account_service import AccountServiceTests
        fixture = AccountServiceTests()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        catalog = application_catalog(PaintRobotSystem)
        provider = AccountPolicyProvider(fixture.store, catalog)
        permissions = PermissionService(fixture.store, fixture.session, fixture.policy,
            app_ids=frozenset(app.app_id for app in catalog),
            protected_roles={app.app_id: app.protected_roles for app in catalog},
            denied_roles={app.app_id: app.denied_roles for app in catalog},
            default_roles=('Admin',))
        fixture.login(fixture.manufacturer)
        before = permissions.read_permissions().value
        grant = next(item for item in before.grants if item.app_id == 'contourmatchingtester')
        self.assertIn('Admin', grant.editable_roles)
        changed = permissions.update_permissions(UpdateAppPermissions('contourmatchingtester', ('Manufacturer',), before.revision))
        self.assertNotIn('Admin', next(item.roles for item in changed.value.grants if item.app_id == 'contourmatchingtester'))
        request = AccessRequest(AccessKind.APPLICATION, 'contourmatchingtester')
        for account, allowed in ((fixture.admin, False), (fixture.manufacturer, True)):
            fixture.login(account)
            decision = provider.capture().decide(request, AccountAccessContext(fixture.store, fixture.session).capture())
            self.assertEqual(decision.allowed, allowed)


if __name__ == "__main__":
    unittest.main()
