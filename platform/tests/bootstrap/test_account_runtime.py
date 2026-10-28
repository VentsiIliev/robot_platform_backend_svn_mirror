from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch

from src.bootstrap.account_runtime import (
    account_installation_paths, application_catalog, configure_account_runtime, get_account_navigation,
    close_account_runtime,
)
from src.engine.auth.account_installation import AccountInstallation, AccountInstallationPaths, PreparedAccountInstallation
from src.engine.auth.account_runtime import AccountRuntime
from src.engine.auth.access_extensions import AccountAccessExtensions
from src.engine.auth.access_policy import AccessRule, RoleGrant
from src.engine.auth.i_access_resource_resolver import IAccessResourceResolver
from src.engine.auth.user_session import UserSession
from src.applications.login.stub_login_application_service import _StubUser
from src.shared_contracts.declarations.system_specs import ApplicationSpec, FolderSpec, RolePolicy, ShellSetup
from src.shared_contracts.authorization.errors import StorageIntegrityError
from src.shared_contracts.authorization.results import Failure
from src.shared_contracts.authorization.access import AccessKind, AccessRequest, ResourceFacts, ResourceRef
import tests.engine.auth.test_account_service as fixtures


class _System:
    system_manager = None
    role_policy = RolePolicy(role_values=["Manufacturer", "Admin", "Operator"],
                             default_permission_role_values=["Admin"],
                             denied_folder_role_values={"ADMIN": ["Operator"], "SERVICE": ["Operator"]})
    shell = ShellSetup([FolderSpec(1, "PRODUCTION", "Production"), FolderSpec(2, "ADMIN", "Administration")],
                       [ApplicationSpec("Dashboard", 1), ApplicationSpec("Accounts", 2)])

    def __init__(self, root, development=False):
        self.root, self.development_mode = root, development
        self.resources = []

    def storage_path(self, *parts):
        return str(self.root.joinpath(*parts))

    def register_managed_resource(self, resource, cleanup):
        self.resources.append(cleanup)
        return resource

    def account_access_extensions(self):
        return getattr(self, "extensions", AccountAccessExtensions())

    def get_account_access_change_block_reason(self):
        return None


class AccountBootstrapTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.system = _System(self.root / "system")
        self.addCleanup(close_account_runtime, self.system)
        self.session = UserSession()
        self.paths = AccountInstallationPaths(self.root / "data" / "accounts.sqlite3",
                                              self.root / "data" / "installation.json",
                                              self.root / "private" / "operator.key")

    def test_runtime_open_does_not_initialize_missing_store(self):
        with self.assertRaises(StorageIntegrityError):
            configure_account_runtime(self.system, self.session, self.paths)
        self.assertFalse(self.paths.database.exists())
        self.assertFalse(self.paths.operator_key.exists())

    def test_second_runtime_cannot_bypass_the_active_platforms_idle_guard(self):
        from src.shared_contracts.authorization.errors import AccountRuntimeInUseError
        AccountInstallation(self.paths).initialize_new()
        configure_account_runtime(self.system, self.session, self.paths)
        another = _System(self.root / "other")
        with self.assertRaises(AccountRuntimeInUseError):
            configure_account_runtime(another, UserSession(), self.paths)

    def test_runtime_uses_one_session_and_fresh_empty_installation(self):
        AccountInstallation(self.paths).initialize_new()
        runtime = configure_account_runtime(self.system, self.session, self.paths)
        self.assertIs(runtime.session, self.session)
        self.assertIs(configure_account_runtime(self.system, self.session, self.paths), runtime)
        self.assertTrue(runtime.commissioning.status().required)
        with runtime.accounts._operations._store.transaction() as transaction:
            self.assertEqual(transaction.list_accounts(), ())
        with self.assertRaises(ValueError):
            configure_account_runtime(self.system, UserSession(), self.paths)

    def test_dev_bypass_uses_disposable_empty_storage_without_account_authority(self):
        self.system.development_mode = True
        runtime = configure_account_runtime(self.system, self.session, self.paths)
        self.addCleanup(self.system.resources[0])
        user = _StubUser()
        self.session.login(user)
        self.assertTrue(get_account_navigation(self.system).can_access(user, "accounts"))
        self.assertFalse(get_account_navigation(self.system).can_access(user, "unknown"))
        self.assertIsInstance(runtime.accounts.list_users(), Failure)
        self.assertFalse(self.paths.database.exists())

    def test_key_location_is_separate_and_can_be_explicitly_configured(self):
        with patch.dict("os.environ", {"XDG_STATE_HOME": str(self.root / "state")}, clear=True):
            paths = account_installation_paths(self.system)
        self.assertNotEqual(paths.database.parent, paths.operator_key.parent)
        self.assertTrue(paths.operator_key.is_relative_to(self.root / "state"))
        with patch.dict("os.environ", {"ROBOT_PLATFORM_ACCOUNT_KEY_FILE": str(self.root / "other" / "operator.key")}, clear=True):
            self.assertEqual(account_installation_paths(self.system).operator_key, self.root / "other" / "operator.key")
        with patch.dict("os.environ", {"ROBOT_PLATFORM_ACCOUNT_KEY_FILE": "relative.key"}, clear=True):
            with self.assertRaises(ValueError):
                account_installation_paths(self.system)

    def test_bootstrap_adopts_robot_system_domain_rules_and_resource_resolver(self):
        fixture = fixtures.AccountServiceTests()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        reference = ResourceRef("recipe", "recipe-1")
        class Recipes(IAccessResourceResolver):
            def resolve(self, requested):
                return ResourceFacts(reference) if requested == reference else None
        self.system.extensions = AccountAccessExtensions((
            AccessRule(AccessKind.ACTION, "paint.recipe.edit", (RoleGrant("Admin"),), target_kind="recipe"),
        ), Recipes())
        installation = PreparedAccountInstallation("fixture", fixture.store, fixture.credentials)
        self.paths.database.parent.mkdir()
        self.paths.database.touch()
        with patch.object(AccountInstallation, "open_existing", return_value=installation):
            runtime = configure_account_runtime(self.system, fixture.session, self.paths)
        result = runtime.access.evaluate((AccessRequest(AccessKind.ACTION, "paint.recipe.edit", reference),))
        self.assertTrue(result.value.decisions[0].allowed)


