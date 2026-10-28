"""Access contract tests; no Qt, hardware, or real account storage."""
import unittest
from dataclasses import dataclass
from enum import Enum

from src.engine.auth.access_policy import AccessPolicy, AccessRule, GrantScope, RoleGrant
from src.engine.auth.access_service import AccessService
from src.engine.auth.i_access_context_provider import IAccessContextProvider
from src.engine.auth.i_access_condition import IAccessCondition
from src.engine.auth.user_access_rules import user_access_rules
from src.shared_contracts.authorization.access import (
    AccessContext, AccessKind, AccessRequest, Actor, DenialReason, ResourceFacts, ResourceRef,
)
from src.shared_contracts.authorization.actions import PermissionAction, UserAction
from src.shared_contracts.authorization.errors import (
    AuditPersistenceError, ErrorCode, ServiceUnavailableError, StorageIntegrityError,
)
from src.shared_contracts.authorization.features import UserFeature
from src.shared_contracts.authorization.results import Failure, Success

ACCOUNT = ResourceRef("account", "admin-1")
OPERATOR = ResourceRef("account", "operator-1")
OTHER_ADMIN = ResourceRef("account", "admin-2")


class Contexts(IAccessContextProvider):
    def __init__(self, role="Admin", account_id="admin-1"):
        self.actor = Actor(account_id, role) if role else None
        self.revision = 1
        self.targets = {
            ACCOUNT: ResourceFacts(ACCOUNT, "admin-1", "Admin"),
            OPERATOR: ResourceFacts(OPERATOR, "operator-1", "Operator"),
            OTHER_ADMIN: ResourceFacts(OTHER_ADMIN, "admin-2", "Admin"),
        }

    def capture(self, target=None):
        return AccessContext(self.actor, self.revision, self.targets.get(target))


def policy(extra_rules=()):
    return AccessPolicy(
        roles=frozenset({"Admin", "Operator", "Manufacturer"}),
        manufacturer_role="Manufacturer",
        rules=user_access_rules(admin_role="Admin", operator_role="Operator") + tuple(extra_rules),
    )


