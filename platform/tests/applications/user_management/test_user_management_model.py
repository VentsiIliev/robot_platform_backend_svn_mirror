import unittest
from src.applications.user_management.model.user_management_model import UserManagementModel
from src.applications.user_management.model.permissions_model import PermissionsModel
from src.applications.user_management.service.stub_user_management_service import StubUserManagementService
from src.applications.user_management.service.i_user_management_service import NewUser, EditUser, UserFailure


class UserManagementModelTests(unittest.TestCase):
    def setUp(self):
        self.service = StubUserManagementService()
        self.model = UserManagementModel(self.service, PermissionsModel(self.service))
        self.model.page = self.model.load().value

    def test_page_is_safe_and_filters_on_stable_keys(self):
        rows = self.model.filtered_users("firstName", "alice")
        self.assertEqual([row.login_id for row in rows], ["1"])
        self.assertTrue(all(row.get("password") == "" for row in self.model.page.users))
        self.assertEqual(len(self.model.filtered_users("", "")), 3)

    def test_create_and_edit_use_explicit_commands_and_revisions(self):
        created = self.model.create(NewUser("5", "New", "User", "Operator", "secret")).value
        edited = self.model.edit(EditUser(created.account_id, 1, "Changed", "User", "")).value
        self.assertEqual((edited.first_name, edited.revision), ("Changed", 2))
        self.assertIsInstance(self.model.edit(EditUser(created.account_id, 1, "Stale", "User", "")), UserFailure)

    def test_load_does_not_overwrite_the_displayed_snapshot_until_controller_accepts_it(self):
        old = self.model.page
        self.model.create(NewUser("5", "New", "User", "Operator", "secret"))
        result = self.model.load()
        self.assertIs(self.model.page, old)
        self.assertEqual(len(result.value.users), 4)

    def test_delete_is_bound_to_technical_identity(self):
        target = self.model.page.users[1]
        self.model.delete(target.account_id, target.revision)
        recreated = self.model.create(NewUser(target.login_id, "New", "Owner", "Operator", "secret")).value
        self.assertNotEqual(recreated.account_id, target.account_id)

    def test_secret_commands_are_redacted(self):
        command = NewUser("5", "New", "User", "Operator", "do-not-log")
        self.assertNotIn("do-not-log", repr(command))
        self.assertNotIn("DEMO ONLY", repr(self.model.reveal("demo-operator")))

    def test_generic_save_cannot_bypass_explicit_command_contracts(self):
        with self.assertRaises(NotImplementedError):
            self.model.save({"password": "replacement"})

