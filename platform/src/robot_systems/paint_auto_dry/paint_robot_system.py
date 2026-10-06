from dataclasses import replace
import os

from src.robot_systems.paint.paint_robot_system import PaintRobotSystem


class AutomaticDryerPaintRobotSystem(PaintRobotSystem):
    """Paint system variant with storage isolated for the automatic dryer."""

    metadata = replace(
        PaintRobotSystem.metadata,
        name="PaintSystemAutomaticDryer",
        settings_root=os.path.join("storage", "settings"),
        translations_root=os.path.join(
            "storage", "translations"
        ),
    )


