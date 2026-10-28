from __future__ import annotations

from src.bootstrap.account_application_wiring import build_account_login_view
from src.bootstrap.account_runtime import get_account_navigation
from src.engine.robot.drivers.ros2_robot import Ros2Robot
from src.robot_systems.paint.paint_robot_system import PaintRobotSystem
from src.robot_systems.robot_system_bootstrap_provider import RobotSystemBootstrapProvider


class PaintBootstrapProvider(RobotSystemBootstrapProvider):
    def __init__(self, system_class=PaintRobotSystem):
        self._system_class = system_class

    @property
    def system_class(self):
        return self._system_class

    def build_robot(self):
        # TODO: Move concrete robot driver selection into persisted startup config.
        return Ros2Robot()
        # TODO: CHANGE THIS TO RUN ON REAL HARDWARE ON USE FAKE FOR TESTING
        # return Ros2Robot(server_url="fake://local")

    def build_login_view(self, robot_system, messaging_service):
        return build_account_login_view(robot_system, messaging_service)

    def build_authorization_service(self, robot_system):
        return get_account_navigation(robot_system)


def create_bootstrap_provider() -> RobotSystemBootstrapProvider:
    return PaintBootstrapProvider()
