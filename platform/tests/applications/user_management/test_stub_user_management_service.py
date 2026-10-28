import unittest
from src.applications.user_management.service.i_user_management_service import (
    IUserManagementService, NewUser, UserSuccess, UserFailure,
)
from src.applications.user_management.service.stub_user_management_service import StubUserManagementService


class StubContractTests(unittest.TestCase):
    def setUp(self):
        self.service = StubUserManagementService()

    def test_stub_implements_typed_contract_without_platform_dependencies(self):
        self.assertIsInstance(self.service, IUserManagementService)
        self.assertIsInstance(self.service.load_users(), UserSuccess)
        self.assertEqual({row.role for row in self.service.load_users().value.users},
                         {"Manufacturer", "Admin", "Operator"})

    def test_duplicate_login_id_is_a_typed_failure(self):
        result = self.service.create(NewUser("1", "Duplicate", "User", "Operator", "secret"))
        self.assertIsInstance(result, UserFailure)
        self.assertEqual(result.error.code, "already_exists")

    def test_only_operator_demo_passwords_can_be_revealed(self):
        self.assertIsInstance(self.service.reveal("demo-operator"), UserSuccess)
        self.assertIsInstance(self.service.reveal("demo-admin"), UserFailure)

    def test_no_plaintext_export_api_exists(self):
        self.assertFalse(hasattr(self.service, "send_access_package"))
        self.assertFalse(hasattr(self.service, "get_all_users"))

