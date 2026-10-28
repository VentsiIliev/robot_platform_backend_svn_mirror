from __future__ import annotations

from src.bootstrap.account_application_wiring import build_account_login_view
from src.bootstrap.account_runtime import get_account_navigation
from src.engine.robot.drivers.fairino.test_robot import TestRobotWrapper
from src.robot_systems.ROBOT_SYSTEM_BLUEPRINT.my_robot_system import MyRobotSystem
from src.robot_systems.robot_system_bootstrap_provider import RobotSystemBootstrapProvider


class MyRobotSystemBootstrapProvider(RobotSystemBootstrapProvider):
    @property
    def system_class(self):
        return MyRobotSystem

    def build_robot(self):
        return TestRobotWrapper()

    def build_login_view(self, robot_system, messaging_service):
        return build_account_login_view(robot_system, messaging_service)

    def build_authorization_service(self, robot_system):
        return get_account_navigation(robot_system)


def create_bootstrap_provider() -> RobotSystemBootstrapProvider:
    return MyRobotSystemBootstrapProvider()
