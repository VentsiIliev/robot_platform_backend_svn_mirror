"""
Plugin integration tests for UserManagement application.

Verifies:
- ApplicationSpec is declared in GlueRobotSystem.shell.applications
- factory produces a WidgetApplication
- factory uses the shared account runtime
"""
import os
import tempfile
import unittest
from unittest.mock import MagicMock

from src.applications.base.widget_application import WidgetApplication
from src.robot_systems.glue.glue_robot_system import GlueRobotSystem


def _make_robot_system():
    class RobotStub:
        role_policy = GlueRobotSystem.role_policy
        shell = GlueRobotSystem.shell
    app = RobotStub()
    app._account_runtime = MagicMock()
    app.get_service = MagicMock()
    return app


def _spec():
    return next(
        (s for s in GlueRobotSystem.shell.applications if s.name == "UserManagement"),
        None,
    )


class TestUserManagementApplicationSpec(unittest.TestCase):

    def test_spec_declared(self):
        self.assertIsNotNone(_spec(), "UserManagement ApplicationSpec missing")

    def test_spec_folder_id(self):
        self.assertEqual(_spec().folder_id, 3)

    def test_spec_has_factory(self):
        self.assertIsNotNone(_spec().factory)

    def test_spec_icon_set(self):
        self.assertIsNotNone(_spec().icon)


class TestUserManagementApplicationFactory(unittest.TestCase):

    def test_factory_returns_widget_application(self):
        application = _spec().factory(_make_robot_system())
        self.assertIsInstance(application, WidgetApplication)

    def test_register_stores_messaging_service(self):
        application = _spec().factory(_make_robot_system())
        ms = MagicMock()
        application.register(ms)
        self.assertIs(application._messaging_service, ms)

    def test_factory_creates_service_without_robot_service(self):
        """UserManagement does not depend on robot or vision service."""
        robot_app = _make_robot_system()
        application = _spec().factory(robot_app)
        robot_app.get_service.assert_not_called()


if __name__ == "__main__":
    unittest.main()
