from dataclasses import replace
import os
from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock, patch

from src.engine.auth.account_maintenance_service import AccountMaintenanceService
from src.engine.auth.account_store import IAccountStore
from src.engine.auth.i_maintenance_authority import IMaintenanceAuthority
from src.engine.auth.sqlite_account_store import SQLiteAccountTransaction
from src.engine.auth.unix_maintenance_authority import UnixMaintenanceAuthority
from src.shared_contracts.accounts.maintenance import CreateManufacturer, OperatingSystemActor, ResetManufacturerPassword
from src.shared_contracts.authorization.errors import AuditPersistenceError, ErrorCode, ServiceError
from src.shared_contracts.authorization.results import Failure, Success
import tests.engine.auth.test_account_service as fixtures


class FakeAuthority(IMaintenanceAuthority):
    def __init__(self, allowed=True):
        self.allowed = allowed

    def current_actor(self):
        if self.allowed:
            return Success(OperatingSystemActor(0, "root", 1000, "service-tech"))
        return Failure(ServiceError(ErrorCode.ACCESS_DENIED, "maintenance.os_authority_required", "test"))


class AccountMaintenanceTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.AccountServiceTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.authority = FakeAuthority()
        self.service = AccountMaintenanceService(self.fixture.store, self.authority, self.fixture.credentials,
                                                 clock=lambda: "2026-10-27T15:00:00+00:00")

    def test_os_authority_is_required_before_any_store_access(self):
        store = MagicMock(spec=IAccountStore)
        service = AccountMaintenanceService(store, FakeAuthority(False), self.fixture.credentials)
        commands = (
            service.has_enabled_manufacturer(),
            service.inspect_manufacturer("4"),
            service.create_manufacturer(CreateManufacturer("5", "New", "Manufacturer", "secret")),
            service.reset_manufacturer_password(ResetManufacturerPassword("id", 1, "secret")),
        )
        self.assertTrue(all(result.error.code == ErrorCode.ACCESS_DENIED for result in commands))
        store.transaction.assert_not_called()

    def test_readiness_requires_an_enabled_manufacturer_without_mutating_accounts(self):
        self.assertTrue(self.service.has_enabled_manufacturer().value)
        before = self.fixture.get(self.fixture.manufacturer)
        with self.fixture.store.transaction() as transaction:
            transaction.replace(replace(before, summary=replace(before.summary, enabled=False)))
        self.assertFalse(self.service.has_enabled_manufacturer().value)
        with self.fixture.store.transaction() as transaction:
            transaction.delete(before.summary.account_id)
        self.assertFalse(self.service.has_enabled_manufacturer().value)

    def test_platform_manufacturer_session_does_not_grant_os_maintenance(self):
        self.fixture.login(self.fixture.manufacturer)
        self.authority.allowed = False
        result = self.service.inspect_manufacturer("4")
        self.assertEqual(result.error.code, ErrorCode.ACCESS_DENIED)

    def test_reset_preserves_account_identity_and_records_os_actor(self):
        before = self.fixture.manufacturer
        result = self.service.reset_manufacturer_password(ResetManufacturerPassword(before.summary.account_id, 1, "reset-secret"))
        self.assertIsInstance(result, Success)
        stored = self.fixture.get(before)
        self.assertEqual(stored.summary.account_id, before.summary.account_id)
        self.assertEqual(stored.summary.created_at, before.summary.created_at)
        self.assertEqual(stored.summary.role, "Manufacturer")
        self.assertEqual(stored.summary.updated_by, "os:0")
        self.assertEqual(stored.credential_version, 2)
        self.assertIsNone(stored.operator_ciphertext)
        self.assertTrue(self.fixture.credentials.verify_password("reset-secret", stored.password_hash))
        event = self.fixture.history(before.summary.account_id)[0]
        self.assertEqual(event.actor_id, "os:0")
        self.assertIsNone(event.actor_role)
        self.assertEqual(event.actor_method, "os_maintenance")
        self.assertEqual(event.os_actor, OperatingSystemActor(0, "root", 1000, "service-tech"))
        self.assertNotIn("reset-secret", repr(event))

    def test_reset_invalidates_old_manufacturer_session(self):
        self.fixture.login(self.fixture.manufacturer)
        self.service.reset_manufacturer_password(ResetManufacturerPassword(
            self.fixture.manufacturer.summary.account_id, 1, "reset-secret"))
        self.assertEqual(self.fixture.service.list_users().error.code, ErrorCode.AUTHENTICATION_REQUIRED)

    def test_reset_only_targets_existing_enabled_manufacturer_and_expected_revision(self):
        admin = self.service.reset_manufacturer_password(ResetManufacturerPassword(self.fixture.admin.summary.account_id, 1, "secret"))
        self.assertEqual(admin.error.code, ErrorCode.POLICY_VIOLATION)
        stale = self.service.reset_manufacturer_password(ResetManufacturerPassword(self.fixture.manufacturer.summary.account_id, 99, "secret"))
        self.assertEqual(stale.error.code, ErrorCode.CONFLICT)
        with self.fixture.store.transaction() as transaction:
            transaction.replace(replace(self.fixture.manufacturer, summary=replace(self.fixture.manufacturer.summary, enabled=False)))
        disabled = self.service.reset_manufacturer_password(ResetManufacturerPassword(self.fixture.manufacturer.summary.account_id, 1, "secret"))
        self.assertEqual(disabled.error.message_key, "maintenance.account_disabled")

    def test_creation_provisions_manufacturer_with_no_operator_encryption_dependency(self):
        with patch.object(self.fixture.credentials, "encrypt_operator_password", side_effect=AssertionError("not needed")):
            result = self.service.create_manufacturer(CreateManufacturer("5", "Service", "Engineer", "secret"))
        self.assertIsInstance(result, Success)
        self.assertEqual(result.value.role, "Manufacturer")
        self.assertEqual(result.value.created_by, "os:0")
        self.assertEqual(self.fixture.history(result.value.account_id)[0].os_actor.sudo_username, "service-tech")
        with self.fixture.store.transaction() as transaction:
            self.assertEqual(transaction.metadata("commissioned"), "0")

    def test_duplicate_creation_does_not_replace_existing_account(self):
        result = self.service.create_manufacturer(CreateManufacturer("1", "Service", "Engineer", "secret"))
        self.assertEqual(result.error.code, ErrorCode.ALREADY_EXISTS)
        self.assertEqual(self.fixture.get(self.fixture.admin), self.fixture.admin)

    def test_audit_failure_rolls_back_os_authorized_reset(self):
        before = self.fixture.manufacturer
        with patch.object(SQLiteAccountTransaction, "append_event", side_effect=AuditPersistenceError):
            with self.assertRaises(AuditPersistenceError):
                self.service.reset_manufacturer_password(ResetManufacturerPassword(before.summary.account_id, 1, "reset-secret"))
        self.assertEqual(self.fixture.get(before), before)


