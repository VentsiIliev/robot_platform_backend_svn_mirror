from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QGroupBox, QGridLayout, QSlider, QFrame, QScrollArea, QWidget,
                             QSpinBox, QDoubleSpinBox, QComboBox)
from frontend.pl_ui.ui.windows.mainWindow.appWidgets.AppWidget import AppWidget
from modules.shared.MessageBroker import MessageBroker
from modules.shared.v1.topics import RobotTopics
class TCPCalibrationAppWidget(AppWidget):
    jog_requested = pyqtSignal(str, str, str, float)
    save_point_requested = pyqtSignal()
    clear_points_requested = pyqtSignal()
    compute_tcp_requested = pyqtSignal()
    def __init__(self, parent=None, controller=None):
        self.controller = controller
        self.broker = MessageBroker()
        self.saved_points = []
        super().__init__("TCP Calibration", parent)
    def setup_ui(self):
        # Main layout with scroll area for 1920x1080 compatibility
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        content_widget = QWidget()
        self.content_layout = QVBoxLayout(content_widget)
        self.content_layout.setContentsMargins(20, 10, 20, 10)
        self.content_layout.setSpacing(12)
        # Compact title
        title_label = QLabel("Four-Point TCP Calibration")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #333333; margin-bottom: 5px;")
        self.content_layout.addWidget(title_label)
        # Compact instructions
        instructions = QLabel("Move robot to 4 positions/orientations, save each, then compute TCP.")
        instructions.setStyleSheet("font-size: 12px; color: #666666; margin-bottom: 8px;")
        instructions.setWordWrap(True)
        self.content_layout.addWidget(instructions)
        self._create_step_slider()
        self._create_jog_controls()
        self._create_rotation_controls()
        self._create_pattern_movement_controls()
        self._create_calibration_controls()
        self.content_layout.addStretch()
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)
        self.setLayout(main_layout)
        self._connect_signals()
    def _create_step_slider(self):
        slider_group = QGroupBox("Step Size (mm)")
        slider_group.setStyleSheet("""
            QGroupBox {
                font-size: 13px;
                font-weight: 600;
                border: 2px solid #E5E5E5;
                border-radius: 6px;
                margin-top: 8px;
                padding: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        layout = QVBoxLayout()
        slider_container = QHBoxLayout()
        self.step_slider = QSlider(Qt.Orientation.Horizontal)
        self.step_slider.setMinimum(1)
        self.step_slider.setMaximum(100)
        self.step_slider.setValue(10)
        self.step_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.step_slider.setTickInterval(10)
        self.step_label = QLabel("10 mm")
        self.step_label.setStyleSheet("font-size: 16px; font-weight: 600; color: #905BA9; min-width: 80px;")
        self.step_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.step_slider.valueChanged.connect(lambda v: self.step_label.setText(f"{v} mm"))
        slider_container.addWidget(self.step_slider)
        slider_container.addWidget(self.step_label)
        layout.addLayout(slider_container)
        slider_group.setLayout(layout)
        self.content_layout.addWidget(slider_group)
    def _create_jog_controls(self):
        jog_group = QGroupBox("Position Control (X, Y, Z)")
        jog_group.setStyleSheet("""
            QGroupBox {
                font-size: 13px;
                font-weight: 600;
                border: 2px solid #E5E5E5;
                border-radius: 6px;
                margin-top: 8px;
                padding: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        layout = QHBoxLayout()
        layout.setSpacing(25)
        # Z-axis
        z_layout = QVBoxLayout()
        z_label = QLabel("Z-Axis")
        z_label.setStyleSheet("font-size: 12px; font-weight: 500; color: #666666;")
        z_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        z_layout.addWidget(z_label)
        self.btn_z_plus = self._create_jog_button("Z+", "#905BA9", "white")
        self.btn_z_minus = self._create_jog_button("Z−", "#905BA9", "white")
        z_layout.addWidget(self.btn_z_plus)
        z_layout.addSpacing(10)
        z_layout.addWidget(self.btn_z_minus)
        # X-Y axes
        xy_container = QVBoxLayout()
        xy_label = QLabel("X-Y Axes")
        xy_label.setStyleSheet("font-size: 12px; font-weight: 500; color: #666666;")
        xy_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        xy_container.addWidget(xy_label)
        xy_layout = QGridLayout()
        xy_layout.setSpacing(10)
        self.btn_x_minus = self._create_jog_button("X−", "#F5F5F5", "#666666")
        self.btn_x_plus = self._create_jog_button("X+", "#F5F5F5", "#666666")
        self.btn_y_plus = self._create_jog_button("Y+", "#F5F5F5", "#666666")
        self.btn_y_minus = self._create_jog_button("Y−", "#F5F5F5", "#666666")
        xy_layout.addWidget(self.btn_y_plus, 0, 1)
        xy_layout.addWidget(self.btn_x_minus, 1, 0)
        xy_layout.addWidget(self.btn_x_plus, 1, 2)
        xy_layout.addWidget(self.btn_y_minus, 2, 1)
        spacer = QFrame()
        spacer.setFixedSize(50, 50)
        xy_layout.addWidget(spacer, 1, 1)
        xy_container.addLayout(xy_layout)
        layout.addStretch()
        layout.addLayout(z_layout)
        layout.addSpacing(25)
        layout.addLayout(xy_container)
        layout.addStretch()
        jog_group.setLayout(layout)
        self.content_layout.addWidget(jog_group)
    def _create_rotation_controls(self):
        rot_group = QGroupBox("Orientation Control (Rx, Ry)")
        rot_group.setStyleSheet("""
            QGroupBox {
                font-size: 13px;
                font-weight: 600;
                border: 2px solid #E5E5E5;
                border-radius: 6px;
                margin-top: 8px;
                padding: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        layout = QHBoxLayout()
        layout.setSpacing(25)
        # Rx (Tilt)
        rx_layout = QVBoxLayout()
        rx_label = QLabel("Rx (Tilt)")
        rx_label.setStyleSheet("font-size: 12px; font-weight: 500; color: #666666;")
        rx_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        rx_layout.addWidget(rx_label)
        self.btn_rx_plus = self._create_jog_button("Rx+", "#4A90E2", "white")
        self.btn_rx_minus = self._create_jog_button("Rx−", "#4A90E2", "white")
        rx_layout.addWidget(self.btn_rx_plus)
        rx_layout.addSpacing(10)
        rx_layout.addWidget(self.btn_rx_minus)
        # Ry (Roll)
        ry_layout = QVBoxLayout()
        ry_label = QLabel("Ry (Roll)")
        ry_label.setStyleSheet("font-size: 12px; font-weight: 500; color: #666666;")
        ry_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ry_layout.addWidget(ry_label)
        self.btn_ry_plus = self._create_jog_button("Ry+", "#4A90E2", "white")
        self.btn_ry_minus = self._create_jog_button("Ry−", "#4A90E2", "white")
        ry_layout.addWidget(self.btn_ry_plus)
        ry_layout.addSpacing(10)
        ry_layout.addWidget(self.btn_ry_minus)
        layout.addStretch()
        layout.addLayout(rx_layout)
        layout.addSpacing(25)
        layout.addLayout(ry_layout)
        layout.addStretch()
        rot_group.setLayout(layout)
        self.content_layout.addWidget(rot_group)

    def _create_pattern_movement_controls(self):
        pattern_group = QGroupBox("Pattern Movement")
        pattern_group.setStyleSheet("""
            QGroupBox {
                font-size: 13px;
                font-weight: 600;
                border: 2px solid #E5E5E5;
                border-radius: 6px;
                margin-top: 8px;
                padding: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)

        layout = QVBoxLayout()

        shape_layout = QHBoxLayout()
        shape_label = QLabel("Shape:")
        shape_label.setStyleSheet("font-size: 12px; font-weight: 500; color: #666666;")

        self.shape_combo = QComboBox()
        self.shape_combo.addItems(["Rectangle", "Circle"])
        self.shape_combo.setStyleSheet("""
            QComboBox {
                font-size: 12px;
                padding: 5px;
                border: 1px solid #E5E5E5;
                border-radius: 4px;
                color: #333333;
                background-color: white;
            }
        """)

        orientation_label = QLabel("Orientation:")
        orientation_label.setStyleSheet("font-size: 12px; font-weight: 500; color: #666666; margin-left: 15px;")

        self.orientation_combo = QComboBox()
        self.orientation_combo.addItems(["Horizontal (XY)", "Vertical (XZ)", "Vertical (YZ)"])
        self.orientation_combo.setStyleSheet("""
            QComboBox {
                font-size: 12px;
                padding: 5px;
                border: 1px solid #E5E5E5;
                border-radius: 4px;
                color: #333333;
                background-color: white;
            }
        """)

        shape_layout.addWidget(shape_label)
        shape_layout.addWidget(self.shape_combo)
        shape_layout.addWidget(orientation_label)
        shape_layout.addWidget(self.orientation_combo)
        shape_layout.addStretch()
        layout.addLayout(shape_layout)

        params_layout = QGridLayout()
        params_layout.setSpacing(10)

        width_label = QLabel("Width (mm):")
        width_label.setStyleSheet("font-size: 12px; font-weight: 500; color: #666666;")
        self.width_input = QDoubleSpinBox()
        self.width_input.setRange(1.0, 1000.0)
        self.width_input.setValue(100.0)
        self.width_input.setDecimals(1)
        self.width_input.setStyleSheet("""
            QDoubleSpinBox {
                font-size: 12px;
                padding: 5px;
                border: 1px solid #E5E5E5;
                border-radius: 4px;
                color: #333333;
                background-color: white;
            }
        """)

        height_label = QLabel("Height (mm):")
        height_label.setStyleSheet("font-size: 12px; font-weight: 500; color: #666666;")
        self.height_input = QDoubleSpinBox()
        self.height_input.setRange(1.0, 1000.0)
        self.height_input.setValue(100.0)
        self.height_input.setDecimals(1)
        self.height_input.setStyleSheet("""
            QDoubleSpinBox {
                font-size: 12px;
                padding: 5px;
                border: 1px solid #E5E5E5;
                border-radius: 4px;
                color: #333333;
                background-color: white;
            }
        """)

        points_label = QLabel("Number of Points:")
        points_label.setStyleSheet("font-size: 12px; font-weight: 500; color: #666666;")
        self.points_input = QSpinBox()
        self.points_input.setRange(4, 1000)
        self.points_input.setValue(20)
        self.points_input.setStyleSheet("""
            QSpinBox {
                font-size: 12px;
                padding: 5px;
                border: 1px solid #E5E5E5;
                border-radius: 4px;
                color: #333333;
                background-color: white;
            }
        """)

        repetitions_label = QLabel("Repetitions:")
        repetitions_label.setStyleSheet("font-size: 12px; font-weight: 500; color: #666666;")
        self.repetitions_input = QSpinBox()
        self.repetitions_input.setRange(1, 100)
        self.repetitions_input.setValue(1)
        self.repetitions_input.setStyleSheet("""
            QSpinBox {
                font-size: 12px;
                padding: 5px;
                border: 1px solid #E5E5E5;
                border-radius: 4px;
                color: #333333;
                background-color: white;
            }
        """)

        velocity_label = QLabel("Velocity (%):")
        velocity_label.setStyleSheet("font-size: 12px; font-weight: 500; color: #666666;")
        self.velocity_input = QSpinBox()
        self.velocity_input.setRange(1, 100)
        self.velocity_input.setValue(50)
        self.velocity_input.setStyleSheet("""
            QSpinBox {
                font-size: 12px;
                padding: 5px;
                border: 1px solid #E5E5E5;
                border-radius: 4px;
                color: #333333;
                background-color: white;
            }
        """)

        acceleration_label = QLabel("Acceleration (%):")
        acceleration_label.setStyleSheet("font-size: 12px; font-weight: 500; color: #666666;")
        self.acceleration_input = QSpinBox()
        self.acceleration_input.setRange(1, 100)
        self.acceleration_input.setValue(50)
        self.acceleration_input.setStyleSheet("""
            QSpinBox {
                font-size: 12px;
                padding: 5px;
                border: 1px solid #E5E5E5;
                border-radius: 4px;
                color: #333333;
                background-color: white;
            }
        """)

        params_layout.addWidget(width_label, 0, 0)
        params_layout.addWidget(self.width_input, 0, 1)
        params_layout.addWidget(height_label, 0, 2)
        params_layout.addWidget(self.height_input, 0, 3)
        params_layout.addWidget(points_label, 1, 0)
        params_layout.addWidget(self.points_input, 1, 1)
        params_layout.addWidget(repetitions_label, 1, 2)
        params_layout.addWidget(self.repetitions_input, 1, 3)
        params_layout.addWidget(velocity_label, 2, 0)
        params_layout.addWidget(self.velocity_input, 2, 1)
        params_layout.addWidget(acceleration_label, 2, 2)
        params_layout.addWidget(self.acceleration_input, 2, 3)

        layout.addLayout(params_layout)

        self.draw_pattern_btn = QPushButton("Draw Pattern")
        self.draw_pattern_btn.setStyleSheet(self._get_button_style("#FF8C00"))
        self.draw_pattern_btn.setMinimumHeight(40)
        self.draw_pattern_btn.clicked.connect(self._draw_pattern)

        layout.addWidget(self.draw_pattern_btn)

        pattern_group.setLayout(layout)
        self.content_layout.addWidget(pattern_group)

    def _create_calibration_controls(self):
        cal_group = QGroupBox("Calibration")
        cal_group.setStyleSheet("""
            QGroupBox {
                font-size: 13px;
                font-weight: 600;
                border: 2px solid #E5E5E5;
                border-radius: 6px;
                margin-top: 8px;
                padding: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        layout = QVBoxLayout()
        self.points_label = QLabel("Saved Points: 0/4")
        self.points_label.setStyleSheet("font-size: 14px; font-weight: 600; color: #333333; margin-bottom: 8px;")
        layout.addWidget(self.points_label)
        self.points_list_label = QLabel("No points saved yet")
        self.points_list_label.setStyleSheet("""
            font-size: 12px; 
            color: #666666; 
            background-color: #F8F9FA;
            border: 1px solid #E5E5E5;
            border-radius: 4px;
            padding: 8px;
            margin-bottom: 10px;
        """)
        self.points_list_label.setWordWrap(True)
        self.points_list_label.setMinimumHeight(50)
        layout.addWidget(self.points_list_label)
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        self.save_btn = QPushButton("Save Point")
        self.save_btn.setStyleSheet(self._get_button_style("#28A745"))
        self.save_btn.setMinimumHeight(40)
        self.clear_btn = QPushButton("Clear All")
        self.clear_btn.setStyleSheet(self._get_button_style("#DC3545"))
        self.clear_btn.setMinimumHeight(40)
        self.compute_btn = QPushButton("Compute TCP")
        self.compute_btn.setStyleSheet(self._get_button_style("#905BA9"))
        self.compute_btn.setMinimumHeight(40)
        self.compute_btn.setEnabled(False)
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.clear_btn)
        button_layout.addWidget(self.compute_btn)
        layout.addLayout(button_layout)
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("font-size: 12px; color: #666666; margin-top: 8px;")
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)
        cal_group.setLayout(layout)
        self.content_layout.addWidget(cal_group)
    def _create_jog_button(self, text, bg_color, text_color):
        btn = QPushButton(text)
        btn.setFixedSize(70, 70)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg_color};
                color: {text_color};
                border: none;
                border-radius: 6px;
                font-size: 16px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                opacity: 0.9;
            }}
            QPushButton:pressed {{
                background-color: {self._darken_color(bg_color)};
            }}
        """)
        return btn
    def _get_button_style(self, color):
        return f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 13px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {self._darken_color(color)};
            }}
            QPushButton:pressed {{
                background-color: {self._darken_color(color, 0.2)};
            }}
            QPushButton:disabled {{
                background-color: #CCCCCC;
                color: #888888;
            }}
        """
    def _darken_color(self, hex_color, factor=0.1):
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r = int(r * (1 - factor))
        g = int(g * (1 - factor))
        b = int(b * (1 - factor))
        return f'#{r:02x}{g:02x}{b:02x}'
    def _connect_signals(self):
        self.btn_x_plus.clicked.connect(lambda: self._jog("X", "+"))
        self.btn_x_minus.clicked.connect(lambda: self._jog("X", "-"))
        self.btn_y_plus.clicked.connect(lambda: self._jog("Y", "+"))
        self.btn_y_minus.clicked.connect(lambda: self._jog("Y", "-"))
        self.btn_z_plus.clicked.connect(lambda: self._jog("Z", "+"))
        self.btn_z_minus.clicked.connect(lambda: self._jog("Z", "-"))
        self.btn_rx_plus.clicked.connect(lambda: self._jog("Rx", "+"))
        self.btn_rx_minus.clicked.connect(lambda: self._jog("Rx", "-"))
        self.btn_ry_plus.clicked.connect(lambda: self._jog("Ry", "+"))
        self.btn_ry_minus.clicked.connect(lambda: self._jog("Ry", "-"))
        self.save_btn.clicked.connect(self._save_point)
        self.clear_btn.clicked.connect(self._clear_points)
        self.compute_btn.clicked.connect(self._compute_tcp)
        self.broker.subscribe(RobotTopics.TCP_CALIBRATION_STATUS, self._on_status_update)
        self.broker.subscribe(RobotTopics.TCP_CALIBRATION_RESULT, self._on_result)
    def _jog(self, axis, direction):
        step_value = self.step_slider.value()
        self.jog_requested.emit("MoveJ", axis, direction, step_value)
        if self.controller:
            self.controller.handleJog(axis, direction, step_value)

    def _draw_pattern(self):
        shape = self.shape_combo.currentText()
        width = self.width_input.value()
        height = self.height_input.value()
        num_points = self.points_input.value()
        orientation = self.orientation_combo.currentText()
        repetitions = self.repetitions_input.value()
        velocity = self.velocity_input.value()
        acceleration = self.acceleration_input.value()

        if self.controller:
            if shape == "Rectangle":
                self.controller.handleDrawRectangle(width, height, num_points, orientation, repetitions, velocity, acceleration)
            else:
                self.controller.handleDrawCircle(width, height, num_points, orientation, repetitions, velocity, acceleration)

        self.broker.publish(RobotTopics.TCP_CALIBRATION_STATUS, {
            "message": f"Drawing {shape.lower()} pattern ({orientation}) {repetitions}x at {velocity}% vel, {acceleration}% acc..."
        })

    def _save_point(self):
        if len(self.saved_points) < 4:
            self.saved_points.append(len(self.saved_points) + 1)
            self._update_points_display()
            self.broker.publish(RobotTopics.TCP_CALIBRATION_SAVE_POINT, {
                "point_number": len(self.saved_points)
            })
            self.status_label.setText(f"Point {len(self.saved_points)} saved successfully")
    def _clear_points(self):
        self.saved_points.clear()
        self._update_points_display()
        self.broker.publish(RobotTopics.TCP_CALIBRATION_CLEAR_POINTS, {})
        self.status_label.setText("All points cleared")
    def _compute_tcp(self):
        if len(self.saved_points) == 4:
            self.broker.publish(RobotTopics.TCP_CALIBRATION_COMPUTE, {})
            self.status_label.setText("Computing TCP offset...")
            self.compute_btn.setEnabled(False)
    def _update_points_display(self):
        count = len(self.saved_points)
        self.points_label.setText(f"Saved Points: {count}/4")
        self.compute_btn.setEnabled(count == 4)
        self.save_btn.setEnabled(count < 4)
        if count == 0:
            self.points_list_label.setText("No points saved yet")
        else:
            points_text = "\n".join([f"✓ Point {i}" for i in self.saved_points])
            self.points_list_label.setText(points_text)
    def _on_status_update(self, message):
        if isinstance(message, dict):
            self.status_label.setText(message.get("message", ""))
            self.status_label.setStyleSheet("font-size: 12px; color: #666666; margin-top: 8px;")
    def _on_result(self, message):
        if isinstance(message, dict):
            success = message.get("success", False)
            if success:
                self.status_label.setText("✓ TCP calibration completed successfully!")
                self.status_label.setStyleSheet("font-size: 12px; color: #28A745; margin-top: 8px; font-weight: 600;")
            else:
                error = message.get("error", "Unknown error")
                self.status_label.setText(f"✗ Calibration failed: {error}")
                self.status_label.setStyleSheet("font-size: 12px; color: #DC3545; margin-top: 8px; font-weight: 600;")
            self.compute_btn.setEnabled(len(self.saved_points) == 4)
