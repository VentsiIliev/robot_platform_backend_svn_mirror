from enum import Enum


class MovementGroupID(str, Enum):
    VERTICAL_SHAFT_ALIGNMENT = "Vertical Shaft Alignment"


class CameraRoleID(str, Enum):
    PRIMARY_VISION = "primary_vision"


class ServiceID(str, Enum):
    CUSTOM_DEVICE = "custom_device"
    VACUUM_PUMP = "vacuum_pump"
    FAN = "fan"
    TRAY_FAN = "tray_fan"
    PHYSICAL_CONTROL_BUTTONS = "physical_control_buttons"
    VACUUM_SENSOR = "vacuum_sensor"
    DRYER = "dryer"


class SettingsID(str, Enum):
    CAMERAS = "cameras"
    PAINT_HEAD_CALIBRATION = "paint_head_calibration"
    PAINT_PROCESS_CONFIG = "paint_process_config"
    PAINT_ADJUSTMENT_SETTINGS = "paint_adjustment_settings"
    DRYER_CONFIG = "dryer_config"
    PERIPHERALS = "peripherals"


class ProcessID(str, Enum):
    MAIN_PROCESS = "main_process"
    ROBOT_CALIBRATION = "robot_calibration"
    HEAD_CALIBRATION_SELECTION = "paint_head_calibration_selection"
