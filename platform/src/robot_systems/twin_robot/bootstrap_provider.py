from __future__ import annotations

from src.bootstrap.account_application_wiring import build_account_login_view
from src.bootstrap.account_runtime import get_account_navigation
from src.engine.robot.drivers.ros2_robot import Ros2Robot
from src.robot_systems.twin_robot.twin_robot_system import TwinRobotSystem
from src.robot_systems.robot_system_bootstrap_provider import RobotSystemBootstrapProvider


class TwinBootstrapProvider(RobotSystemBootstrapProvider):
    @property
    def system_class(self):
        return TwinRobotSystem

    def build_robot(self):
        # Twin execution remains owned by its explicitly injected twin runtime.
        # The shared shell requires an IRobotService; this placeholder performs no I/O.
        return Ros2Robot(server_url="fake://local")

    def build_login_view(self, robot_system, messaging_service):
        return build_account_login_view(robot_system, messaging_service)

    def build_authorization_service(self, robot_system):
        return get_account_navigation(robot_system)


def create_bootstrap_provider() -> RobotSystemBootstrapProvider:
    return TwinBootstrapProvider()