class AccessServiceContractTests(unittest.TestCase):
    def evaluate(self, contexts, action=UserAction.CHANGE_PASSWORD, target=None, rules=()):
        service = AccessService(contexts, policy(rules))
        result = service.evaluate((AccessRequest(AccessKind.ACTION, action, target),))
        self.assertIsInstance(result, Success)
        return result.value.decisions[0]

    def test_admin_password_scope_distinguishes_self_operator_and_other_admin(self):
        contexts = Contexts()
        self.assertTrue(self.evaluate(contexts, target=ACCOUNT).allowed)
        self.assertTrue(self.evaluate(contexts, target=OPERATOR).allowed)
        denied = self.evaluate(contexts, target=OTHER_ADMIN)
        self.assertFalse(denied.allowed)
        self.assertTrue(denied.role_eligible)
        self.assertEqual(denied.reason, DenialReason.TARGET_DENIED)

    def test_reveal_requires_operator_target(self):
        contexts = Contexts()
        self.assertTrue(self.evaluate(contexts, UserAction.REVEAL_PASSWORD, OPERATOR).allowed)
        self.assertFalse(self.evaluate(contexts, UserAction.REVEAL_PASSWORD, ACCOUNT).allowed)

    def test_operator_cannot_change_own_password_or_manage_permissions(self):
        contexts = Contexts("Operator", "operator-1")
        self.assertFalse(self.evaluate(contexts, target=OPERATOR).role_eligible)
        self.assertFalse(self.evaluate(contexts, PermissionAction.MANAGE).allowed)

    def test_admin_permission_tab_and_action_are_both_denied(self):
        service = AccessService(Contexts(), policy())
        result = service.evaluate((
            AccessRequest(AccessKind.FEATURE, UserFeature.APP_PERMISSIONS),
            AccessRequest(AccessKind.ACTION, PermissionAction.MANAGE),
        ))
        self.assertIsInstance(result, Success)
        self.assertTrue(all(not d.allowed for d in result.value.decisions))

    def test_manufacturer_grant_applies_to_new_domain_actions_without_engine_edits(self):
        class PaintAction(str, Enum):
            EDIT = "paint.recipes.edit"
        new_rule = AccessRule(AccessKind.ACTION, PaintAction.EDIT)
        self.assertTrue(self.evaluate(Contexts("Manufacturer"), PaintAction.EDIT, rules=(new_rule,)).allowed)
        self.assertFalse(self.evaluate(Contexts(), PaintAction.EDIT, rules=(new_rule,)).allowed)

    def test_hard_role_denial_wins_over_app_grant(self):
        rule = AccessRule(AccessKind.APPLICATION, "service-settings", (
            RoleGrant("Admin"), RoleGrant("Operator"),
        ), denied_roles=frozenset({"Operator"}))
        request = AccessRequest(AccessKind.APPLICATION, "service-settings")
        for role, allowed in (("Operator", False), ("Admin", True), ("Manufacturer", True)):
            with self.subTest(role=role):
                result = AccessService(Contexts(role), policy((rule,))).evaluate((request,))
                self.assertEqual(result.value.decisions[0].allowed, allowed)

    def test_domain_condition_extends_typed_facts_without_granting_unlisted_roles(self):
        @dataclass(frozen=True)
        class RecipeFacts(ResourceFacts):
            editable: bool = False

        class EditableRecipe(IAccessCondition):
            def matches(self, actor, target):
                return isinstance(target, RecipeFacts) and target.editable

        reference = ResourceRef("recipe", "recipe-1")
        rule = AccessRule(AccessKind.ACTION, "paint.edit", (RoleGrant("Admin"),),
                          target_kind="recipe", condition=EditableRecipe())
        for role, editable, allowed in (("Admin", False, False), ("Admin", True, True),
                                        ("Operator", True, False), ("Manufacturer", False, True)):
            with self.subTest(role=role, editable=editable):
                contexts = Contexts(role)
                contexts.targets[reference] = RecipeFacts(reference, editable=editable)
                self.assertEqual(self.evaluate(contexts, "paint.edit", reference, (rule,)).allowed, allowed)

    def test_unknown_actions_and_roles_and_unauthenticated_deny(self):
        for role, reason in ((None, DenialReason.AUTHENTICATION_REQUIRED),
                             ("Unknown", DenialReason.UNKNOWN_ROLE),
                             ("Manufacturer", DenialReason.UNKNOWN_REQUIREMENT)):
            with self.subTest(role=role):
                decision = self.evaluate(Contexts(role), "unregistered.action")
                self.assertFalse(decision.allowed)
                self.assertEqual(decision.reason, reason)

    def test_missing_selection_preserves_role_eligibility_but_never_allows(self):
        decision = self.evaluate(Contexts())
        self.assertFalse(decision.allowed)
        self.assertTrue(decision.role_eligible)
        self.assertEqual(decision.reason, DenialReason.TARGET_REQUIRED)

    def test_missing_or_spoofed_target_never_allows_even_for_manufacturer(self):
        contexts = Contexts("Manufacturer")
        missing = ResourceRef("account", "missing")
        self.assertEqual(self.evaluate(contexts, target=missing).reason, DenialReason.TARGET_NOT_FOUND)
        contexts.targets[OPERATOR] = contexts.targets[ACCOUNT]
        self.assertEqual(self.evaluate(contexts, target=OPERATOR).reason, DenialReason.TARGET_DENIED)
        wrong_kind = ResourceRef("recipe", "operator-1")
        contexts.targets[wrong_kind] = ResourceFacts(wrong_kind, "operator-1", "Operator")
        self.assertFalse(self.evaluate(contexts, target=wrong_kind).allowed)

    def test_session_change_during_batch_returns_conflict_without_partial_decisions(self):
        class ChangingContext(Contexts):
            def capture(self, target=None):
                if target:
                    self.revision += 1
                return super().capture(target)
        result = AccessService(ChangingContext(), policy()).evaluate((
            AccessRequest(AccessKind.ACTION, UserAction.CHANGE_PASSWORD, ACCOUNT),
        ))
        self.assertIsInstance(result, Failure)
        self.assertEqual(result.error.code, ErrorCode.CONFLICT)

    def test_same_user_relogin_is_also_a_session_change(self):
        class ReloginContext(Contexts):
            calls = 0
            def capture(self, target=None):
                self.calls += 1
                if self.calls == 2:
                    self.revision += 1
                return super().capture(target)
        result = AccessService(ReloginContext(), policy()).evaluate(())
        self.assertIsInstance(result, Failure)
        self.assertEqual(result.error.code, ErrorCode.CONFLICT)

    def test_invalid_request_has_typed_business_error(self):
        service = AccessService(Contexts(), policy())
        for requests in ([], ("not a request",), (AccessRequest("action", "key"),),
                         (AccessRequest(AccessKind.ACTION, ""),)):
            with self.subTest(requests=requests):
                result = service.evaluate(requests)
                self.assertIsInstance(result, Failure)
                self.assertEqual(result.error.code, ErrorCode.INVALID_INPUT)
                self.assertTrue(result.error.correlation_id)

    def test_declared_infrastructure_error_propagates_as_structured_exception(self):
        class BrokenContext(Contexts):
            def capture(self, target=None):
                raise StorageIntegrityError(correlation_id="test-correlation")
        with self.assertRaises(StorageIntegrityError) as raised:
            AccessService(BrokenContext(), policy()).evaluate(())
        self.assertEqual(raised.exception.error.code, ErrorCode.STORAGE_INTEGRITY)
        self.assertEqual(raised.exception.error.correlation_id, "test-correlation")

    def test_duplicate_and_misconfigured_rules_fail_during_composition(self):
        duplicate = AccessRule(AccessKind.ACTION, PermissionAction.MANAGE)
        with self.assertRaises(ValueError):
            policy((duplicate,))
        with self.assertRaises(ValueError):
            AccessRule(AccessKind.ACTION, "bad", (RoleGrant("Admin", GrantScope.SELF),))
        with self.assertRaises(ValueError):
            policy((AccessRule(AccessKind.ACTION, "bad", (RoleGrant("Unknown"),)),))

    def test_service_exceptions_have_distinct_codes_and_safe_messages(self):
        for exception, code in ((ServiceUnavailableError, ErrorCode.SERVICE_UNAVAILABLE),
                                (StorageIntegrityError, ErrorCode.STORAGE_INTEGRITY),
                                (AuditPersistenceError, ErrorCode.AUDIT_PERSISTENCE)):
            error = exception()
            self.assertEqual(error.error.code, code)
            self.assertEqual(str(error), error.error.message_key)
            self.assertTrue(error.error.correlation_id)


if __name__ == "__main__":
    unittest.main()