class UnixMaintenanceAuthorityTests(unittest.TestCase):
    def test_nonroot_cannot_claim_root_with_environment_variables(self):
        with patch("os.geteuid", return_value=1000), patch.dict(os.environ, {"SUDO_UID": "0", "SUDO_USER": "root"}):
            result = UnixMaintenanceAuthority().current_actor()
        self.assertIsInstance(result, Failure)

    def test_root_records_matching_sudo_origin_as_environment_context(self):
        def lookup(uid):
            return SimpleNamespace(pw_name="root" if uid == 0 else "service-tech")
        with patch("os.geteuid", return_value=0), patch("pwd.getpwuid", side_effect=lookup), \
                patch.dict(os.environ, {"SUDO_UID": "1000", "SUDO_USER": "service-tech"}):
            result = UnixMaintenanceAuthority().current_actor()
        self.assertEqual(result.value, OperatingSystemActor(0, "root", 1000, "service-tech"))

    def test_invalid_origin_does_not_become_an_os_identity(self):
        with patch("os.geteuid", return_value=0), patch("pwd.getpwuid", return_value=SimpleNamespace(pw_name="root")), \
                patch.dict(os.environ, {"SUDO_UID": "not-a-uid", "SUDO_USER": "unverified"}):
            result = UnixMaintenanceAuthority().current_actor()
        self.assertIsNone(result.value.sudo_uid)


if __name__ == "__main__":
    unittest.main()
