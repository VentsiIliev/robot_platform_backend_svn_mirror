from dataclasses import replace
import unittest
from unittest.mock import patch
from src.applications.user_management.model.user_management_model import UserManagementModel
from src.applications.user_management.model.permissions_model import PermissionsModel
from src.applications.user_management.service.stub_user_management_service import StubUserManagementService
from src.applications.user_management.service.i_user_management_service import NewUser, EditUser, UserFailure
from src.applications.user_management.service.i_user_management_service import HistoryEntry, UserSuccess


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

    def test_actor_columns_show_names_and_login_ids_without_rewriting_audit_references(self):
        created = self.model.create(NewUser("5", "New", "User", "Operator", "secret")).value
        self.model.page = self.model.load().value
        row = self.model.filtered_users("id", "5")[0]
        self.assertEqual(row.created_by_label, "Service Engineer (3)")
        self.assertEqual(row.updated_by_label, "Service Engineer (3)")
        self.assertEqual((row.created_by, row.updated_by), (created.created_by, created.updated_by))
        original = next(entry for entry in self.model.page.users if entry.account_id == created.account_id)
        self.assertEqual(original.created_by_label, "—")

    def test_filtering_actor_names_resolves_actors_outside_the_filtered_rows(self):
        self.model.create(NewUser("5", "New", "User", "Operator", "secret"))
        self.model.page = self.model.load().value
        self.assertEqual([row.login_id for row in self.model.filtered_users("created_by_label", "service engineer")], ["5"])
        self.assertEqual([row.login_id for row in self.model.filtered_users("updated_by_label", "(3)")], ["5"])

    def test_deleted_actor_is_not_misattributed_to_a_reused_login_id(self):
        self.model.create(NewUser("5", "New", "User", "Operator", "secret"))
        page = self.model.load().value
        rows = tuple(replace(row, account_id="replacement-maker") if row.account_id == "demo-maker" else row
                     for row in page.users)
        self.model.page = replace(page, users=rows)
        row = self.model.filtered_users("id", "5")[0]
        self.assertEqual(row.created_by, "demo-maker")
        self.assertEqual(row.created_by_label, "—")
        self.assertEqual(row.updated_by_label, "—")

    def test_initial_setup_and_unavailable_actors_have_a_safe_placeholder(self):
        initial = self.model.filtered_users("id", "1")[0]
        self.assertEqual((initial.created_by_label, initial.updated_by_label), ("—", "—"))
        self.model.page = replace(self.model.page,
            users=(replace(self.model.page.users[0], created_by="os:uid:0", updated_by="missing-id"),))
        unknown = self.model.filtered_users("", "")[0]
        self.assertEqual((unknown.created_by_label, unknown.updated_by_label), ("—", "—"))

    def test_history_resolves_known_actor_names_without_guessing_deleted_identities(self):
        events = (HistoryEntry("now", "demo-maker", "users.edit_profile", "succeeded"),
                  HistoryEntry("then", "deleted-identity", "users.edit_profile", "succeeded"))
        with patch.object(self.service, "history", return_value=UserSuccess(events)):
            history = self.model.history("demo-operator").value
        self.assertEqual(history[0].actor, "Service Engineer (3)")
        self.assertEqual(history[1].actor, "deleted-identity")
        self.assertEqual(events[0].actor, "demo-maker")
