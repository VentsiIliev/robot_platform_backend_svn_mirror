from dataclasses import replace
import os

from src.robot_systems.paint.paint_robot_system import PaintRobotSystem
from src.robot_systems.paint.component_ids import SettingsID
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
    ]

    metadata = replace(
        PaintRobotSystem.metadata,
        name="PaintSystemTrayDryer",
        settings_root=os.path.join("storage", "settings"),
        translations_root=os.path.join(
            "storage", "translations"
        ),
    )


