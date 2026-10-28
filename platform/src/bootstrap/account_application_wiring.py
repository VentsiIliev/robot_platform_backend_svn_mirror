"""Shared account application composition; robot systems inject their runtime."""
from src.bootstrap.account_runtime import get_account_runtime


def build_account_login_view(robot_system, messaging_service):
    from src.applications.login.login_application_service import LoginApplicationService
    from src.applications.login.login_factory import LoginFactory
    from src.applications.login.qr_scanner import OpenCvQrScanner
    from src.engine.common_service_ids import CommonServiceID

    runtime = get_account_runtime(robot_system)
    vision = robot_system.get_optional_service(CommonServiceID.VISION)
    scanner = OpenCvQrScanner(vision.capture_corrected_image) if vision is not None else None
    service = LoginApplicationService(
        login=runtime.login, tokens=runtime.login_tokens, commissioning=runtime.commissioning,
        recovery=runtime.recovery, robot_service=robot_system.get_optional_service(CommonServiceID.ROBOT),
        qr_scanner=scanner,
    )
    return LoginFactory.build(service, messaging=messaging_service)


def build_account_user_management_application(robot_system):
    from src.applications.base.widget_application import WidgetApplication
    from src.applications.base.robot_jog_service_builder import build_robot_system_jog_service
    from src.applications.user_management.user_management_factory import UserManagementFactory
    from src.applications.user_management.service.user_management_application_service import UserManagementApplicationService

    runtime = get_account_runtime(robot_system)
    service = UserManagementApplicationService(
        accounts=runtime.accounts, access=runtime.access, tokens=runtime.login_tokens,
        recovery=runtime.recovery, permissions=runtime.permissions, history=runtime.history,
        session=runtime.session,
    )
    jog = build_robot_system_jog_service(robot_system)

    def build(messaging_service):
        return UserManagementFactory().build(service, messaging=messaging_service, jog_service=jog)

    return WidgetApplication(widget_factory=build)
