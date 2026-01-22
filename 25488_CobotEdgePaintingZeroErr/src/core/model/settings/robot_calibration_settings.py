from modules.robot_calibration.config_helpers import AdaptiveMovementConfig


class RobotCalibrationSettings:
    def __init__(self,):
        """ INITIALIZE WITH DEFAULT SETTINGS """
        self.min_step_mm = 0.1  # minimum movement (for very small errors)
        self.max_step_mm = 25.0  # maximum movement for very large misalignment's
        self.target_error_mm = 0.25  # desired error to reach
        self.max_error_ref = 100.0  # error at which we reach max step
        self.k = 2.0  # responsiveness (1.0 = smooth, 2.0 = faster reaction)
        self.derivative_scaling = 0.5  # how strongly derivative term reduces step
        self.z_target: int = 300  # height for refined marker search
        self.required_ids = [0, 1, 2, 3, 4, 5, 6, 8]
        self.axis_mapping_marker_id: int = 0  # marker ID used for axis mapping during calibration

        # Work area corners - pickup area (4 corners, each with x,y)
        self.work_area_pickup_corner1_x = 0
        self.work_area_pickup_corner1_y = 0
        self.work_area_pickup_corner2_x = 0
        self.work_area_pickup_corner2_y = 0
        self.work_area_pickup_corner3_x = 0
        self.work_area_pickup_corner3_y = 0
        self.work_area_pickup_corner4_x = 0
        self.work_area_pickup_corner4_y = 0

        # Work area corners - spray area (4 corners, each with x,y)
        self.work_area_spray_corner1_x = 0
        self.work_area_spray_corner1_y = 0
        self.work_area_spray_corner2_x = 0
        self.work_area_spray_corner2_y = 0
        self.work_area_spray_corner3_x = 0
        self.work_area_spray_corner3_y = 0
        self.work_area_spray_corner4_x = 0
        self.work_area_spray_corner4_y = 0

    def to_dict(self):
        return {
            "adaptive_movement_config": AdaptiveMovementConfig(
                min_step_mm=self.min_step_mm,
                max_step_mm=self.max_step_mm,
                target_error_mm=self.target_error_mm,
                max_error_ref=self.max_error_ref,
                k=self.k,
                derivative_scaling=self.derivative_scaling
            ).to_dict(),
            "z_target": self.z_target,
            "required_ids": self.required_ids,
            "axis_mapping_marker_id": self.axis_mapping_marker_id,
            # Work area corners
            "work_area_pickup_corner1_x": self.work_area_pickup_corner1_x,
            "work_area_pickup_corner1_y": self.work_area_pickup_corner1_y,
            "work_area_pickup_corner2_x": self.work_area_pickup_corner2_x,
            "work_area_pickup_corner2_y": self.work_area_pickup_corner2_y,
            "work_area_pickup_corner3_x": self.work_area_pickup_corner3_x,
            "work_area_pickup_corner3_y": self.work_area_pickup_corner3_y,
            "work_area_pickup_corner4_x": self.work_area_pickup_corner4_x,
            "work_area_pickup_corner4_y": self.work_area_pickup_corner4_y,
            "work_area_spray_corner1_x": self.work_area_spray_corner1_x,
            "work_area_spray_corner1_y": self.work_area_spray_corner1_y,
            "work_area_spray_corner2_x": self.work_area_spray_corner2_x,
            "work_area_spray_corner2_y": self.work_area_spray_corner2_y,
            "work_area_spray_corner3_x": self.work_area_spray_corner3_x,
            "work_area_spray_corner3_y": self.work_area_spray_corner3_y,
            "work_area_spray_corner4_x": self.work_area_spray_corner4_x,
            "work_area_spray_corner4_y": self.work_area_spray_corner4_y
        }

    @staticmethod
    def from_dict(data: dict):
        settings = RobotCalibrationSettings()
        adaptive_cfg = data.get("adaptive_movement_config", {})
        settings.min_step_mm = adaptive_cfg.get("min_step_mm", settings.min_step_mm)
        settings.max_step_mm = adaptive_cfg.get("max_step_mm", settings.max_step_mm)
        settings.target_error_mm = adaptive_cfg.get("target_error_mm", settings.target_error_mm)
        settings.max_error_ref = adaptive_cfg.get("max_error_ref", settings.max_error_ref)
        settings.k = adaptive_cfg.get("k", settings.k)
        settings.derivative_scaling = adaptive_cfg.get("derivative_scaling", settings.derivative_scaling)
        settings.z_target = data.get("z_target", settings.z_target)
        settings.required_ids = data.get("required_ids", settings.required_ids)
        settings.axis_mapping_marker_id = data.get("axis_mapping_marker_id", settings.axis_mapping_marker_id)

        # Load work area corners
        settings.work_area_pickup_corner1_x = data.get("work_area_pickup_corner1_x", 0)
        settings.work_area_pickup_corner1_y = data.get("work_area_pickup_corner1_y", 0)
        settings.work_area_pickup_corner2_x = data.get("work_area_pickup_corner2_x", 0)
        settings.work_area_pickup_corner2_y = data.get("work_area_pickup_corner2_y", 0)
        settings.work_area_pickup_corner3_x = data.get("work_area_pickup_corner3_x", 0)
        settings.work_area_pickup_corner3_y = data.get("work_area_pickup_corner3_y", 0)
        settings.work_area_pickup_corner4_x = data.get("work_area_pickup_corner4_x", 0)
        settings.work_area_pickup_corner4_y = data.get("work_area_pickup_corner4_y", 0)
        settings.work_area_spray_corner1_x = data.get("work_area_spray_corner1_x", 0)
        settings.work_area_spray_corner1_y = data.get("work_area_spray_corner1_y", 0)
        settings.work_area_spray_corner2_x = data.get("work_area_spray_corner2_x", 0)
        settings.work_area_spray_corner2_y = data.get("work_area_spray_corner2_y", 0)
        settings.work_area_spray_corner3_x = data.get("work_area_spray_corner3_x", 0)
        settings.work_area_spray_corner3_y = data.get("work_area_spray_corner3_y", 0)
        settings.work_area_spray_corner4_x = data.get("work_area_spray_corner4_x", 0)
        settings.work_area_spray_corner4_y = data.get("work_area_spray_corner4_y", 0)

        return settings