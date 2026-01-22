from applications.edge_painting_application.painting_operation import PaintingOperation
from applications.edge_painting_application.glue_operation import GlueOperation
from communication_layer.api.v1.topics import SystemTopics
from core.application.interfaces.application_settings_interface import ApplicationSettingsRegistry
from core.application.interfaces.robot_application_interface import RobotApplicationInterface
from core.application_state_management import ApplicationState
from core.base_robot_application import BaseRobotApplication, ApplicationMetadata, PluginType
from core.model.robot.robot_types import RobotType
from core.operation_state_management import OperationResult, OperationStatePublisher, OperationState
from core.services.robot_service.impl.base_robot_service import RobotService
from core.services.settings.SettingsService import SettingsService
from core.services.vision.VisionService import _VisionService
from core.system_state_management import ServiceRegistry
from modules.shared.MessageBroker import MessageBroker
import json
from pathlib import Path



class OperationPublisher:
    pass


class EdgePaintingApplication(BaseRobotApplication, RobotApplicationInterface):

    def __init__(self, vision_service: _VisionService,
                 settings_manager: SettingsService,
                 robot_service: RobotService,
                 settings_registry: ApplicationSettingsRegistry,
                 service_registry: ServiceRegistry,
                 **kwargs):

        self.vision_service = vision_service
        self.settings_manager = settings_manager
        self.robot_service = robot_service
        self.settings_registry = settings_registry
        self.service_registry = service_registry
        super().__init__(vision_service, settings_manager, robot_service, settings_registry, **kwargs)
        # Register application-specific settings after initialization
        self._register_settings()
        self.broker = MessageBroker()

        # Initialize painting operation
        self.painting_operation = PaintingOperation()
        self.painting_operation.set_services(self.robot_service, self.vision_service)
        self.painting_operation.set_state_publisher(OperationStatePublisher(broker=self.broker))

        # Initialize glue operation (same as painting but for glueing)
        self.glue_operation = GlueOperation()
        self.glue_operation.set_services(self.robot_service, self.vision_service)
        self.glue_operation.set_state_publisher(OperationStatePublisher(broker=self.broker))

        self.broker.publish(SystemTopics.OPERATION_STATE, OperationState.IDLE)

        # Default to painting mode
        self.operation_mode = "Painting"
        self.current_operation = self.painting_operation

        # Subscribe to mode and params changes
        self.broker.subscribe("application/operation-mode", self.on_mode_change)
        self.broker.subscribe("application/operation-params", self.on_params_change)
        self.broker.subscribe("application/alignment-mode", self.on_alignment_mode_change)

        # Load saved operation parameters on startup
        self._load_saved_operation_params()

    @staticmethod
    def get_metadata() -> ApplicationMetadata:
        return ApplicationMetadata(
            name="Edge Painting Application",
            version="1.0.0",
            robot_type=RobotType.ZERO_ERROR,  # Paint application uses ZeroError robot
            dependencies=["_VisionService",
                          "SettingsService",
                          "GlueRobotService",
                          "ApplicationSettingsRegistry"],
            plugin_dependencies=[
                PluginType.DASHBOARD,
                PluginType.SETTINGS,
                PluginType.CALIBRATION,
                PluginType.USER_MANAGEMENT
            ],
            settings_tabs=["camera", "robot"]
        )


    def get_initial_state(self) -> ApplicationState:
        return ApplicationState.INITIALIZING

    def set_current_operation(self):
        """determine the current operation based on mode"""
        if self.operation_mode == "Painting":
            self.current_operation = self.painting_operation
        else:
            self.current_operation = self.glue_operation
        print(f"Current operation set to: {self.operation_mode}")

    def _on_operation_start(self, **kwargs) -> OperationResult:
        if self.operation_mode == "Painting":
            print(f"Painting in progress")
            print(self.robotService.robot_config)
            print(f"###### Robot Calibration Settings ######")
            print(self.settingsManager.get_robot_calibration_settings().to_dict())
            self.painting_operation.start()
            return OperationResult(success=True, message="Painting started")
        else:
            print(f"Glueing in progress")
            print(self.robotService.robot_config)
            print(f"###### Robot Calibration Settings ######")
            print(self.settingsManager.get_robot_calibration_settings().to_dict())
            self.glue_operation.start()
            return OperationResult(success=True, message="Glueing started")

    @property
    def operation(self):
        return self.current_operation

    def on_mode_change(self, mode):
        """Handle operation mode change"""
        self.operation_mode = mode
        self.set_current_operation()
        print(f"Operation mode changed to: {mode}")

    def on_params_change(self, params):
        """Handle operation parameters change"""
        # Update painting operation with all parameters including lift_z, iterations, wait_time, and all pressure adjustment parameters
        if 'velocity' in params and 'acceleration' in params and 'z_offset' in params:
            self.painting_operation.set_params(
                velocity=params['velocity'],
                acceleration=params['acceleration'],
                z_offset=params['z_offset'],
                lift_z=params.get('lift_z'),
                iterations=params.get('iterations', 1),
                wait_time=params.get('wait_time', 0.0),
                center_samples=params.get('center_samples', 5),
                enable_pressure_adjustment=params.get('enable_pressure_adjustment', True),
                target_force_x=params.get('target_force_x', 2.0),
                force_adjustment_gain=params.get('force_adjustment_gain', 0.1),
                force_deadband=params.get('force_deadband', 0.5),
                max_search_distance=params.get('max_search_distance', 15.0),
                search_step_size=params.get('search_step_size', 0.5),
                contact_threshold=params.get('contact_threshold', 1.0),
                search_velocity=params.get('search_velocity', 5),
                search_at_all_corners=params.get('search_at_all_corners', True),
                max_position_adjustment=params.get('max_position_adjustment', 12.0),
                enable_rotation_adjustment=params.get('enable_rotation_adjustment', True),
                rotation_coefficient=params.get('rotation_coefficient', 0.05),
                max_rotation_adjustment=params.get('max_rotation_adjustment', 2.0)
            )
            # Update glue operation with basic parameters only (no lift_z, iterations, wait_time)
            self.glue_operation.set_params(
                velocity=params['velocity'],
                acceleration=params['acceleration'],
                z_offset=params['z_offset']
            )
            print(f"Operation parameters updated: {params}")

    def on_alignment_mode_change(self, mode):
        """Handle alignment mode change"""
        # Only painting operation needs alignment
        self.painting_operation.set_alignment_mode(mode)
        print(f"Alignment mode changed to: {mode}")

    def get_operation_params(self):
        """Get current operation parameters from painting operation"""
        return self.painting_operation.get_params()

    def reset(self) -> OperationResult:
        pass

    def _register_settings(self):
        # Register application-specific settings here
        pass

    def _load_saved_operation_params(self):
        """Load saved operation parameters from JSON file on startup"""
        try:
            # Get the settings file path
            current_file = Path(__file__)
            settings_dir = current_file.parent / "storage" / "settings"
            settings_file = settings_dir / "operation_parameters.json"

            if settings_file.exists():
                with open(settings_file, 'r') as f:
                    params = json.load(f)
                # Apply loaded parameters to operations
                self.on_params_change(params)
                print(f"✓ Loaded saved operation parameters from {settings_file}")
            else:
                print(f"ℹ No saved operation parameters found, using defaults")
        except Exception as e:
            print(f"✗ Failed to load saved operation parameters: {e}")

    def _initialize_application(self):
        super()._initialize_application()
        print("ROS2 node spinning in background thread")
