from __future__ import annotations

import os
from contextlib import nullcontext
from uuid import uuid4

from src.robot_systems.base_robot_system import BaseRobotSystem
from src.robot_systems.twin_robot import application_wiring
from src.robot_systems.twin_robot.applications.choreography_setup.service.choreography_setup_service import (
    ChoreographySetupService,
)
from src.robot_systems.twin_robot.applications.dashboard.service.twin_dashboard_service import (
    TwinDashboardService,
)
from src.robot_systems.twin_robot.storage import ChoreographyRepository
from src.shared_contracts.declarations import (
    ApplicationSpec,
    FolderSpec,
    RolePolicy,
    ShellSetup,
    SystemMetadata,
)


class TwinRobotSystem(BaseRobotSystem):
    """Platform composition for synchronized two-robot choreography.

    Concrete twin applications live under this robot-system package. The ROS
    transport is injected through ``set_twin_runtime`` so the platform remains
    decoupled from the motion-stack implementation.
    """

    services = []
    settings_specs = []
    movement_groups = []
    work_areas = []

    role_policy = RolePolicy(
        role_values=["Manufacturer", "Admin", "Operator"],
        admin_role_value="Admin",
        default_permission_role_values=["Admin"],
        protected_app_role_values={
            "usermanagement": ["Admin"],
            "softwareupdate": ["Admin"],
            "platformsettings": ["Admin"],
        },
        denied_folder_role_values={"ADMIN": ["Operator"], "SERVICE": ["Operator"]},
    )

    shell = ShellSetup(
        folders=[
            FolderSpec(folder_id=1, name="PRODUCTION", display_name="Production"),
            FolderSpec(folder_id=2, name="SETUP", display_name="Setup"),
            FolderSpec(folder_id=3, name="ADMIN", display_name="Administration"),
        ],
        applications=[
            ApplicationSpec(name="UserManagement", folder_id=3, icon="fa5s.users-cog",
                            factory=application_wiring._build_user_management_application),
            ApplicationSpec(name="SoftwareUpdate", folder_id=3, icon="fa5s.download",
                            factory=application_wiring._build_software_update_application),
            ApplicationSpec(name="PlatformSettings", folder_id=3, icon="fa5s.desktop",
                            factory=application_wiring._build_platform_settings_application),
            ApplicationSpec(
                name="TwinDashboard",
                folder_id=1,
                icon="fa5s.play-circle",
                factory=application_wiring._build_dashboard_application,
            ),
            ApplicationSpec(
                name="ChoreographySetup",
                folder_id=2,
                icon="fa5s.project-diagram",
                factory=application_wiring._build_choreography_setup_application,
            ),
            ApplicationSpec(
                name="NetworkSettings",
                folder_id=2,
                icon="fa5s.wifi",
                factory=application_wiring._build_network_settings_application,
            ),
        ],
    )

    metadata = SystemMetadata(
        name="TwinRobotSystem",
        version="0.1.0",
        description="Synchronized twin-robot choreography system",
        author="Platform Team",
        settings_root=os.path.join("storage", "settings"),
    )

    def __init__(self) -> None:
        super().__init__()
        self._twin_runtime = None
        self._choreography_repository = None
        self._dashboard_service = None
        self._choreography_setup_service = None
        from .runtime.account_activity import TwinAccountActivity
        self._account_activity = TwinAccountActivity(self._get_twin_runtime)

    def _get_twin_runtime(self):
        return self._twin_runtime

    def set_twin_runtime(self, runtime) -> None:
        """Attach the transport/runtime adapter used by both twin applications."""
        from src.shared_contracts.authorization.errors import AccountRuntimeInUseError
        owner = "twin_runtime_attachment:" + uuid4().hex
        manager = self.system_manager
        if manager is not None and not manager.acquire(owner):
            raise AccountRuntimeInUseError()
        try:
            # Replacing/detaching an adapter must not bypass its idle lease.
            reservation = self._account_activity.hold_idle() if self._twin_runtime is not None else nullcontext(True)
            with reservation as idle:
                if not idle:
                    raise AccountRuntimeInUseError()
                self._twin_runtime = runtime
                if self._dashboard_service is not None:
                    self._dashboard_service.set_runtime(runtime)
                if self._choreography_setup_service is not None:
                    self._choreography_setup_service.set_runtime(runtime)
        finally:
            if manager is not None:
                manager.release(owner)

    def account_access_extensions(self):
        from src.engine.auth.access_extensions import AccountAccessExtensions
        return AccountAccessExtensions(activity_check=self.get_account_access_change_block_reason,
                                       idle_reservation=self._account_activity.hold_idle)

    def get_account_access_change_block_reason(self) -> str | None:
        return self._account_activity.block_reason() or super().get_account_access_change_block_reason()

    def on_start(self) -> None:
        choreography_dir = self.storage_path("choreographies")
        self._choreography_repository = ChoreographyRepository(choreography_dir)
        self._dashboard_service = TwinDashboardService(
            self._choreography_repository,
            runtime=self._twin_runtime,
        )
        self._choreography_setup_service = ChoreographySetupService(
            self._choreography_repository,
            runtime=self._twin_runtime,
        )

    def on_stop(self) -> None:
        runtime = self._twin_runtime
        stop = getattr(runtime, "stop", None)
        if callable(stop):
            try:
                stop()
            except Exception:
                self._logger.exception("Failed to stop twin runtime")
