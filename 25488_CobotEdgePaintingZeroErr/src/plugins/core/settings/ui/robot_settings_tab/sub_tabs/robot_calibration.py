from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import (QVBoxLayout, QLabel, QWidget, QHBoxLayout,
                             QScrollArea, QGroupBox, QGridLayout, QLineEdit, QPushButton, QComboBox)

from plugins.core.settings.ui.BaseSettingsTabLayout import BaseSettingsTabLayout
from plugins.core.settings.enums.RobotCalibrationSettingKeys import RobotCalibrationSettingKeys
from frontend.core.utils.localization import get_app_translator
from modules.shared.MessageBroker import MessageBroker
from communication_layer.api.v1.topics import RobotTopics


# Define signals for thread-safe communication
class CalibrationSignals:
    """Signals for camera-TCP calibration thread communication"""
    def __init__(self):
        pass


class RobotCalibrationTabLayout(BaseSettingsTabLayout, QVBoxLayout):
    """
    Robot calibration settings tab layout matching existing UI patterns.
    
    Provides UI for configuring robot calibration parameters including:
    - Adaptive movement settings (6 parameters)
    - General calibration settings (z_target, required_marker_ids)
    
    Follows exact same patterns as Camera and Glue settings tabs.
    """
    
    value_changed_signal = pyqtSignal(str, object, str)  # key, value, className
    camera_tcp_calibration_complete = pyqtSignal(dict)  # Calibration result signal
    camera_tcp_calibration_error = pyqtSignal(str)  # Error message signal

    def __init__(self, parent_widget):
        """
        Initialize robot calibration settings tab.
        
        Args:
            parent_widget: Parent widget for the settings interface
        """
        BaseSettingsTabLayout.__init__(self, parent_widget)
        QVBoxLayout.__init__(self)
        
        self.parent_widget = parent_widget
        self.translator = get_app_translator()
        self.translator.language_changed.connect(self.translate)
        
        self.broker = MessageBroker()
        self.tcp_points_count = 0
        self.controller_service = None

        self._subscribe_to_tcp_updates()

        # Connect calibration signals
        self.camera_tcp_calibration_complete.connect(self._on_camera_tcp_calibration_complete)
        self.camera_tcp_calibration_error.connect(self._on_camera_tcp_calibration_error)

        self.create_main_content()
        
        self._connect_widget_signals()

    def set_controller_service(self, controller_service):
        """Set controller service reference for accessing robot backend"""
        self.controller_service = controller_service

    def create_main_content(self):
        """Create the main scrollable content area with responsive layout"""
        # Create scroll area - exact same properties as existing tabs
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Create main content widget - exact same pattern
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(20)  # Same as GlueSettings
        content_layout.setContentsMargins(20, 20, 20, 20)  # Same as GlueSettings
        
        # Add settings groups
        self.add_calibration_settings_groups(content_layout)
        
        # Add stretch at the end - same as existing
        content_layout.addStretch()
        
        scroll_area.setWidget(content_widget)
        self.addWidget(scroll_area)

    def add_calibration_settings_groups(self, parent_layout):
        """Add settings groups - first row with adaptive and general, second row with TCP calibration, third row with camera-to-TCP offset"""
        first_row_layout = QHBoxLayout()
        first_row_layout.setSpacing(15)

        groups = self.create_calibration_control_groups()
        for group in groups:
            first_row_layout.addWidget(group)

        parent_layout.addLayout(first_row_layout)

        tcp_group = self.create_tcp_calibration_group()
        parent_layout.addWidget(tcp_group)

        camera_tcp_group = self.create_camera_to_tcp_offset_group()
        parent_layout.addWidget(camera_tcp_group)

    def create_calibration_control_groups(self):
        """Create all calibration settings groups"""
        return [
            self.create_adaptive_movement_group(),
            self.create_general_calibration_group()
        ]

    def create_adaptive_movement_group(self):
        """Create adaptive movement settings group with exact styling"""
        self.adaptive_group = QGroupBox("Adaptive Movement Settings")
        layout = QGridLayout(self.adaptive_group)
        layout.setSpacing(15)  # Same as existing
        layout.setContentsMargins(20, 25, 20, 20)  # Same as existing
        
        row = 0
        
        # Min Step MM
        layout.addWidget(QLabel("Min Step:"), row, 0)
        self.min_step_spinbox = self.create_double_spinbox(0.01, 100.0, 0.1, " mm")
        layout.addWidget(self.min_step_spinbox, row, 1)
        row += 1
        
        # Max Step MM  
        layout.addWidget(QLabel("Max Step:"), row, 0)
        self.max_step_spinbox = self.create_double_spinbox(0.1, 500.0, 25.0, " mm")
        layout.addWidget(self.max_step_spinbox, row, 1)
        row += 1
        
        # Target Error MM
        layout.addWidget(QLabel("Target Error:"), row, 0) 
        self.target_error_spinbox = self.create_double_spinbox(0.01, 10.0, 0.25, " mm")
        layout.addWidget(self.target_error_spinbox, row, 1)
        row += 1
        
        # Max Error Ref
        layout.addWidget(QLabel("Max Error Ref:"), row, 0)
        self.max_error_ref_spinbox = self.create_double_spinbox(1.0, 1000.0, 100.0, " mm")
        layout.addWidget(self.max_error_ref_spinbox, row, 1)
        row += 1
        
        # Responsiveness K
        layout.addWidget(QLabel("Responsiveness (K):"), row, 0)
        self.k_spinbox = self.create_double_spinbox(0.1, 10.0, 2.0)
        layout.addWidget(self.k_spinbox, row, 1)
        row += 1
        
        # Derivative Scaling
        layout.addWidget(QLabel("Derivative Scaling:"), row, 0)
        self.derivative_scaling_spinbox = self.create_double_spinbox(0.0, 2.0, 0.5)
        layout.addWidget(self.derivative_scaling_spinbox, row, 1)
        
        return self.adaptive_group

    def create_general_calibration_group(self):
        """Create general calibration settings group"""
        self.general_group = QGroupBox("General Settings")
        layout = QGridLayout(self.general_group)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 25, 20, 20)
        
        # Z Target
        layout.addWidget(QLabel("Z Target:"), 0, 0)
        self.z_target_spinbox = self.create_spinbox(0, 1000, 300, " mm")
        layout.addWidget(self.z_target_spinbox, 0, 1)
        
        # Required Marker IDs - Simple line edit for now (will be enhanced later)
        layout.addWidget(QLabel("Required Marker IDs:"), 1, 0)
        self.required_ids_edit = QLineEdit()
        self.required_ids_edit.setText("0,1,2,3,4,5,6,8")  # Default from JSON
        self.required_ids_edit.setPlaceholderText("Comma-separated marker IDs (e.g., 0,1,2,3)")
        layout.addWidget(self.required_ids_edit, 1, 1)
        
        # Axis Mapping Marker ID
        layout.addWidget(QLabel("Axis Mapping Marker ID:"), 2, 0)
        self.axis_mapping_marker_id_spinbox = self.create_spinbox(0, 1000, 0, "")
        layout.addWidget(self.axis_mapping_marker_id_spinbox, 2, 1)

        return self.general_group

    def _connect_widget_signals(self):
        """Connect all widget signals to unified emission pattern"""
        # Use the same component type as parent RobotConfigUI
        component_type = "plugins.core.settings.ui.robot_settings_tab.RobotConfigUI"
        
        # Adaptive movement signals
        self.min_step_spinbox.valueChanged.connect(
            lambda v: self.value_changed_signal.emit(RobotCalibrationSettingKeys.MIN_STEP_MM, v, component_type))
        self.max_step_spinbox.valueChanged.connect(
            lambda v: self.value_changed_signal.emit(RobotCalibrationSettingKeys.MAX_STEP_MM, v, component_type))
        self.target_error_spinbox.valueChanged.connect(
            lambda v: self.value_changed_signal.emit(RobotCalibrationSettingKeys.TARGET_ERROR_MM, v, component_type))
        self.max_error_ref_spinbox.valueChanged.connect(
            lambda v: self.value_changed_signal.emit(RobotCalibrationSettingKeys.MAX_ERROR_REF, v, component_type))
        self.k_spinbox.valueChanged.connect(
            lambda v: self.value_changed_signal.emit(RobotCalibrationSettingKeys.RESPONSIVENESS_K, v, component_type))
        self.derivative_scaling_spinbox.valueChanged.connect(
            lambda v: self.value_changed_signal.emit(RobotCalibrationSettingKeys.DERIVATIVE_SCALING, v, component_type))
        
        # General settings signals  
        self.z_target_spinbox.valueChanged.connect(
            lambda v: self.value_changed_signal.emit(RobotCalibrationSettingKeys.Z_TARGET, v, component_type))
        self.required_ids_edit.textChanged.connect(
            lambda text: self.value_changed_signal.emit(RobotCalibrationSettingKeys.REQUIRED_MARKER_IDS, 
                                                       self._parse_marker_ids(text), component_type))
        self.axis_mapping_marker_id_spinbox.valueChanged.connect(
            lambda v: self.value_changed_signal.emit(RobotCalibrationSettingKeys.AXIS_MAPPING_MARKER_ID, v, component_type))

    def _parse_marker_ids(self, text):
        """Parse comma-separated marker IDs to list of integers"""
        try:
            if not text.strip():
                return []
            return [int(id.strip()) for id in text.split(',') if id.strip().isdigit()]
        except (ValueError, AttributeError):
            return []

    def translate(self):
        """Update UI text based on current language - exact pattern"""
        # Refresh responsive styling
        self.setup_styling()
        
        # Update group titles (will add translation keys later)
        if hasattr(self, 'adaptive_group'):
            self.adaptive_group.setTitle("Adaptive Movement Settings")  # TODO: Add translation
        if hasattr(self, 'general_group'): 
            self.general_group.setTitle("General Settings")  # TODO: Add translation

    def get_current_values(self):
        """Get current values from all widgets - for future use"""
        return {
            RobotCalibrationSettingKeys.MIN_STEP_MM: self.min_step_spinbox.value(),
            RobotCalibrationSettingKeys.MAX_STEP_MM: self.max_step_spinbox.value(),
            RobotCalibrationSettingKeys.TARGET_ERROR_MM: self.target_error_spinbox.value(),
            RobotCalibrationSettingKeys.MAX_ERROR_REF: self.max_error_ref_spinbox.value(),
            RobotCalibrationSettingKeys.RESPONSIVENESS_K: self.k_spinbox.value(),
            RobotCalibrationSettingKeys.DERIVATIVE_SCALING: self.derivative_scaling_spinbox.value(),
            RobotCalibrationSettingKeys.Z_TARGET: self.z_target_spinbox.value(),
            RobotCalibrationSettingKeys.REQUIRED_MARKER_IDS: self._parse_marker_ids(self.required_ids_edit.text()),
            RobotCalibrationSettingKeys.AXIS_MAPPING_MARKER_ID: self.axis_mapping_marker_id_spinbox.value()
        }

    def update_values(self, settings_dict):
        """Update widget values from settings dictionary - for future use"""
        # Block all signals during update to prevent save loops
        self.blockSignals(True)
        try:
            adaptive_config = settings_dict.get("adaptive_movement_config", {})

            if "min_step_mm" in adaptive_config:
                self.min_step_spinbox.setValue(adaptive_config["min_step_mm"])
            if "max_step_mm" in adaptive_config:
                self.max_step_spinbox.setValue(adaptive_config["max_step_mm"])
            if "target_error_mm" in adaptive_config:
                self.target_error_spinbox.setValue(adaptive_config["target_error_mm"])
            if "max_error_ref" in adaptive_config:
                self.max_error_ref_spinbox.setValue(adaptive_config["max_error_ref"])
            if "k" in adaptive_config:
                self.k_spinbox.setValue(adaptive_config["k"])
            if "derivative_scaling" in adaptive_config:
                self.derivative_scaling_spinbox.setValue(adaptive_config["derivative_scaling"])

            if "z_target" in settings_dict:
                self.z_target_spinbox.setValue(settings_dict["z_target"])
            if "required_ids" in settings_dict:
                ids_text = ",".join(map(str, settings_dict["required_ids"]))
                self.required_ids_edit.setText(ids_text)
            if "axis_mapping_marker_id" in settings_dict:
                self.axis_mapping_marker_id_spinbox.setValue(settings_dict["axis_mapping_marker_id"])
        finally:
            # Re-enable signals after update is complete
            self.blockSignals(False)

    def create_tcp_calibration_group(self):
        """Create TCP calibration group for 4 or 6 point calibration"""
        self.tcp_group = QGroupBox("TCP Calibration")
        layout = QGridLayout(self.tcp_group)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 25, 20, 20)

        layout.addWidget(QLabel("Calibration Mode:"), 0, 0)
        self.tcp_mode_combo = QComboBox()
        self.tcp_mode_combo.addItems(["4 Point", "6 Point"])
        layout.addWidget(self.tcp_mode_combo, 0, 1)

        self.tcp_status_label = QLabel("Points saved: 0/4")
        self.tcp_status_label.setStyleSheet("color: #666666; font-weight: 500;")
        layout.addWidget(self.tcp_status_label, 1, 0, 1, 2)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        self.tcp_save_btn = QPushButton("Save Point")
        self.tcp_save_btn.setStyleSheet("""
            QPushButton {
                background-color: #905BA9;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 13px;
                font-weight: 500;
            }
            QPushButton:hover { background-color: #7D4D96; }
            QPushButton:pressed { background-color: #6B4182; }
        """)
        self.tcp_save_btn.clicked.connect(self._on_save_tcp_point)
        button_layout.addWidget(self.tcp_save_btn)

        self.tcp_clear_btn = QPushButton("Clear")
        self.tcp_clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #F5F5F5;
                color: #666666;
                border: 1px solid #D0D0D0;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 13px;
                font-weight: 500;
            }
            QPushButton:hover { background-color: #EEEEEE; }
            QPushButton:pressed { background-color: #E8E8E8; }
        """)
        self.tcp_clear_btn.clicked.connect(self._on_clear_tcp_points)
        button_layout.addWidget(self.tcp_clear_btn)

        self.tcp_compute_btn = QPushButton("Compute TCP")
        self.tcp_compute_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 13px;
                font-weight: 500;
            }
            QPushButton:hover { background-color: #45a049; }
            QPushButton:pressed { background-color: #3d8b40; }
            QPushButton:disabled {
                background-color: #CCCCCC;
                color: #666666;
            }
        """)
        self.tcp_compute_btn.clicked.connect(self._on_compute_tcp)
        self.tcp_compute_btn.setEnabled(False)
        button_layout.addWidget(self.tcp_compute_btn)

        layout.addLayout(button_layout, 2, 0, 1, 2)

        self.tcp_result_label = QLabel("")
        self.tcp_result_label.setStyleSheet("color: #4CAF50; font-weight: 500; margin-top: 5px;")
        self.tcp_result_label.setWordWrap(True)
        layout.addWidget(self.tcp_result_label, 3, 0, 1, 2)

        return self.tcp_group

    def _subscribe_to_tcp_updates(self):
        """Subscribe to TCP calibration status and result topics"""
        print(f"[RobotCalibration] Subscribing to topics:")
        print(f"  - {RobotTopics.TCP_CALIBRATION_STATUS}")
        print(f"  - {RobotTopics.TCP_CALIBRATION_RESULT}")
        self.broker.subscribe(RobotTopics.TCP_CALIBRATION_STATUS, self._on_tcp_status_update)
        self.broker.subscribe(RobotTopics.TCP_CALIBRATION_RESULT, self._on_tcp_result)
        print(f"[RobotCalibration] Subscription complete")

    def _on_save_tcp_point(self):
        """Request saving current robot position as TCP calibration point"""
        self.broker.publish(RobotTopics.TCP_CALIBRATION_SAVE_POINT, {})

    def _on_clear_tcp_points(self):
        """Request clearing all TCP calibration points"""
        self.broker.publish(RobotTopics.TCP_CALIBRATION_CLEAR_POINTS, {})

    def _on_compute_tcp(self):
        """Request computing TCP offset from saved points"""
        self.broker.publish(RobotTopics.TCP_CALIBRATION_COMPUTE, {})

    def _on_tcp_status_update(self, message):
        """Handle TCP calibration status updates"""
        print(f"[RobotCalibration] _on_tcp_status_update called: {message}")
        if "points_count" in message:
            self.tcp_points_count = message["points_count"]
            mode = self.tcp_mode_combo.currentText()
            required = 6 if "6" in mode else 4
            self.tcp_status_label.setText(f"Points saved: {self.tcp_points_count}/{required}")
            self.tcp_compute_btn.setEnabled(self.tcp_points_count >= 4)

        if "message" in message:
            print(f"[TCP Calibration] {message['message']}")

    def _on_tcp_result(self, message):
        """Handle TCP calibration result"""
        print(f"[RobotCalibration] _on_tcp_result called with message: {message}")

        if message.get("success"):
            tcp_offset = message.get("tcp_offset", {})
            x, y, z = tcp_offset.get("x", 0), tcp_offset.get("y", 0), tcp_offset.get("z", 0)

            # Check if this is from chessboard calibration or manual TCP calibration
            source = message.get("source", "manual")
            print(f"[RobotCalibration] Source: {source}")

            if source == "chessboard_calibration":
                print("[RobotCalibration] Processing chessboard calibration result")
                # Camera-to-TCP offset from chessboard calibration
                camera_tcp_offset = message.get("camera_to_tcp_offset", {})
                result_text = (
                    f"Camera-to-TCP Offset (from chessboard calibration):\n"
                    f"X={camera_tcp_offset.get('x_mm', 0):.2f}mm, Y={camera_tcp_offset.get('y_mm', 0):.2f}mm"
                )
                self.camera_tcp_status_label.setText(result_text)
                self.camera_tcp_status_label.setStyleSheet("color: #4CAF50; font-weight: 500;")

                # Add to existing TCP offset values
                current_tcp_x = 0.0
                current_tcp_y = 0.0
                if hasattr(self.parent_widget, 'general_settings_tab'):
                    if hasattr(self.parent_widget.general_settings_tab, 'robot_info_group'):
                        robot_info = self.parent_widget.general_settings_tab.robot_info_group
                        if hasattr(robot_info, 'tcp_x_offset_edit'):
                            current_tcp_x = robot_info.tcp_x_offset_edit.value()
                        if hasattr(robot_info, 'tcp_y_offset_edit'):
                            current_tcp_y = robot_info.tcp_y_offset_edit.value()

                new_tcp_x = current_tcp_x + camera_tcp_offset.get('x_mm', 0)
                new_tcp_y = current_tcp_y + camera_tcp_offset.get('y_mm', 0)

                self.value_changed_signal.emit("tcp_x_offset", new_tcp_x, "plugins.core.settings.ui.robot_settings_tab.RobotConfigUI")
                self.value_changed_signal.emit("tcp_y_offset", new_tcp_y, "plugins.core.settings.ui.robot_settings_tab.RobotConfigUI")
            else:
                # Manual TCP calibration (4-6 point)
                rms_error = message.get("rms_error_mm", 0)
                result_text = (
                    f"TCP Offset: X={x*1000:.2f}mm, Y={y*1000:.2f}mm, Z={z*1000:.2f}mm\n"
                    f"RMS Error: {rms_error:.3f}mm"
                )
                self.tcp_result_label.setText(result_text)
                self.tcp_result_label.setStyleSheet("color: #4CAF50; font-weight: 500;")

                self.value_changed_signal.emit("tcp_x_offset", x*1000, "plugins.core.settings.ui.robot_settings_tab.RobotConfigUI")
                self.value_changed_signal.emit("tcp_y_offset", y*1000, "plugins.core.settings.ui.robot_settings_tab.RobotConfigUI")
        else:
            error = message.get("error", "Unknown error")
            self.tcp_result_label.setText(f"Error: {error}")
            self.tcp_result_label.setStyleSheet("color: #F44336; font-weight: 500;")

    def create_camera_to_tcp_offset_group(self):
        """Create camera-to-TCP offset calibration group"""
        self.camera_tcp_group = QGroupBox("Camera to TCP Offset Calibration")
        layout = QGridLayout(self.camera_tcp_group)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 25, 20, 20)

        info_label = QLabel(
            "Calibrate the physical offset from camera optical center to TCP.\n"
            "Method: Position TCP at chessboard center, then move until camera sees center."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #666666; font-size: 12px; margin-bottom: 10px;")
        layout.addWidget(info_label, 0, 0, 1, 2)

        # Calibration button
        self.calibrate_camera_tcp_btn = QPushButton("📐 Calibrate Camera-TCP Offset")
        self.calibrate_camera_tcp_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 12px 20px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover { background-color: #45a049; }
            QPushButton:pressed { background-color: #3d8b40; }
            QPushButton:disabled {
                background-color: #CCCCCC;
                color: #666666;
            }
        """)
        self.calibrate_camera_tcp_btn.clicked.connect(self._on_calibrate_camera_tcp_offset)
        layout.addWidget(self.calibrate_camera_tcp_btn, 1, 0, 1, 2)

        # Instructions
        instructions = QLabel(
            "<b>Instructions:</b><br>"
            "1. Manually position TCP EXACTLY at chessboard center<br>"
            "2. Click 'Calibrate Camera-TCP Offset' button<br>"
            "3. Robot will move in X and Y until camera sees chessboard center<br>"
            "4. System calculates offset = movement distance<br>"
            "5. Offset is automatically applied to settings"
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("color: #666666; font-size: 11px; padding: 10px; background: #F5F5F5; border-radius: 4px;")
        layout.addWidget(instructions, 2, 0, 1, 2)

        # Manual entry section
        manual_section = QLabel("<b>Or enter manually:</b>")
        manual_section.setStyleSheet("color: #333333; font-size: 12px; margin-top: 10px;")
        layout.addWidget(manual_section, 3, 0, 1, 2)

        manual_layout = QGridLayout()
        manual_layout.setSpacing(10)

        manual_layout.addWidget(QLabel("Camera X to TCP X:"), 0, 0)
        self.camera_tcp_x_spinbox = self.create_double_spinbox(-500.0, 500.0, 73.0, " mm")
        manual_layout.addWidget(self.camera_tcp_x_spinbox, 0, 1)

        manual_layout.addWidget(QLabel("Camera Y to TCP Y:"), 1, 0)
        self.camera_tcp_y_spinbox = self.create_double_spinbox(-500.0, 500.0, -48.0, " mm")
        manual_layout.addWidget(self.camera_tcp_y_spinbox, 1, 1)

        apply_btn = QPushButton("Apply Manual Offset")
        apply_btn.setStyleSheet("""
            QPushButton {
                background-color: #905BA9;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 13px;
                font-weight: 500;
            }
            QPushButton:hover { background-color: #7D4D96; }
            QPushButton:pressed { background-color: #6B4182; }
        """)
        apply_btn.clicked.connect(self._on_apply_manual_camera_tcp_offset)
        manual_layout.addWidget(apply_btn, 2, 0, 1, 2)

        layout.addLayout(manual_layout, 4, 0, 1, 2)

        self.camera_tcp_status_label = QLabel("")
        self.camera_tcp_status_label.setStyleSheet("color: #4CAF50; font-weight: 500; margin-top: 5px;")
        self.camera_tcp_status_label.setWordWrap(True)
        layout.addWidget(self.camera_tcp_status_label, 5, 0, 1, 2)

        return self.camera_tcp_group

    def _on_calibrate_camera_tcp_offset(self):
        """Start the standalone camera-to-TCP offset calibration procedure"""
        print("[RobotCalibration] _on_calibrate_camera_tcp_offset called")
        try:
            self.calibrate_camera_tcp_btn.setEnabled(False)
            self.camera_tcp_status_label.setText("Starting camera-to-TCP offset calibration...")
            self.camera_tcp_status_label.setStyleSheet("color: #2196F3; font-weight: 500;")

            print("[RobotCalibration] Importing calibration module...")
            # Import and start the calibration procedure
            from modules.robot_calibration.camera_tcp_offset_calibration import start_camera_tcp_offset_calibration
            print("[RobotCalibration] Module imported successfully")

            # Get robot service from controller
            if not self.controller_service:
                error_msg = "Controller service not available"
                print(f"[RobotCalibration] ERROR: {error_msg}")
                self.camera_tcp_status_label.setText(f"❌ Error: {error_msg}")
                self.camera_tcp_status_label.setStyleSheet("color: #F44336; font-weight: 500;")
                self.calibrate_camera_tcp_btn.setEnabled(True)
                return

            print(f"[RobotCalibration] Controller service: {self.controller_service}")

            # Start calibration in a separate thread to avoid blocking UI
            import threading
            def run_calibration():
                print("[RobotCalibration] Thread started, running calibration...")
                try:
                    result = start_camera_tcp_offset_calibration(self.controller_service)
                    print(f"[RobotCalibration] Calibration result: {result}")

                    # Emit signal for thread-safe UI update
                    self.camera_tcp_calibration_complete.emit(result)
                except Exception as e:
                    import traceback
                    error_msg = f"Calibration failed: {str(e)}\n{traceback.format_exc()}"
                    print(f"[RobotCalibration] Exception in calibration thread: {error_msg}")

                    # Emit error signal
                    self.camera_tcp_calibration_error.emit(error_msg)

            print("[RobotCalibration] Starting calibration thread...")
            thread = threading.Thread(target=run_calibration, daemon=True)
            thread.start()
            print("[RobotCalibration] Thread started successfully")

        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"[Camera-TCP Calibration] Error starting calibration: {e}\n{error_trace}")
            self.camera_tcp_status_label.setText(f"❌ Error: {str(e)}")
            self.camera_tcp_status_label.setStyleSheet("color: #F44336; font-weight: 500;")
            self.calibrate_camera_tcp_btn.setEnabled(True)

    @pyqtSlot(dict)
    def _on_camera_tcp_calibration_complete(self, result):
        """Handle completion of camera-TCP offset calibration"""
        print(f"[RobotCalibration] _on_camera_tcp_calibration_complete called with result: {result}")

        # Re-enable the button
        self.calibrate_camera_tcp_btn.setEnabled(True)

        if result.get("success"):
            offset_x = result.get("offset_x_mm", 0)
            offset_y = result.get("offset_y_mm", 0)

            print(f"[RobotCalibration] Applying offset: X={offset_x:.2f}mm, Y={offset_y:.2f}mm")

            # Update the manual entry spinboxes to show the calculated values
            self.camera_tcp_x_spinbox.setValue(offset_x)
            self.camera_tcp_y_spinbox.setValue(offset_y)

            # Apply the offset to robot settings
            self.value_changed_signal.emit("tcp_x_offset", offset_x, "plugins.core.settings.ui.robot_settings_tab.RobotConfigUI")
            self.value_changed_signal.emit("tcp_y_offset", offset_y, "plugins.core.settings.ui.robot_settings_tab.RobotConfigUI")

            # Publish TCP offset to ROS2 gui_bridge for dynamic TF updates
            if self.controller_service:
                try:
                    # Access through: controller → requestSender → request_handler → application
                    controller = self.controller_service.get_controller()
                    request_sender = getattr(controller, 'requestSender', None) if controller else None
                    request_handler = getattr(request_sender, 'request_handler', None) if request_sender else None
                    application = getattr(request_handler, 'application', None) if request_handler else None
                    robot_service = getattr(application, 'robot_service', None) if application else None

                    if robot_service and hasattr(robot_service, 'publish_tcp_offset'):
                        robot_service.publish_tcp_offset(offset_x, offset_y)
                        print(f"[RobotCalibration] ✅ Published TCP offset to ROS2: X={offset_x:.2f}mm, Y={offset_y:.2f}mm")
                    else:
                        print(f"[RobotCalibration] Warning: Could not publish TCP offset to ROS2 (robot_service not available)")
                        print(f"[RobotCalibration] Debug: controller={controller}, request_sender={request_sender}, request_handler={request_handler}, application={application}, robot_service={robot_service}")
                except Exception as e:
                    import traceback
                    print(f"[RobotCalibration] Error publishing TCP offset to ROS2: {e}")
                    print(f"[RobotCalibration] Traceback: {traceback.format_exc()}")

            print(f"[RobotCalibration] Offset applied successfully")

            self.camera_tcp_status_label.setText(
                f"✅ Calibration complete!\n"
                f"Camera-to-TCP offset: X={offset_x:.2f}mm, Y={offset_y:.2f}mm\n"
                f"Applied to robot settings."
            )
            self.camera_tcp_status_label.setStyleSheet("color: #4CAF50; font-weight: 500;")
        else:
            error = result.get("error", "Unknown error")
            print(f"[RobotCalibration] Calibration failed: {error}")
            self.camera_tcp_status_label.setText(f"❌ Calibration failed: {error}")
            self.camera_tcp_status_label.setStyleSheet("color: #F44336; font-weight: 500;")

    @pyqtSlot(str)
    def _on_camera_tcp_calibration_error(self, error_msg):
        """Handle error during camera-TCP offset calibration"""
        print(f"[RobotCalibration] _on_camera_tcp_calibration_error called: {error_msg}")
        self.calibrate_camera_tcp_btn.setEnabled(True)
        self.camera_tcp_status_label.setText(f"❌ Error: {error_msg}")
        self.camera_tcp_status_label.setStyleSheet("color: #F44336; font-weight: 500;")

    def _on_apply_manual_camera_tcp_offset(self):
        """Apply manually entered camera-to-TCP offset by adding to existing TCP calibration values"""
        try:
            camera_tcp_x = self.camera_tcp_x_spinbox.value()
            camera_tcp_y = self.camera_tcp_y_spinbox.value()

            # Get current TCP offset values from the robot info group
            current_tcp_x = 0.0
            current_tcp_y = 0.0

            # Try to get current values from parent RobotConfigUI
            if hasattr(self.parent_widget, 'general_settings_tab'):
                if hasattr(self.parent_widget.general_settings_tab, 'robot_info_group'):
                    robot_info = self.parent_widget.general_settings_tab.robot_info_group
                    if hasattr(robot_info, 'tcp_x_offset_edit'):
                        current_tcp_x = robot_info.tcp_x_offset_edit.value()
                    if hasattr(robot_info, 'tcp_y_offset_edit'):
                        current_tcp_y = robot_info.tcp_y_offset_edit.value()

            # Add manual offset to current TCP calibration values
            new_tcp_x = current_tcp_x + camera_tcp_x
            new_tcp_y = current_tcp_y + camera_tcp_y

            self.value_changed_signal.emit("tcp_x_offset", new_tcp_x, "plugins.core.settings.ui.robot_settings_tab.RobotConfigUI")
            self.value_changed_signal.emit("tcp_y_offset", new_tcp_y, "plugins.core.settings.ui.robot_settings_tab.RobotConfigUI")

            self.camera_tcp_status_label.setText(
                f"Manual offset added to TCP calibration:\n"
                f"Previous TCP: X={current_tcp_x:.2f}mm, Y={current_tcp_y:.2f}mm\n"
                f"Camera-TCP Offset: X={camera_tcp_x:.2f}mm, Y={camera_tcp_y:.2f}mm\n"
                f"New TCP Total: X={new_tcp_x:.2f}mm, Y={new_tcp_y:.2f}mm"
            )
            self.camera_tcp_status_label.setStyleSheet("color: #4CAF50; font-weight: 500;")

        except Exception as e:
            import traceback
            print(f"[Manual Camera-TCP Offset] Error: {e}")
            traceback.print_exc()
            self.camera_tcp_status_label.setText(f"Error: {str(e)}")
            self.camera_tcp_status_label.setStyleSheet("color: #F44336; font-weight: 500;")

    def _on_capture_tcp_position(self):
        """Capture TCP position and calculate offset from camera center automatically"""
        try:
            if not self.controller_service:
                self.camera_tcp_status_label.setText("Error: Controller service not available")
                self.camera_tcp_status_label.setStyleSheet("color: #F44336; font-weight: 500;")
                return

            result = self.controller_service.robot.get_current_position()
            if not result or not result.data or len(result.data) < 2:
                self.camera_tcp_status_label.setText("Error: Could not get robot position")
                self.camera_tcp_status_label.setStyleSheet("color: #F44336; font-weight: 500;")
                return

            current_position = result.data

            import json
            import os

            calib_file = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "../../../../../transformation_to_camera_center.json"
            )

            if not os.path.exists(calib_file):
                self.camera_tcp_status_label.setText(
                    "Error: Robot calibration data not found. Run robot calibration first."
                )
                self.camera_tcp_status_label.setStyleSheet("color: #F44336; font-weight: 500;")
                return

            with open(calib_file, 'r') as f:
                calib_data = json.load(f)

            if not calib_data.get("calibration_points"):
                self.camera_tcp_status_label.setText("Error: No calibration points found")
                self.camera_tcp_status_label.setStyleSheet("color: #F44336; font-weight: 500;")
                return

            import numpy as np
            camera_center_points = []
            for point in calib_data["calibration_points"]:
                robot_pt = point.get("robot_point", [])
                if len(robot_pt) >= 2:
                    camera_center_points.append(robot_pt[:2])

            if len(camera_center_points) < 4:
                self.camera_tcp_status_label.setText("Error: Insufficient calibration points")
                self.camera_tcp_status_label.setStyleSheet("color: #F44336; font-weight: 500;")
                return

            camera_center_points = np.array(camera_center_points)
            camera_center_avg = np.mean(camera_center_points, axis=0)

            tcp_x = current_position[0]
            tcp_y = current_position[1]

            offset_x = camera_center_avg[0] - tcp_x
            offset_y = camera_center_avg[1] - tcp_y

            # Get current TCP offset values from the robot info group
            current_tcp_x = 0.0
            current_tcp_y = 0.0

            # Try to get current values from parent RobotConfigUI
            if hasattr(self.parent_widget, 'general_settings_tab'):
                if hasattr(self.parent_widget.general_settings_tab, 'robot_info_group'):
                    robot_info = self.parent_widget.general_settings_tab.robot_info_group
                    if hasattr(robot_info, 'tcp_x_offset_edit'):
                        current_tcp_x = robot_info.tcp_x_offset_edit.value()
                    if hasattr(robot_info, 'tcp_y_offset_edit'):
                        current_tcp_y = robot_info.tcp_y_offset_edit.value()

            # Add calculated offset to current TCP calibration values
            new_tcp_x = current_tcp_x + offset_x
            new_tcp_y = current_tcp_y + offset_y

            self.value_changed_signal.emit("tcp_x_offset", new_tcp_x, "plugins.core.settings.ui.robot_settings_tab.RobotConfigUI")
            self.value_changed_signal.emit("tcp_y_offset", new_tcp_y, "plugins.core.settings.ui.robot_settings_tab.RobotConfigUI")

            self.camera_tcp_status_label.setText(
                f"Offset calculated and added to TCP calibration:\n"
                f"Camera Center: X={camera_center_avg[0]:.2f}mm, Y={camera_center_avg[1]:.2f}mm\n"
                f"TCP Position: X={tcp_x:.2f}mm, Y={tcp_y:.2f}mm\n"
                f"Camera-TCP Offset: X={offset_x:.2f}mm, Y={offset_y:.2f}mm\n"
                f"Previous TCP: X={current_tcp_x:.2f}mm, Y={current_tcp_y:.2f}mm\n"
                f"New TCP Total: X={new_tcp_x:.2f}mm, Y={new_tcp_y:.2f}mm"
            )
            self.camera_tcp_status_label.setStyleSheet("color: #4CAF50; font-weight: 500;")

        except Exception as e:
            import traceback
            print(f"[Camera-TCP Offset] Error: {e}")
            traceback.print_exc()
            self.camera_tcp_status_label.setText(f"Error: {str(e)}")
            self.camera_tcp_status_label.setStyleSheet("color: #F44336; font-weight: 500;")


