from dataclasses import replace
import os

from src.robot_systems.paint.paint_robot_system import PaintRobotSystem
from src.robot_systems.paint.component_ids import SettingsID
from src.robot_systems.paint_tray_dry.component_ids import ServiceID, SettingsID as TraySettingsID
from src.engine.hardware.operator_lights.config import OperatorLightsConfigSerializer
from src.engine.hardware.operator_lights.i_operator_lights import IOperatorLights
from src.robot_systems.paint_tray_dry.service_builders import build_operator_lights_service
from src.shared_contracts.declarations import ServiceSpec, SettingsSpec
from src.robot_systems.paint.processes.paint.paint_process_config_serializer import PaintProcessConfigSerializer


class TrayDryerPaintRobotSystem(PaintRobotSystem):
    """Paint system variant with storage isolated for the tray dryer."""

    ui_config = replace(
        PaintRobotSystem.ui_config,
        show_drying_mode_control=False,
    )
    allowed_dropoff_strategies = ("plate_layout",)

    # Fresh installations must use a strategy supported by this profile.
    settings_specs = [
        replace(spec, serializer=PaintProcessConfigSerializer(
            replace(
                spec.serializer.get_default(),
                dropoff=replace(spec.serializer.get_default().dropoff, strategy="plate_layout"),
            )
        )) if spec.name == SettingsID.PAINT_PROCESS_CONFIG else spec
        for spec in PaintRobotSystem.settings_specs
    ] + [
        SettingsSpec(TraySettingsID.OPERATOR_LIGHTS, OperatorLightsConfigSerializer(),
                     "hardware/operator_lights.json"),
    ]

    services = [*PaintRobotSystem.services,
        ServiceSpec(ServiceID.OPERATOR_LIGHTS, IOperatorLights, required=False,
                    description="Configurable operator light outputs",
                    builder=build_operator_lights_service),
    ]

    def on_start(self) -> None:
        super().on_start()
        self._operator_lights = self.get_optional_service(ServiceID.OPERATOR_LIGHTS)
        if self._operator_lights is not None:
            self.register_managed_resource(self._operator_lights)
            from src.robot_systems.paint_tray_dry.operator_light_coordinator import OperatorLightCoordinator
            from src.robot_systems.paint.component_ids import ProcessID

            self._operator_light_coordinator = OperatorLightCoordinator(
                self._operator_lights, self.get_settings(TraySettingsID.OPERATOR_LIGHTS),
                self._messaging_service, ProcessID.MAIN_PROCESS,
                state_getter=self._get_paint_process_state,
            )
            self.register_managed_resource(self._operator_light_coordinator)
            self._operator_light_coordinator.start()

    def _get_paint_process_state(self):
        return self._main_process.state

    metadata = replace(
        PaintRobotSystem.metadata,
        name="PaintSystemTrayDryer",
        settings_root=os.path.join("storage", "settings"),
        translations_root=os.path.join(
            "storage", "translations"
        ),
    )


