import unittest
from src.applications.user_management.model.permissions_model import PermissionsModel
from src.applications.user_management.service.stub_user_management_service import StubUserManagementService
from src.applications.user_management.service.i_user_management_service import UserFailure


class PermissionsModelTests(unittest.TestCase):
    def setUp(self):
        self.service = StubUserManagementService()
        self.model = PermissionsModel(self.service)
        self.model.page = self.model.load().value

    def test_toggle_uses_the_displayed_revision_and_preserves_other_roles(self):
        result = self.model.set_permission("demo", "Operator", False)
        self.assertEqual(dict(result.value.grants)["demo"], ("Admin", "Manufacturer"))
        self.assertEqual(result.value.revision, self.model.page.revision + 1)

    def test_stale_editor_cannot_overwrite_a_newer_update(self):
        self.model.set_permission("demo", "Operator", False)
        self.assertIsInstance(self.model.set_permission("demo", "Admin", False), UserFailure)

    def test_read_is_deferred_until_load(self):
        self.assertIsNone(PermissionsModel(self.service).page)

    def test_edit_before_load_is_rejected(self):
        with self.assertRaises(RuntimeError):
            PermissionsModel(self.service).set_permission("demo", "Operator", True)