class SystemRoleCatalogTests(unittest.TestCase):
    def test_every_supported_system_has_three_roles_and_immutable_operator_restrictions(self):
        from src.robot_systems.paint.paint_robot_system import PaintRobotSystem
        from src.robot_systems.paint_auto_dry.paint_robot_system import AutomaticDryerPaintRobotSystem
        from src.robot_systems.paint_tray_dry.paint_robot_system import TrayDryerPaintRobotSystem
        from src.robot_systems.glue.glue_robot_system import GlueRobotSystem
        from src.robot_systems.welding.welding_robot_system import WeldingRobotSystem
        from src.robot_systems.twin_robot.twin_robot_system import TwinRobotSystem
        from src.robot_systems.ROBOT_SYSTEM_BLUEPRINT.my_robot_system import MyRobotSystem
        fixture = fixtures.AccountServiceTests()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        installation = PreparedAccountInstallation("fixture", fixture.store, fixture.credentials)
        for system in (PaintRobotSystem, AutomaticDryerPaintRobotSystem, TrayDryerPaintRobotSystem,
                       GlueRobotSystem, WeldingRobotSystem, TwinRobotSystem, MyRobotSystem):
            with self.subTest(system=system.__name__):
                self.assertEqual(set(system.role_policy.role_values), {"Manufacturer", "Admin", "Operator"})
                catalog = application_catalog(system)
                folders = {folder.folder_id: folder.name for folder in system.shell.folders}
                by_id = {app.app_id: app for app in catalog}
                restricted = [spec for spec in system.shell.applications if folders[spec.folder_id] in {"ADMIN", "SERVICE"}]
                for spec in restricted:
                    self.assertIn("Operator", by_id[spec.app_id].denied_roles)
                    with fixture.store.transaction() as transaction:
                        transaction.write_permissions(spec.app_id, ("Operator",))
                runtime = AccountRuntime(installation, fixture.session, catalog)
                fixture.login(fixture.operator)
                for spec in restricted:
                    self.assertFalse(runtime.authorization.can_access(fixture.session.current_user, spec.app_id))
                fixture.login(fixture.manufacturer)
                self.assertEqual(runtime.authorization.get_visible_apps(fixture.session.current_user, system.shell.applications),
                                 system.shell.applications)
