from __future__ import annotations

from src.bootstrap.account_application_wiring import build_account_login_view
from src.bootstrap.account_runtime import get_account_navigation
from src.engine.robot.drivers.ros2_robot import Ros2Robot
from src.robot_systems.welding.welding_robot_system import WeldingRobotSystem
from src.robot_systems.robot_system_bootstrap_provider import RobotSystemBootstrapProvider


class WeldingBootstrapProvider(RobotSystemBootstrapProvider):
    @property
    def system_class(self):
        return WeldingRobotSystem

    def build_robot(self):
        # TODO: Move concrete robot driver selection into persisted startup config.
        return Ros2Robot()

    def build_login_view(self, robot_system, messaging_service):
        return build_account_login_view(robot_system, messaging_service)

    def build_authorization_service(self, robot_system):
        return get_account_navigation(robot_system)


def create_bootstrap_provider() -> RobotSystemBootstrapProvider:
    return WeldingBootstrapProvider()
