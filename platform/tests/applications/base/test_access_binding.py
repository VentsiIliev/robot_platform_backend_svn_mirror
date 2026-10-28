"""Permission bindings preserve existing visual properties and operational state."""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import unittest

from PyQt6.QtGui import QAction
from PyQt6 import sip
from PyQt6.QtWidgets import QApplication, QPushButton, QTabWidget, QWidget

from src.applications.base.access.access_binding import AccessBinding
from src.applications.base.access.adapters import TabAdapter, WidgetAdapter
from src.applications.base.access.contracts import (
    AccessRequirement, AccessVersion, ControlState, PresentationAccess,
)


class AccessBindingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.binding = AccessBinding()
        self.version = AccessVersion(1, 1)
        self.widgets = []

    def tearDown(self):
        self.binding.close()
        for widget in self.widgets:
            widget.close()
            sip.delete(widget)
        self.widgets.clear()

    def button(self, requirement=AccessRequirement(action="users.change_password")):
        parent = QWidget()
        button = QPushButton("Existing text", parent)
        self.widgets.append(parent)
        self.binding.register("button", WidgetAdapter(button), requirement)
        self.binding.invalidate(self.version)
        return button

    def test_protected_starts_hidden_and_role_denial_stays_hidden(self):
        button = self.button()
        self.assertTrue(button.isHidden())
        self.binding.apply_access(self.version, {"button": PresentationAccess(role_eligible=False)})
        self.assertTrue(button.isHidden())
        self.assertFalse(button.isEnabled())

    def test_target_denial_disables_but_retains_role_visible_control(self):
        button = self.button()
        self.binding.apply_access(self.version, {"button": PresentationAccess(action_allowed=False)})
        self.assertFalse(button.isHidden())
        self.assertFalse(button.isEnabled())

    def test_visible_but_denied_and_hidden_but_allowed_are_independent(self):
        button = self.button(AccessRequirement(action="x", hide_when_role_denied=False))
        self.binding.apply_access(self.version, {"button": PresentationAccess(role_eligible=False)})
        self.assertFalse(button.isHidden())
        self.assertFalse(button.isEnabled())
        self.binding.set_operational_state("button", ControlState(visible=False))
        self.binding.apply_access(self.version, {"button": PresentationAccess()})
        self.assertTrue(button.isHidden())

    def test_permission_regrant_never_overrides_busy_or_selection_state(self):
        button = self.button()
        self.binding.set_operational_state("button", ControlState(enabled=False))
        self.binding.apply_access(self.version, {"button": PresentationAccess()})
        self.assertFalse(button.isEnabled())
        self.binding.apply_access(self.version, {"button": PresentationAccess(role_eligible=False)})
        self.binding.apply_access(self.version, {"button": PresentationAccess()})
        self.assertFalse(button.isEnabled())
        self.binding.set_operational_state("button", ControlState())
        self.assertTrue(button.isEnabled())

    def test_existing_style_geometry_font_and_text_are_untouched(self):
        button = QPushButton("Existing text")
        self.widgets.append(button)
        button.setStyleSheet("padding: 13px; border-radius: 9px;")
        button.setMinimumSize(123, 49)
        font = button.font()
        font.setPointSize(14)
        button.setFont(font)
        before = (button.styleSheet(), button.minimumSize(), button.font(), button.text())
        self.binding.register("button", WidgetAdapter(button), AccessRequirement(action="x"))
        self.binding.invalidate(self.version)
        self.binding.apply_access(self.version, {"button": PresentationAccess()})
        self.binding.apply_access(self.version, {"button": PresentationAccess(action_allowed=False)})
        self.assertEqual(before, (button.styleSheet(), button.minimumSize(), button.font(), button.text()))

    def test_old_session_policy_or_selection_results_cannot_reenable(self):
        button = self.button()
        next_version = AccessVersion(2, 3, 4)
        self.binding.invalidate(next_version)
        self.assertFalse(self.binding.apply_access(self.version, {"button": PresentationAccess()}))
        self.assertTrue(button.isHidden())
        self.assertTrue(self.binding.apply_access(next_version, {"button": PresentationAccess()}))
        self.assertTrue(button.isEnabled())

    def test_omitted_decision_revokes_previous_permission(self):
        button = self.button()
        self.binding.apply_access(self.version, {"button": PresentationAccess()})
        self.binding.apply_access(self.version, {})
        self.assertTrue(button.isHidden())

    def test_ordinary_button_and_qaction_work_without_authorizer(self):
        button = self.button(AccessRequirement())
        action = QAction("Existing action")
        self.binding.register("action", WidgetAdapter(action))
        self.assertFalse(button.isHidden())
        self.assertTrue(action.isEnabled())
        self.binding.invalidate(AccessVersion(2, 2))
        self.assertFalse(button.isHidden())
        self.assertTrue(action.isEnabled())

    def test_tab_visibility_uses_page_identity_and_rejects_programmatic_activation(self):
        tabs = QTabWidget()
        self.widgets.append(tabs)
        users, permissions = QWidget(), QWidget()
        tabs.addTab(users, "Users")
        tabs.addTab(permissions, "App Permissions")
        self.binding.register("tab", TabAdapter(tabs, permissions),
                              AccessRequirement(feature="users.app_permissions"))
        self.binding.invalidate(self.version)
        self.assertFalse(tabs.isTabVisible(tabs.indexOf(permissions)))
        self.binding.apply_access(self.version, {"tab": PresentationAccess()})
        tabs.tabBar().moveTab(1, 0)
        tabs.setCurrentWidget(permissions)
        self.assertIs(tabs.currentWidget(), permissions)
        self.binding.apply_access(self.version, {"tab": PresentationAccess(feature_visible=False)})
        self.assertIs(tabs.currentWidget(), users)
        tabs.setCurrentWidget(permissions)
        self.assertIs(tabs.currentWidget(), users)
        self.assertEqual(tabs.tabText(tabs.indexOf(permissions)), "App Permissions")

    def test_close_rejects_pending_results_and_is_idempotent(self):
        button = self.button()
        self.binding.close()
        self.binding.close()
        self.assertFalse(self.binding.apply_access(self.version, {"button": PresentationAccess()}))
        self.assertTrue(button.isHidden())

    def test_atomic_policy_refresh_preserves_current_allowed_tab(self):
        tabs = QTabWidget()
        self.widgets.append(tabs)
        users, permissions = QWidget(), QWidget()
        tabs.addTab(users, "Users")
        tabs.addTab(permissions, "App Permissions")
        self.binding.register("tab", TabAdapter(tabs, permissions), AccessRequirement(feature="permissions"))
        self.binding.invalidate(self.version)
        self.binding.apply_access(self.version, {"tab": PresentationAccess()})
        tabs.setCurrentWidget(permissions)
        newer = AccessVersion(self.version.session_revision, self.version.policy_revision + 1)
        self.assertTrue(self.binding.replace_access(self.version, newer, {"tab": PresentationAccess()}))
        self.assertIs(tabs.currentWidget(), permissions)
        self.assertFalse(self.binding.replace_access(self.version, newer, {"tab": PresentationAccess()}))

    def test_atomic_refresh_cannot_cross_session_selection_or_reverse_policy(self):
        button = self.button()
        for version in (AccessVersion(2, 1), AccessVersion(1, 1, 1), AccessVersion(1, 0)):
            self.assertFalse(self.binding.replace_access(self.version, version, {"button": PresentationAccess()}))
        self.assertTrue(button.isHidden())

    def test_explicit_target_hiding_and_combined_feature_gate(self):
        button = self.button(AccessRequirement(action="x", feature="section",
                                               hide_when_target_denied=True))
        self.binding.apply_access(self.version, {"button": PresentationAccess(action_allowed=False)})
        self.assertTrue(button.isHidden())
        self.binding.apply_access(self.version, {"button": PresentationAccess(feature_visible=False)})
        self.assertTrue(button.isHidden())
        self.binding.apply_access(self.version, {"button": PresentationAccess()})
        self.assertFalse(button.isHidden())

    def test_existing_initial_disabled_state_survives_first_permission_result(self):
        button = QPushButton("Existing")
        self.widgets.append(button)
        button.setEnabled(False)
        self.binding.register("button", WidgetAdapter(button), AccessRequirement(action="x"),
                              operational=ControlState(visible=True, enabled=button.isEnabled()))
        self.binding.invalidate(self.version)
        self.binding.apply_access(self.version, {"button": PresentationAccess()})
        self.assertFalse(button.isEnabled())

    def test_invalid_requirement_cannot_be_mistaken_for_unprotected_control(self):
        with self.assertRaises(ValueError):
            AccessRequirement(action="")

    def test_disabled_parent_does_not_permanently_disable_an_allowed_child(self):
        parent = QWidget()
        self.widgets.append(parent)
        button = QPushButton("Existing", parent)
        parent.setEnabled(False)
        self.binding.register("button", WidgetAdapter(button), AccessRequirement(action="x"))
        self.binding.invalidate(self.version)
        self.binding.apply_access(self.version, {"button": PresentationAccess()})
        self.assertFalse(button.isEnabled())
        parent.setEnabled(True)
        self.assertTrue(button.isEnabled())


if __name__ == "__main__":
    unittest.main()
