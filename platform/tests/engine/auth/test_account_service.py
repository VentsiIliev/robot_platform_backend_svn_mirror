"""Account contract integration against real SQLite and fake credential protection."""
from dataclasses import replace
import hashlib
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch
from uuid import uuid4

from src.engine.auth.access_policy import AccessPolicy
from src.engine.auth.account_access_context import AccountAccessContext
from src.engine.auth.account_principal import AccountPrincipal
from src.engine.auth.account_service import AccountService
from src.engine.auth.account_login_service import AccountLoginService
from src.engine.auth.account_store import StoredAccount
from src.engine.auth.i_credential_protector import ICredentialProtector
from src.engine.auth.sqlite_account_store import SQLiteAccountStore, SQLiteAccountTransaction
from src.engine.auth.permission_service import PermissionService
from src.engine.audit.audit_history_service import AuditHistoryService
from src.engine.auth.user_access_rules import user_access_rules
from src.engine.auth.user_session import UserSession
from src.shared_contracts.accounts.commands import (
    ChangePassword, ChangeRole, CreateAccount, DeleteAccount, EditProfile, RevealPassword,
)
from src.shared_contracts.accounts.authentication import LoginCredentials
from src.shared_contracts.accounts.events import AuditEvent, HistoryQuery
from src.shared_contracts.accounts.records import AccountSummary
from src.shared_contracts.authorization.access import ResourceRef
from src.shared_contracts.authorization.errors import AuditPersistenceError, ErrorCode, StorageIntegrityError
from src.shared_contracts.authorization.results import Failure, Success
from src.shared_contracts.authorization.permissions import UpdateAppPermissions


class FakeCredentials(ICredentialProtector):
    """Test double only: token-to-secret mapping lives exclusively in test memory."""
    def __init__(self):
        self.secrets = {}

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def verify_password(self, password, encoded_hash):
        return self.hash_password(password) == encoded_hash

    def encrypt_operator_password(self, password):
        token = uuid4().hex.encode()
        self.secrets[token] = password
        return token

    def decrypt_operator_password(self, ciphertext):
        return self.secrets[ciphertext]


class AccountServiceTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / "accounts.sqlite3"
        self.store = SQLiteAccountStore.initialize(self.path)
        self.credentials = FakeCredentials()
        self.session = UserSession()
        self.policy = AccessPolicy(
            roles=frozenset({"Manufacturer", "Admin", "Operator"}),
            manufacturer_role="Manufacturer",
            rules=user_access_rules(admin_role="Admin", operator_role="Operator"),
        )
        self.service = AccountService(self.store, self.session, self.policy, self.credentials,
                                      clock=lambda: "2026-10-27T12:00:00+00:00")
        self.admin = self.seed("1", "Admin")
        self.other_admin = self.seed("2", "Admin")
        self.operator = self.seed("3", "Operator")
        self.manufacturer = self.seed("4", "Manufacturer")
        self.login(self.admin)

    def seed(self, login, role):
        summary = AccountSummary(uuid4().hex, login, "First", "Last", role, "", True, 1,
                                 None, None, None, None)
        account = StoredAccount(summary, 1, self.credentials.hash_password("initial-secret"),
                                 self.credentials.encrypt_operator_password("initial-secret")
                                 if role == "Operator" else None)
        with self.store.transaction() as transaction:
            transaction.insert(account)
        return account

    def login(self, account):
        self.session.login(AccountPrincipal(account.summary, account.credential_version))

    def get(self, account):
        with self.store.transaction() as transaction:
            return transaction.get(account.summary.account_id)

    def history(self, account_id):
        with self.store.transaction() as transaction:
            return transaction.history(HistoryQuery(account_id))

    def test_admin_creates_operator_with_trusted_metadata_and_secret_free_history(self):
        result = self.service.create_user(CreateAccount("5", "New", "Operator", "Operator", "new-secret"))
        self.assertIsInstance(result, Success)
        account = result.value
        self.assertEqual(account.created_by, self.admin.summary.account_id)
        self.assertEqual(account.updated_by, self.admin.summary.account_id)
        self.assertEqual(account.created_at, "2026-10-27T12:00:00+00:00")
        events = self.history(account.account_id)
        self.assertEqual(len(events), 1)
        self.assertTrue(events[0].password_changed)
        self.assertNotIn("new-secret", repr(events))
        self.assertNotIn("password_hash", repr(account))

    def test_admin_cannot_create_admin_or_manufacturer(self):
        for role in ("Admin", "Manufacturer", "Developer", "Viewer"):
            result = self.service.create_user(CreateAccount("5", "New", "User", role, "new-secret"))
            self.assertIsInstance(result, Failure)
        self.assertEqual(len(self.service.list_users().value), 4)

    def test_profile_edit_changes_only_allowed_fields_and_noop_does_not_touch_history(self):
        summary = self.operator.summary
        result = self.service.edit_profile(EditProfile(summary.account_id, 1, "Changed", "Last", ""))
        self.assertTrue(result.value.changed)
        self.assertEqual(result.value.account.created_at, summary.created_at)
        self.assertEqual(result.value.account.revision, 2)
        event = self.history(summary.account_id)[0]
        self.assertEqual(event.changes[0].field, "first_name")
        self.assertEqual((event.changes[0].before, event.changes[0].after), ("First", "Changed"))
        noop = self.service.edit_profile(EditProfile(summary.account_id, 2, "Changed", "Last", ""))
        self.assertFalse(noop.value.changed)
        self.assertEqual(noop.value.account, result.value.account)
        self.assertEqual(len(self.history(summary.account_id)), 1)

    def test_admin_profile_scope_allows_self_and_operator_but_not_other_admin(self):
        for account, allowed in ((self.admin, True), (self.operator, True), (self.other_admin, False),
                                  (self.manufacturer, False)):
            with self.subTest(role=account.summary.role, account=account.summary.login_id):
                result = self.service.edit_profile(EditProfile(account.summary.account_id, 1, "Changed", "Last", ""))
                self.assertEqual(isinstance(result, Success), allowed)

    def test_password_change_cannot_be_used_against_another_admin(self):
        result = self.service.change_password(ChangePassword(self.other_admin.summary.account_id, 1, "replacement"))
        self.assertIsInstance(result, Failure)
        self.assertEqual(result.error.code, ErrorCode.ACCESS_DENIED)
        self.assertEqual(self.get(self.other_admin).password_hash, self.other_admin.password_hash)
        self.assertEqual(self.history(self.other_admin.summary.account_id)[0].outcome, "denied")

    def test_own_password_requires_proof_and_invalidates_old_session_claims(self):
        account_id = self.admin.summary.account_id
        bad = self.service.change_password(ChangePassword(account_id, 1, "replacement", "wrong"))
        self.assertEqual(bad.error.code, ErrorCode.INVALID_PROOF)
        self.assertEqual(self.get(self.admin), self.admin)
        good = self.service.change_password(ChangePassword(account_id, 1, "replacement", "initial-secret"))
        self.assertIsInstance(good, Success)
        self.assertIsNone(self.get(self.admin).operator_ciphertext)
        self.assertEqual(self.service.list_users().error.code, ErrorCode.AUTHENTICATION_REQUIRED)

    def test_admin_can_change_and_reveal_operator_password_and_reveal_does_not_edit_metadata(self):
        identity = self.operator.summary.account_id
        changed = self.service.change_password(ChangePassword(identity, 1, "replacement"))
        reveal = self.service.reveal_operator_password(RevealPassword(identity))
        self.assertEqual(reveal.value.password, "replacement")
        self.assertEqual(self.get(self.operator).summary, changed.value)
        self.assertEqual([e.action_id for e in self.history(identity)],
                         ["users.reveal_password", "users.change_password"])
        self.assertNotIn("replacement", repr(self.history(identity)))
        self.assertNotIn("replacement", repr(reveal))

    def test_reveal_never_exposes_an_admin_secret_even_for_manufacturer(self):
        self.login(self.manufacturer)
        result = self.service.reveal_operator_password(RevealPassword(self.admin.summary.account_id))
        self.assertEqual(result.error.code, ErrorCode.POLICY_VIOLATION)

    def test_operator_direct_service_calls_are_denied(self):
        self.login(self.operator)
        self.assertIsInstance(self.service.list_users(), Failure)
        self.assertIsInstance(self.service.change_password(ChangePassword(
            self.operator.summary.account_id, 1, "replacement", "initial-secret")), Failure)

    def test_stale_revision_does_not_overwrite_newer_profile_or_credential(self):
        identity = self.operator.summary.account_id
        self.service.edit_profile(EditProfile(identity, 1, "Changed", "Last", ""))
        result = self.service.change_password(ChangePassword(identity, 1, "replacement"))
        self.assertEqual(result.error.code, ErrorCode.CONFLICT)
        self.assertEqual(self.get(self.operator).password_hash, self.operator.password_hash)

    def test_audit_failure_rolls_back_profile_and_credentials(self):
        identity = self.operator.summary.account_id
        with patch.object(SQLiteAccountTransaction, "append_event", side_effect=AuditPersistenceError):
            with self.assertRaises(AuditPersistenceError):
                self.service.change_password(ChangePassword(identity, 1, "replacement"))
        self.assertEqual(self.get(self.operator), self.operator)
        self.assertEqual(self.history(identity), ())

    def test_reveal_returns_no_secret_when_audit_cannot_be_persisted(self):
        with patch.object(SQLiteAccountTransaction, "append_event", side_effect=AuditPersistenceError):
            with self.assertRaises(AuditPersistenceError):
                self.service.reveal_operator_password(RevealPassword(self.operator.summary.account_id))

    def test_admin_cannot_change_roles_or_delete_other_admins(self):
        self.assertIsInstance(self.service.change_role(ChangeRole(
            self.operator.summary.account_id, 1, "Admin")), Failure)
        self.assertIsInstance(self.service.delete_user(DeleteAccount(self.other_admin.summary.account_id, 1)), Failure)

    def test_delete_and_recreate_preserves_history_under_old_identity(self):
        identity = self.operator.summary.account_id
        self.assertIsInstance(self.service.delete_user(DeleteAccount(identity, 1)), Success)
        created = self.service.create_user(CreateAccount("3", "New", "Person", "Operator", "replacement"))
        self.assertNotEqual(created.value.account_id, identity)
        self.assertEqual(self.history(identity)[0].action_id, "users.delete")

    def test_manufacturer_cannot_delete_or_demote_last_admin(self):
        self.login(self.manufacturer)
        self.service.delete_user(DeleteAccount(self.other_admin.summary.account_id, 1))
        self.assertEqual(self.service.delete_user(DeleteAccount(self.admin.summary.account_id, 1)).error.code,
                         ErrorCode.POLICY_VIOLATION)
        self.assertEqual(self.service.change_role(ChangeRole(self.admin.summary.account_id, 1,
                                                             "Operator", "new-secret")).error.code,
                         ErrorCode.POLICY_VIOLATION)

    def test_current_stored_role_is_used_instead_of_role_at_login(self):
        with self.store.transaction() as transaction:
            transaction.replace(replace(self.admin, summary=replace(self.admin.summary, role="Operator")))
        self.assertEqual(self.service.list_users().error.code, ErrorCode.ACCESS_DENIED)
        context = AccountAccessContext(self.store, self.session).capture()
        self.assertEqual(context.actor.role, "Operator")

    def test_context_provider_rejects_deleted_recreated_identity(self):
        with self.store.transaction() as transaction:
            transaction.delete(self.admin.summary.account_id)
        self.seed("1", "Admin")
        context = AccountAccessContext(self.store, self.session).capture(ResourceRef("account", self.operator.summary.account_id))
        self.assertIsNone(context.actor)
        self.assertIsNone(context.target)

    def test_missing_or_corrupt_database_never_becomes_an_empty_store(self):
        missing = Path(self.directory.name) / "missing.sqlite3"
        with self.assertRaises(StorageIntegrityError):
            SQLiteAccountStore(missing)
        self.assertFalse(missing.exists())
        missing.write_text("corrupt")
        with self.assertRaises(StorageIntegrityError):
            SQLiteAccountStore(missing)

    def test_audit_history_is_append_only_and_survives_account_deletion(self):
        self.service.delete_user(DeleteAccount(self.operator.summary.account_id, 1))
        with sqlite3.connect(self.path) as connection:
            with self.assertRaises(sqlite3.IntegrityError):
                connection.execute("DELETE FROM audit_events")
        self.assertEqual(len(self.history(self.operator.summary.account_id)), 1)

    def permission_service(self):
        return PermissionService(self.store, self.session, self.policy,
                                 app_ids=frozenset({"dashboard", "settings"}),
                                 denied_roles={"settings": {"Operator"}})

    def test_permission_service_denies_admin_reads_and_writes(self):
        service = self.permission_service()
        self.assertEqual(service.read_permissions().error.code, ErrorCode.ACCESS_DENIED)
        self.assertEqual(service.update_permissions(UpdateAppPermissions(
            "dashboard", ("Operator",), 1)).error.code, ErrorCode.ACCESS_DENIED)

    def test_manufacturer_permission_updates_are_audited_and_revision_checked(self):
        self.login(self.manufacturer)
        service = self.permission_service()
        before = service.read_permissions().value
        result = service.update_permissions(UpdateAppPermissions("dashboard", ("Operator",), before.revision))
        self.assertIsInstance(result, Success)
        self.assertEqual(result.value.revision, before.revision + 1)
        roles = next(grant.roles for grant in result.value.grants if grant.app_id == "dashboard")
        self.assertEqual(set(roles), {"Operator", "Manufacturer"})
        self.assertEqual(self.history("dashboard")[0].actor_id, self.manufacturer.summary.account_id)
        stale = service.update_permissions(UpdateAppPermissions("dashboard", ("Admin",), before.revision))
        self.assertEqual(stale.error.code, ErrorCode.CONFLICT)

    def test_permission_update_cannot_grant_operator_access_to_restricted_app(self):
        self.login(self.manufacturer)
        result = self.permission_service().update_permissions(UpdateAppPermissions("settings", ("Operator",), 1))
        self.assertEqual(result.error.code, ErrorCode.POLICY_VIOLATION)

    def test_permission_update_rolls_back_when_audit_fails(self):
        self.login(self.manufacturer)
        service = self.permission_service()
        before = service.read_permissions().value
        with patch.object(SQLiteAccountTransaction, "append_event", side_effect=AuditPersistenceError):
            with self.assertRaises(AuditPersistenceError):
                service.update_permissions(UpdateAppPermissions("dashboard", ("Operator",), before.revision))
        self.assertEqual(service.read_permissions().value, before)

    def test_concurrent_commands_cannot_both_replace_the_same_revision(self):
        from concurrent.futures import ThreadPoolExecutor
        identity = self.operator.summary.account_id
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = [pool.submit(self.service.edit_profile, EditProfile(identity, 1, name, "Last", ""))
                       for name in ("One", "Two")]
            results = [future.result() for future in futures]
        self.assertEqual(sum(isinstance(result, Success) for result in results), 1)
        self.assertEqual([r.error.code for r in results if isinstance(r, Failure)], [ErrorCode.CONFLICT])
        self.assertEqual(len(self.history(identity)), 1)

    def test_session_change_during_execution_rolls_back_the_entire_command(self):
        original_hash = self.credentials.hash_password
        def hash_then_logout(password):
            result = original_hash(password)
            self.session.logout()
            return result
        with patch.object(self.credentials, "hash_password", side_effect=hash_then_logout):
            result = self.service.change_password(ChangePassword(self.operator.summary.account_id, 1, "replacement"))
        self.assertEqual(result.error.code, ErrorCode.CONFLICT)
        self.assertEqual(self.get(self.operator), self.operator)

    def test_missing_credentials_is_storage_corruption_not_an_empty_account_list(self):
        with sqlite3.connect(self.path) as connection:
            connection.execute("DELETE FROM credentials WHERE account_id=?", (self.operator.summary.account_id,))
        with self.assertRaises(StorageIntegrityError):
            self.service.list_users()

    def test_history_service_is_protected_and_preserves_access_to_deleted_identity(self):
        identity = self.operator.summary.account_id
        self.service.delete_user(DeleteAccount(identity, 1))
        history = AuditHistoryService(self.store, self.session, self.policy)
        self.assertEqual(history.list_events(HistoryQuery(identity)).error.code, ErrorCode.ACCESS_DENIED)
        self.login(self.manufacturer)
        events = history.list_events(HistoryQuery(identity)).value
        self.assertTrue(any(event.action_id == "users.delete" for event in events))
        self.assertTrue(all(event.target_id == identity for event in events))
        self.assertEqual(history.list_events(HistoryQuery(identity, limit=0)).error.code, ErrorCode.INVALID_INPUT)

    def test_history_ui_advice_and_service_enforce_same_role_and_target_scope(self):
        from src.engine.auth.access_service import AccessService
        from src.shared_contracts.authorization.access import AccessKind, AccessRequest
        from src.shared_contracts.authorization.actions import AuditAction

        history = AuditHistoryService(self.store, self.session, self.policy)
        access = AccessService(AccountAccessContext(self.store, self.session), self.policy)
        self.service.edit_profile(EditProfile(self.admin.summary.account_id, 1, "Edited", "Admin", ""))
        self.service.edit_profile(EditProfile(self.operator.summary.account_id, 1, "Edited", "Operator", ""))
        for actor, permitted in ((self.admin, {self.admin.summary.account_id, self.operator.summary.account_id}),
                                 (self.manufacturer, {account.summary.account_id for account in
                                    (self.admin, self.other_admin, self.operator, self.manufacturer)}),
                                 (self.operator, set())):
            self.login(actor)
            for target in (self.admin, self.other_admin, self.operator, self.manufacturer):
                identity = target.summary.account_id
                with self.subTest(actor=actor.summary.role, target=target.summary.role, identity=identity):
                    request = AccessRequest(AccessKind.ACTION, AuditAction.VIEW,
                                            ResourceRef("account_history", identity))
                    decision = access.evaluate((request,)).value.decisions[0]
                    result = history.list_events(HistoryQuery(identity))
                    self.assertEqual(decision.allowed, identity in permitted)
                    self.assertEqual(isinstance(result, Success), identity in permitted)
                    if isinstance(result, Failure):
                        self.assertEqual(result.error.code, ErrorCode.ACCESS_DENIED)
        self.session.logout()
        self.assertEqual(history.list_events(HistoryQuery(self.admin.summary.account_id)).error.code,
                         ErrorCode.AUTHENTICATION_REQUIRED)

    def test_history_rechecks_target_role_after_ui_authorization(self):
        from src.engine.auth.access_service import AccessService
        from src.shared_contracts.authorization.access import AccessKind, AccessRequest
        from src.shared_contracts.authorization.actions import AuditAction

        identity = self.operator.summary.account_id
        history = AuditHistoryService(self.store, self.session, self.policy)
        request = AccessRequest(AccessKind.ACTION, AuditAction.VIEW, ResourceRef("account_history", identity))
        access = AccessService(AccountAccessContext(self.store, self.session), self.policy)
        self.assertTrue(access.evaluate((request,)).value.decisions[0].allowed)
        self.login(self.manufacturer)
        self.assertIsInstance(self.service.change_role(ChangeRole(identity, 1, "Admin", "new-privileged-secret")), Success)
        self.login(self.admin)
        self.assertFalse(access.evaluate((request,)).value.decisions[0].allowed)
        self.assertEqual(history.list_events(HistoryQuery(identity)).error.code, ErrorCode.ACCESS_DENIED)

    def test_history_does_not_return_events_if_session_changes_during_read(self):
        history = AuditHistoryService(self.store, self.session, self.policy)
        original = SQLiteAccountTransaction.history

        def read_then_logout(transaction, query):
            events = original(transaction, query)
            self.session.logout()
            return events

        with patch.object(SQLiteAccountTransaction, "history", read_then_logout):
            result = history.list_events(HistoryQuery(self.operator.summary.account_id))
        self.assertEqual(result.error.code, ErrorCode.CONFLICT)

    def test_login_returns_safe_identity_without_changing_edit_metadata(self):
        login = AccountLoginService(self.store, self.credentials)
        result = login.login(LoginCredentials("1", "initial-secret"))
        self.assertIsInstance(result, Success)
        self.assertEqual(result.value.account, self.admin.summary)
        self.assertEqual(result.value.credential_version, 1)
        self.assertNotIn("initial-secret", repr(result))
        self.assertEqual(self.get(self.admin), self.admin)
        self.assertEqual(self.history(self.admin.summary.account_id)[0].action_id, "users.login")

    def test_login_uses_generic_failure_for_missing_disabled_retired_or_wrong_credentials(self):
        login = AccountLoginService(self.store, self.credentials)
        attempts = [LoginCredentials("missing", "initial-secret"), LoginCredentials("1", "wrong")]
        with self.store.transaction() as transaction:
            transaction.replace(replace(self.operator, summary=replace(self.operator.summary, enabled=False)))
            transaction.replace(replace(self.other_admin, summary=replace(self.other_admin.summary, role="Developer")))
        attempts += [LoginCredentials("3", "initial-secret"), LoginCredentials("2", "initial-secret")]
        for attempt in attempts:
            result = login.login(attempt)
            self.assertEqual(result.error.code, ErrorCode.INVALID_PROOF)
            self.assertEqual(result.error.message_key, "account.invalid_proof")

    def test_login_cannot_succeed_without_durable_audit(self):
        login = AccountLoginService(self.store, self.credentials)
        with patch.object(SQLiteAccountTransaction, "append_event", side_effect=AuditPersistenceError):
            with self.assertRaises(AuditPersistenceError):
                login.login(LoginCredentials("1", "initial-secret"))

    def test_promoted_operator_cannot_reuse_previously_revealed_operator_password(self):
        self.login(self.manufacturer)
        identity = self.operator.summary.account_id
        denied = self.service.change_role(ChangeRole(identity, 1, "Admin"))
        self.assertEqual(denied.error.code, ErrorCode.INVALID_INPUT)
        promoted = self.service.change_role(ChangeRole(identity, 1, "Admin", "fresh-admin-secret"))
        self.assertIsInstance(promoted, Success)
        stored = self.get(self.operator)
        self.assertIsNone(stored.operator_ciphertext)
        self.assertFalse(self.credentials.verify_password("initial-secret", stored.password_hash))
        self.assertTrue(self.credentials.verify_password("fresh-admin-secret", stored.password_hash))

    def test_crossing_operator_boundary_rejects_explicit_reuse_of_the_old_password(self):
        self.login(self.manufacturer)
        for account, role in ((self.operator, "Admin"), (self.other_admin, "Operator")):
            with self.subTest(role=role):
                result = self.service.change_role(ChangeRole(account.summary.account_id, 1, role, "initial-secret"))
                self.assertEqual(result.error.code, ErrorCode.INVALID_INPUT)
                self.assertEqual(self.get(account), account)
                self.assertEqual(self.history(account.summary.account_id), ())


if __name__ == "__main__":
    unittest.main()
