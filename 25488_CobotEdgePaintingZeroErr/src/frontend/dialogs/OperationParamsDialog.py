from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QSpinBox, QDoubleSpinBox, QGroupBox, QPushButton, QCheckBox
)
from PyQt6.QtCore import pyqtSignal, Qt
import json
from pathlib import Path


class OperationParamsDialog(QDialog):
    params_changed = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Operation Parameters")
        self.setModal(True)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        self.resize(1400, 900)  # Wider window for two-column layout

        # Define settings file path
        self.settings_file = self._get_settings_file_path()

        self.init_ui()

        # Load saved settings after UI is initialized
        self.load_settings()

    def init_ui(self):
        main_layout = QVBoxLayout()

        # === Title ===
        title_label = QLabel("Operation Parameters Configuration")
        title_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #333;
            margin-bottom: 10px;
            padding: 10px;
            background-color: #f0f0f0;
            border-radius: 4px;
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)

        # === Two-Column Layout ===
        columns_layout = QHBoxLayout()

        # Left Column
        left_column = QVBoxLayout()

        # Right Column
        right_column = QVBoxLayout()

        # === LEFT COLUMN ===

        # === Movement Parameters Group ===
        movement_group = QGroupBox("Movement Parameters")
        movement_layout = QGridLayout()

        # Velocity
        movement_layout.addWidget(QLabel("Velocity:"), 0, 0)
        self.velocity_spinbox = QSpinBox()
        self.velocity_spinbox.setRange(0, 100)
        self.velocity_spinbox.setValue(20)
        self.velocity_spinbox.setSuffix(" %")
        self.velocity_spinbox.valueChanged.connect(self._on_params_changed)
        movement_layout.addWidget(self.velocity_spinbox, 0, 1)

        # Acceleration
        movement_layout.addWidget(QLabel("Acceleration:"), 1, 0)
        self.acceleration_spinbox = QSpinBox()
        self.acceleration_spinbox.setRange(0, 100)
        self.acceleration_spinbox.setValue(20)
        self.acceleration_spinbox.setSuffix(" %")
        self.acceleration_spinbox.valueChanged.connect(self._on_params_changed)
        movement_layout.addWidget(self.acceleration_spinbox, 1, 1)

        # Z Offset
        movement_layout.addWidget(QLabel("Z Offset:"), 2, 0)
        self.z_offset_spinbox = QDoubleSpinBox()
        self.z_offset_spinbox.setRange(0.0, 100.0)
        self.z_offset_spinbox.setValue(6.0)
        self.z_offset_spinbox.setSingleStep(0.1)
        self.z_offset_spinbox.setSuffix(" mm")
        self.z_offset_spinbox.setDecimals(1)
        self.z_offset_spinbox.valueChanged.connect(self._on_params_changed)
        movement_layout.addWidget(self.z_offset_spinbox, 2, 1)

        # Lift Z
        movement_layout.addWidget(QLabel("Lift Z:"), 3, 0)
        self.lift_z_spinbox = QDoubleSpinBox()
        self.lift_z_spinbox.setRange(0.0, 500.0)
        self.lift_z_spinbox.setValue(200.0)
        self.lift_z_spinbox.setSingleStep(1.0)
        self.lift_z_spinbox.setSuffix(" mm")
        self.lift_z_spinbox.setDecimals(1)
        self.lift_z_spinbox.valueChanged.connect(self._on_params_changed)
        movement_layout.addWidget(self.lift_z_spinbox, 3, 1)

        # Rotation Step (degrees per waypoint during edge rotation)
        movement_layout.addWidget(QLabel("Rotation Step:"), 4, 0)
        self.rotation_step_spinbox = QDoubleSpinBox()
        self.rotation_step_spinbox.setRange(0.1, 90.0)
        self.rotation_step_spinbox.setValue(1.0)
        self.rotation_step_spinbox.setSingleStep(0.1)
        self.rotation_step_spinbox.setSuffix(" deg")
        self.rotation_step_spinbox.setDecimals(1)
        self.rotation_step_spinbox.setToolTip("Degrees per step during 90° edge rotation (smaller = smoother)")
        self.rotation_step_spinbox.valueChanged.connect(self._on_params_changed)
        movement_layout.addWidget(self.rotation_step_spinbox, 4, 1)

        # Joint Rotation Step (for joint 6 rotations)
        movement_layout.addWidget(QLabel("Joint Rotation Step:"), 5, 0)
        self.joint_rotation_step_spinbox = QDoubleSpinBox()
        self.joint_rotation_step_spinbox.setRange(0.5, 90.0)
        self.joint_rotation_step_spinbox.setValue(3.0)
        self.joint_rotation_step_spinbox.setSingleStep(0.5)
        self.joint_rotation_step_spinbox.setSuffix(" deg")
        self.joint_rotation_step_spinbox.setDecimals(1)
        self.joint_rotation_step_spinbox.setToolTip("Degrees per step for joint 6 rotation movements")
        self.joint_rotation_step_spinbox.valueChanged.connect(self._on_params_changed)
        movement_layout.addWidget(self.joint_rotation_step_spinbox, 5, 1)

        movement_group.setLayout(movement_layout)
        left_column.addWidget(movement_group)

        # === Operation Parameters Group ===
        operation_group = QGroupBox("Operation Parameters")
        operation_layout = QGridLayout()

        # Iterations
        operation_layout.addWidget(QLabel("Iterations:"), 0, 0)
        self.iterations_spinbox = QSpinBox()
        self.iterations_spinbox.setRange(1, 100)
        self.iterations_spinbox.setValue(1)
        self.iterations_spinbox.valueChanged.connect(self._on_params_changed)
        operation_layout.addWidget(self.iterations_spinbox, 0, 1)

        # Wait Time
        operation_layout.addWidget(QLabel("Wait Time:"), 1, 0)
        self.wait_time_spinbox = QDoubleSpinBox()
        self.wait_time_spinbox.setRange(0.0, 300.0)
        self.wait_time_spinbox.setValue(0.0)
        self.wait_time_spinbox.setSingleStep(0.5)
        self.wait_time_spinbox.setSuffix(" s")
        self.wait_time_spinbox.setDecimals(1)
        self.wait_time_spinbox.valueChanged.connect(self._on_params_changed)
        operation_layout.addWidget(self.wait_time_spinbox, 1, 1)

        # Center Samples
        operation_layout.addWidget(QLabel("Center Samples:"), 2, 0)
        self.center_samples_spinbox = QSpinBox()
        self.center_samples_spinbox.setRange(1, 20)
        self.center_samples_spinbox.setValue(5)
        self.center_samples_spinbox.setToolTip("Number of images to capture for median center calculation")
        self.center_samples_spinbox.valueChanged.connect(self._on_params_changed)
        operation_layout.addWidget(self.center_samples_spinbox, 2, 1)

        operation_group.setLayout(operation_layout)
        left_column.addWidget(operation_group)

        # === Contour Following Parameters Group ===
        contour_group = QGroupBox("Contour Following (Complex Shapes)")
        contour_layout = QGridLayout()

        # Enable Contour Following
        contour_layout.addWidget(QLabel("Enable Contour Following:"), 0, 0)
        self.enable_contour_following_checkbox = QCheckBox()
        self.enable_contour_following_checkbox.setChecked(True)
        self.enable_contour_following_checkbox.setToolTip("Use actual contour path for circles, ovals, fillets, and chamfers")
        self.enable_contour_following_checkbox.stateChanged.connect(self._on_params_changed)
        contour_layout.addWidget(self.enable_contour_following_checkbox, 0, 1)

        # Contour Simplification Epsilon
        contour_layout.addWidget(QLabel("Simplification:"), 1, 0)
        self.contour_epsilon_spinbox = QDoubleSpinBox()
        self.contour_epsilon_spinbox.setRange(0.5, 10.0)
        self.contour_epsilon_spinbox.setValue(2.0)
        self.contour_epsilon_spinbox.setSingleStep(0.5)
        self.contour_epsilon_spinbox.setSuffix(" mm")
        self.contour_epsilon_spinbox.setDecimals(1)
        self.contour_epsilon_spinbox.setToolTip("Douglas-Peucker epsilon for contour simplification (higher = fewer points)")
        self.contour_epsilon_spinbox.valueChanged.connect(self._on_params_changed)
        contour_layout.addWidget(self.contour_epsilon_spinbox, 1, 1)

        # Min Segment Length
        contour_layout.addWidget(QLabel("Min Segment Length:"), 2, 0)
        self.min_segment_length_spinbox = QDoubleSpinBox()
        self.min_segment_length_spinbox.setRange(1.0, 20.0)
        self.min_segment_length_spinbox.setValue(3.0)
        self.min_segment_length_spinbox.setSingleStep(0.5)
        self.min_segment_length_spinbox.setSuffix(" mm")
        self.min_segment_length_spinbox.setDecimals(1)
        self.min_segment_length_spinbox.setToolTip("Minimum segment length to process (filters out noise)")
        self.min_segment_length_spinbox.valueChanged.connect(self._on_params_changed)
        contour_layout.addWidget(self.min_segment_length_spinbox, 2, 1)

        # Rotation Lookahead Points
        contour_layout.addWidget(QLabel("Rotation Lookahead:"), 3, 0)
        self.rotation_lookahead_spinbox = QSpinBox()
        self.rotation_lookahead_spinbox.setRange(1, 20)
        self.rotation_lookahead_spinbox.setValue(5)
        self.rotation_lookahead_spinbox.setToolTip("Number of points to look ahead for smoother rotation transitions")
        self.rotation_lookahead_spinbox.valueChanged.connect(self._on_params_changed)
        contour_layout.addWidget(self.rotation_lookahead_spinbox, 3, 1)

        contour_group.setLayout(contour_layout)
        left_column.addWidget(contour_group)

        # Add stretch to left column to push content to top
        left_column.addStretch()

        # === RIGHT COLUMN ===

        # === Pressure Adjustment Group ===
        pressure_group = QGroupBox("Pressure Adjustment")
        pressure_layout = QGridLayout()

        # Pressure Enable
        pressure_layout.addWidget(QLabel("Enable:"), 0, 0)
        self.pressure_enable_button = QPushButton("ENABLED")
        self.pressure_enable_button.setCheckable(True)
        self.pressure_enable_button.setChecked(True)
        self.pressure_enable_button.clicked.connect(self._on_pressure_enable_toggle)
        self.setup_pressure_button(self.pressure_enable_button)
        pressure_layout.addWidget(self.pressure_enable_button, 0, 1)

        # Target Force
        pressure_layout.addWidget(QLabel("Target Force:"), 1, 0)
        self.target_force_spinbox = QDoubleSpinBox()
        self.target_force_spinbox.setRange(0.01, 20.0)
        self.target_force_spinbox.setValue(2.0)
        self.target_force_spinbox.setSingleStep(0.01)
        self.target_force_spinbox.setSuffix(" N")
        self.target_force_spinbox.setDecimals(2)
        self.target_force_spinbox.valueChanged.connect(self._on_params_changed)
        pressure_layout.addWidget(self.target_force_spinbox, 1, 1)

        # Force Gain
        pressure_layout.addWidget(QLabel("Force Gain:"), 2, 0)
        self.force_gain_spinbox = QDoubleSpinBox()
        self.force_gain_spinbox.setRange(0.01, 1.0)
        self.force_gain_spinbox.setValue(0.1)
        self.force_gain_spinbox.setSingleStep(0.01)
        self.force_gain_spinbox.setSuffix(" mm/N")
        self.force_gain_spinbox.setDecimals(2)
        self.force_gain_spinbox.valueChanged.connect(self._on_params_changed)
        pressure_layout.addWidget(self.force_gain_spinbox, 2, 1)

        # Force Deadband
        pressure_layout.addWidget(QLabel("Force Deadband:"), 3, 0)
        self.force_deadband_spinbox = QDoubleSpinBox()
        self.force_deadband_spinbox.setRange(0.0, 5.0)
        self.force_deadband_spinbox.setValue(0.5)
        self.force_deadband_spinbox.setSingleStep(0.01)
        self.force_deadband_spinbox.setSuffix(" N")
        self.force_deadband_spinbox.setDecimals(2)
        self.force_deadband_spinbox.valueChanged.connect(self._on_params_changed)
        pressure_layout.addWidget(self.force_deadband_spinbox, 3, 1)

        pressure_group.setLayout(pressure_layout)
        right_column.addWidget(pressure_group)

        # === Contact Search Parameters Group ===
        contact_group = QGroupBox("Contact Search Parameters")
        contact_layout = QGridLayout()

        # Max Search Distance
        contact_layout.addWidget(QLabel("Max Search Distance:"), 0, 0)
        self.max_search_distance_spinbox = QDoubleSpinBox()
        self.max_search_distance_spinbox.setRange(1.0, 50.0)
        self.max_search_distance_spinbox.setValue(15.0)
        self.max_search_distance_spinbox.setSingleStep(1.0)
        self.max_search_distance_spinbox.setSuffix(" mm")
        self.max_search_distance_spinbox.setDecimals(1)
        self.max_search_distance_spinbox.valueChanged.connect(self._on_params_changed)
        contact_layout.addWidget(self.max_search_distance_spinbox, 0, 1)

        # Search Step Size
        contact_layout.addWidget(QLabel("Search Step Size:"), 1, 0)
        self.search_step_size_spinbox = QDoubleSpinBox()
        self.search_step_size_spinbox.setRange(0.1, 5.0)
        self.search_step_size_spinbox.setValue(0.5)
        self.search_step_size_spinbox.setSingleStep(0.1)
        self.search_step_size_spinbox.setSuffix(" mm")
        self.search_step_size_spinbox.setDecimals(1)
        self.search_step_size_spinbox.valueChanged.connect(self._on_params_changed)
        contact_layout.addWidget(self.search_step_size_spinbox, 1, 1)

        # Contact Threshold
        contact_layout.addWidget(QLabel("Contact Threshold:"), 2, 0)
        self.contact_threshold_spinbox = QDoubleSpinBox()
        self.contact_threshold_spinbox.setRange(0.01, 10.0)
        self.contact_threshold_spinbox.setValue(1.0)
        self.contact_threshold_spinbox.setSingleStep(0.01)
        self.contact_threshold_spinbox.setSuffix(" N")
        self.contact_threshold_spinbox.setDecimals(2)
        self.contact_threshold_spinbox.valueChanged.connect(self._on_params_changed)
        contact_layout.addWidget(self.contact_threshold_spinbox, 2, 1)

        # Search Velocity
        contact_layout.addWidget(QLabel("Search Velocity:"), 3, 0)
        self.search_velocity_spinbox = QSpinBox()
        self.search_velocity_spinbox.setRange(1, 20)
        self.search_velocity_spinbox.setValue(5)
        self.search_velocity_spinbox.setSuffix(" %")
        self.search_velocity_spinbox.valueChanged.connect(self._on_params_changed)
        contact_layout.addWidget(self.search_velocity_spinbox, 3, 1)

        # Search At All Corners
        contact_layout.addWidget(QLabel("Search At All Corners:"), 4, 0)
        self.search_all_corners_button = QPushButton("ALL CORNERS")
        self.search_all_corners_button.setCheckable(True)
        self.search_all_corners_button.setChecked(True)
        self.search_all_corners_button.clicked.connect(self._on_search_corners_toggle)
        self.setup_search_corners_button(self.search_all_corners_button)
        contact_layout.addWidget(self.search_all_corners_button, 4, 1)

        contact_group.setLayout(contact_layout)
        right_column.addWidget(contact_group)

        # === Advanced Pressure Parameters Group ===
        advanced_group = QGroupBox("Advanced Pressure Parameters")
        advanced_layout = QGridLayout()

        # Enable Rotation Adjustment
        advanced_layout.addWidget(QLabel("Enable Rotation Adjustment:"), 0, 0)
        self.rotation_adjustment_button = QPushButton("ENABLED")
        self.rotation_adjustment_button.setCheckable(True)
        self.rotation_adjustment_button.setChecked(True)
        self.rotation_adjustment_button.clicked.connect(self._on_rotation_adjustment_toggle)
        self.setup_rotation_adjustment_button(self.rotation_adjustment_button)
        advanced_layout.addWidget(self.rotation_adjustment_button, 0, 1)

        # Max Position Adjustment
        advanced_layout.addWidget(QLabel("Max Position Adjustment:"), 1, 0)
        self.max_position_adjustment_spinbox = QDoubleSpinBox()
        self.max_position_adjustment_spinbox.setRange(1.0, 20.0)
        self.max_position_adjustment_spinbox.setValue(12.0)
        self.max_position_adjustment_spinbox.setSingleStep(1.0)
        self.max_position_adjustment_spinbox.setSuffix(" mm")
        self.max_position_adjustment_spinbox.setDecimals(1)
        self.max_position_adjustment_spinbox.valueChanged.connect(self._on_params_changed)
        advanced_layout.addWidget(self.max_position_adjustment_spinbox, 1, 1)

        # Rotation Coefficient
        advanced_layout.addWidget(QLabel("Rotation Coefficient:"), 2, 0)
        self.rotation_coefficient_spinbox = QDoubleSpinBox()
        self.rotation_coefficient_spinbox.setRange(0.01, 0.5)
        self.rotation_coefficient_spinbox.setValue(0.05)
        self.rotation_coefficient_spinbox.setSingleStep(0.01)
        self.rotation_coefficient_spinbox.setSuffix(" deg/(mm·N)")
        self.rotation_coefficient_spinbox.setDecimals(2)
        self.rotation_coefficient_spinbox.valueChanged.connect(self._on_params_changed)
        advanced_layout.addWidget(self.rotation_coefficient_spinbox, 2, 1)

        # Max Rotation Adjustment
        advanced_layout.addWidget(QLabel("Max Rotation Adjustment:"), 3, 0)
        self.max_rotation_adjustment_spinbox = QDoubleSpinBox()
        self.max_rotation_adjustment_spinbox.setRange(0.5, 10.0)
        self.max_rotation_adjustment_spinbox.setValue(2.0)
        self.max_rotation_adjustment_spinbox.setSingleStep(0.5)
        self.max_rotation_adjustment_spinbox.setSuffix(" deg")
        self.max_rotation_adjustment_spinbox.setDecimals(1)
        self.max_rotation_adjustment_spinbox.valueChanged.connect(self._on_params_changed)
        advanced_layout.addWidget(self.max_rotation_adjustment_spinbox, 3, 1)

        advanced_group.setLayout(advanced_layout)
        right_column.addWidget(advanced_group)

        # Add stretch to right column to push content to top
        right_column.addStretch()

        # Add both columns to the columns layout
        columns_layout.addLayout(left_column)
        columns_layout.addLayout(right_column)

        # Add columns layout to main layout
        main_layout.addLayout(columns_layout)

        # === Current Values Display ===
        self.current_values_label = QLabel()
        self.current_values_label.setStyleSheet("""
            font-size: 12px;
            color: #666;
            padding: 5px;
            background-color: #f9f9f9;
            border: 1px solid #ddd;
            border-radius: 3px;
        """)
        self.update_display()
        main_layout.addWidget(self.current_values_label)

        # === Buttons ===
        button_layout = QHBoxLayout()

        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.clicked.connect(self.reset_values)
        reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 6px 12px;
            }
            QPushButton:hover { background-color: #e9ecef; }
        """)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border-radius: 4px;
                padding: 6px 12px;
            }
            QPushButton:hover { background-color: #5a6268; }
        """)

        button_layout.addWidget(reset_btn)
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        main_layout.addLayout(button_layout)

        # Info label
        info_label = QLabel("Press Ctrl+O to toggle this window")
        info_label.setStyleSheet("color: #888; font-size: 11px; padding: 5px;")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(info_label)

        self.setLayout(main_layout)

    def setup_pressure_button(self, button: QPushButton):
        """Setup pressure enable button with color toggle"""
        button.setCheckable(True)
        button.toggled.connect(lambda checked: self.update_pressure_button_color(button, checked))
        self.update_pressure_button_color(button, button.isChecked())

    def update_pressure_button_color(self, button: QPushButton, checked: bool):
        """Update button color based on state"""
        if checked:
            button.setText("ENABLED")
            button.setStyleSheet("""
                QPushButton {
                    background-color: #28a745;
                    color: white;
                    border-radius: 4px;
                    padding: 6px 12px;
                    font-weight: bold;
                }
                QPushButton:hover { background-color: #218838; }
            """)
        else:
            button.setText("DISABLED")
            button.setStyleSheet("""
                QPushButton {
                    background-color: #dc3545;
                    color: white;
                    border-radius: 4px;
                    padding: 6px 12px;
                    font-weight: bold;
                }
                QPushButton:hover { background-color: #c82333; }
            """)

    def _on_pressure_enable_toggle(self):
        """Toggle pressure adjustment ON/OFF"""
        self._on_params_changed()
        self.update_display()

    def setup_search_corners_button(self, button: QPushButton):
        """Setup initial styling for search corners button"""
        self.update_search_corners_button_color(button, button.isChecked())

    def update_search_corners_button_color(self, button: QPushButton, checked: bool):
        """Update button color based on state"""
        if checked:
            button.setText("ALL CORNERS")
            button.setStyleSheet("""
                QPushButton {
                    background-color: #007bff;
                    color: white;
                    border-radius: 4px;
                    padding: 6px 12px;
                    font-weight: bold;
                }
                QPushButton:hover { background-color: #0056b3; }
            """)
        else:
            button.setText("START ONLY")
            button.setStyleSheet("""
                QPushButton {
                    background-color: #6c757d;
                    color: white;
                    border-radius: 4px;
                    padding: 6px 12px;
                    font-weight: bold;
                }
                QPushButton:hover { background-color: #5a6268; }
            """)

    def _on_search_corners_toggle(self):
        """Toggle search at all corners ON/OFF"""
        checked = self.search_all_corners_button.isChecked()
        self.update_search_corners_button_color(self.search_all_corners_button, checked)
        self._on_params_changed()
        self.update_display()

    def setup_rotation_adjustment_button(self, button: QPushButton):
        """Setup rotation adjustment button with color toggle"""
        button.setCheckable(True)
        button.toggled.connect(lambda checked: self.update_rotation_adjustment_button_color(button, checked))
        self.update_rotation_adjustment_button_color(button, button.isChecked())

    def update_rotation_adjustment_button_color(self, button: QPushButton, checked: bool):
        """Update button color based on state"""
        if checked:
            button.setText("ENABLED")
            button.setStyleSheet("""
                QPushButton {
                    background-color: #17a2b8;
                    color: white;
                    border-radius: 4px;
                    padding: 6px 12px;
                    font-weight: bold;
                }
                QPushButton:hover { background-color: #138496; }
            """)
        else:
            button.setText("DISABLED")
            button.setStyleSheet("""
                QPushButton {
                    background-color: #6c757d;
                    color: white;
                    border-radius: 4px;
                    padding: 6px 12px;
                    font-weight: bold;
                }
                QPushButton:hover { background-color: #5a6268; }
            """)

    def _on_rotation_adjustment_toggle(self):
        """Toggle rotation adjustment ON/OFF"""
        checked = self.rotation_adjustment_button.isChecked()
        self.update_rotation_adjustment_button_color(self.rotation_adjustment_button, checked)
        self._on_params_changed()
        self.update_display()

    def _on_params_changed(self):
        """Emit signal when parameters change"""
        params = self.get_params()
        self.params_changed.emit(params)
        self.update_display()
        # Auto-save settings when parameters change
        self.save_settings()

    def update_display(self):
        """Update the current values display"""
        params = self.get_params()
        pressure_status = "ENABLED" if params['enable_pressure_adjustment'] else "DISABLED"
        self.current_values_label.setText(
            f"Vel: {params['velocity']}% | Acc: {params['acceleration']}% | "
            f"Z: {params['z_offset']:.1f}mm | Lift: {params['lift_z']:.1f}mm | "
            f"Iter: {params['iterations']} | Wait: {params['wait_time']:.1f}s | "
            f"Samples: {params['center_samples']} | Pressure: {pressure_status}"
        )

    def reset_values(self):
        """Reset all values to defaults"""
        self.velocity_spinbox.setValue(20)
        self.acceleration_spinbox.setValue(20)
        self.z_offset_spinbox.setValue(6.0)
        self.lift_z_spinbox.setValue(200.0)
        self.rotation_step_spinbox.setValue(1.0)
        self.joint_rotation_step_spinbox.setValue(3.0)
        self.iterations_spinbox.setValue(1)
        self.wait_time_spinbox.setValue(0.0)
        self.center_samples_spinbox.setValue(5)
        self.pressure_enable_button.setChecked(True)
        self.target_force_spinbox.setValue(2.0)
        self.force_gain_spinbox.setValue(0.1)
        self.force_deadband_spinbox.setValue(0.5)
        self.max_search_distance_spinbox.setValue(15.0)
        self.search_step_size_spinbox.setValue(0.5)
        self.contact_threshold_spinbox.setValue(1.0)
        self.search_velocity_spinbox.setValue(5)
        self.search_all_corners_button.setChecked(True)
        self.update_search_corners_button_color(self.search_all_corners_button, True)
        self.rotation_adjustment_button.setChecked(True)
        self.update_rotation_adjustment_button_color(self.rotation_adjustment_button, True)
        self.max_position_adjustment_spinbox.setValue(12.0)
        self.rotation_coefficient_spinbox.setValue(0.05)
        self.max_rotation_adjustment_spinbox.setValue(2.0)
        self.enable_contour_following_checkbox.setChecked(True)
        self.contour_epsilon_spinbox.setValue(2.0)
        self.min_segment_length_spinbox.setValue(3.0)
        self.rotation_lookahead_spinbox.setValue(5)

    def get_params(self):
        """Get current parameter values as dict"""
        return {
            'velocity': self.velocity_spinbox.value(),
            'acceleration': self.acceleration_spinbox.value(),
            'z_offset': self.z_offset_spinbox.value(),
            'lift_z': self.lift_z_spinbox.value(),
            'rotation_step': self.rotation_step_spinbox.value(),
            'joint_rotation_step': self.joint_rotation_step_spinbox.value(),
            'iterations': self.iterations_spinbox.value(),
            'wait_time': self.wait_time_spinbox.value(),
            'center_samples': self.center_samples_spinbox.value(),
            'enable_pressure_adjustment': self.pressure_enable_button.isChecked(),
            'target_force_x': self.target_force_spinbox.value(),
            'force_adjustment_gain': self.force_gain_spinbox.value(),
            'force_deadband': self.force_deadband_spinbox.value(),
            'max_search_distance': self.max_search_distance_spinbox.value(),
            'search_step_size': self.search_step_size_spinbox.value(),
            'contact_threshold': self.contact_threshold_spinbox.value(),
            'search_velocity': self.search_velocity_spinbox.value(),
            'search_at_all_corners': self.search_all_corners_button.isChecked(),
            'max_position_adjustment': self.max_position_adjustment_spinbox.value(),
            'enable_rotation_adjustment': self.rotation_adjustment_button.isChecked(),
            'rotation_coefficient': self.rotation_coefficient_spinbox.value(),
            'max_rotation_adjustment': self.max_rotation_adjustment_spinbox.value(),
            'enable_contour_following': self.enable_contour_following_checkbox.isChecked(),
            'contour_simplification_epsilon': self.contour_epsilon_spinbox.value(),
            'min_segment_length': self.min_segment_length_spinbox.value(),
            'rotation_lookahead_points': self.rotation_lookahead_spinbox.value()
        }

    def set_params(self, params):
        """Set parameter values from dict"""
        if 'velocity' in params:
            self.velocity_spinbox.setValue(params['velocity'])
        if 'acceleration' in params:
            self.acceleration_spinbox.setValue(params['acceleration'])
        if 'z_offset' in params:
            self.z_offset_spinbox.setValue(params['z_offset'])
        if 'lift_z' in params:
            self.lift_z_spinbox.setValue(params['lift_z'])
        if 'rotation_step' in params:
            self.rotation_step_spinbox.setValue(params['rotation_step'])
        if 'joint_rotation_step' in params:
            self.joint_rotation_step_spinbox.setValue(params['joint_rotation_step'])
        if 'iterations' in params:
            self.iterations_spinbox.setValue(params['iterations'])
        if 'wait_time' in params:
            self.wait_time_spinbox.setValue(params['wait_time'])
        if 'center_samples' in params:
            self.center_samples_spinbox.setValue(params['center_samples'])
        if 'enable_pressure_adjustment' in params:
            self.pressure_enable_button.setChecked(params['enable_pressure_adjustment'])
            self.pressure_enable_button.setText("ENABLED" if params['enable_pressure_adjustment'] else "DISABLED")
        if 'target_force_x' in params:
            self.target_force_spinbox.setValue(params['target_force_x'])
        if 'force_adjustment_gain' in params:
            self.force_gain_spinbox.setValue(params['force_adjustment_gain'])
        if 'force_deadband' in params:
            self.force_deadband_spinbox.setValue(params['force_deadband'])
        if 'max_search_distance' in params:
            self.max_search_distance_spinbox.setValue(params['max_search_distance'])
        if 'search_step_size' in params:
            self.search_step_size_spinbox.setValue(params['search_step_size'])
        if 'contact_threshold' in params:
            self.contact_threshold_spinbox.setValue(params['contact_threshold'])
        if 'search_velocity' in params:
            self.search_velocity_spinbox.setValue(params['search_velocity'])
        if 'search_at_all_corners' in params:
            self.search_all_corners_button.setChecked(params['search_at_all_corners'])
            self.update_search_corners_button_color(self.search_all_corners_button, params['search_at_all_corners'])
        if 'max_position_adjustment' in params:
            self.max_position_adjustment_spinbox.setValue(params['max_position_adjustment'])
        if 'enable_rotation_adjustment' in params:
            self.rotation_adjustment_button.setChecked(params['enable_rotation_adjustment'])
            self.update_rotation_adjustment_button_color(self.rotation_adjustment_button, params['enable_rotation_adjustment'])
        if 'rotation_coefficient' in params:
            self.rotation_coefficient_spinbox.setValue(params['rotation_coefficient'])
        if 'max_rotation_adjustment' in params:
            self.max_rotation_adjustment_spinbox.setValue(params['max_rotation_adjustment'])
        if 'enable_contour_following' in params:
            self.enable_contour_following_checkbox.setChecked(params['enable_contour_following'])
        if 'contour_simplification_epsilon' in params:
            self.contour_epsilon_spinbox.setValue(params['contour_simplification_epsilon'])
        if 'min_segment_length' in params:
            self.min_segment_length_spinbox.setValue(params['min_segment_length'])
        if 'rotation_lookahead_points' in params:
            self.rotation_lookahead_spinbox.setValue(params['rotation_lookahead_points'])

    def _get_settings_file_path(self):
        """Get the path to the operation parameters settings file"""
        # Get the application root directory
        current_file = Path(__file__)
        app_root = current_file.parent.parent.parent  # Go up to src/
        settings_dir = app_root / "applications" / "edge_painting_application" / "storage" / "settings"
        settings_dir.mkdir(parents=True, exist_ok=True)
        return settings_dir / "operation_parameters.json"

    def save_settings(self):
        """Save current parameters to JSON file"""
        try:
            params = self.get_params()
            with open(self.settings_file, 'w') as f:
                json.dump(params, f, indent=4)
            print(f"✓ Operation parameters saved to {self.settings_file}")
        except Exception as e:
            print(f"✗ Failed to save operation parameters: {e}")

    def load_settings(self):
        """Load parameters from JSON file"""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r') as f:
                    params = json.load(f)
                self.set_params(params)
                print(f"✓ Operation parameters loaded from {self.settings_file}")
                # Emit params_changed signal after loading
                self.params_changed.emit(params)
            else:
                print(f"ℹ No saved operation parameters found, using defaults")
        except Exception as e:
            print(f"✗ Failed to load operation parameters: {e}")

    def closeEvent(self, event):
        """Save settings when dialog is closed"""
        self.save_settings()
        super().closeEvent(event)


def show_operation_params_dialog(parent=None, current_params=None):
    """Show the operation parameters dialog"""
    dialog = OperationParamsDialog(parent)
    if current_params:
        dialog.set_params(current_params)
    dialog.show()
    return dialog
