import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray
from sensor_msgs.msg import JointState
from moveit_msgs.srv import GetPositionIK, GetPositionFK, GetCartesianPath
from geometry_msgs.msg import Pose
from std_srvs.srv import Empty
import threading
import math
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QPushButton, QLineEdit
)
from PyQt5.QtCore import Qt, pyqtSignal, QObject

JOINT_NAMES = ['Joint_1', 'Joint_2', 'Joint_3', 'Joint_4', 'Joint_5', 'Joint_6']
EE_LINK = 'tool0'


class ROS2Bridge(Node, QObject):
    joint_state_signal = pyqtSignal(dict)
    cartesian_signal = pyqtSignal(float, float, float, float, float, float)
    status_signal = pyqtSignal(str)
    joint_positions_signal = pyqtSignal(list)

    def __init__(self, gui):
        Node.__init__(self, 'ros2_gui_bridge')
        QObject.__init__(self)
        self.gui = gui
        self.pub = self.create_publisher(Float64MultiArray, '/gui_joint_command', 10)
        self.sub = self.create_subscription(JointState, '/gui_joint_states', self.joint_state_cb, 10)
        self.ik_client = self.create_client(GetPositionIK, '/compute_ik')
        self.fk_client = self.create_client(GetPositionFK, '/compute_fk')
        self.cartesian_path_client = self.create_client(GetCartesianPath, '/compute_cartesian_path')
        self.cartesian_pub = self.create_publisher(Pose, '/gui_cartesian_command', 10)
        self.current_joint_state = None
        self.received_first_joint_state = False  # Block commands until true

        # Connect signals to GUI slots
        self.joint_state_signal.connect(self.gui.update_joint_states)
        self.cartesian_signal.connect(self.gui.set_cartesian_position)
        self.status_signal.connect(self.gui.show_status)
        self.joint_positions_signal.connect(self.gui.set_joint_positions)

    def send_joint_command(self, positions):
        if not self.received_first_joint_state:
            self.status_signal.emit("Waiting for real robot state...")
            return
        msg = Float64MultiArray()
        msg.data = positions
        self.pub.publish(msg)

    def joint_state_cb(self, msg):
        self.current_joint_state = msg
        pos_dict = dict(zip(msg.name, msg.position))
        self.joint_state_signal.emit(pos_dict)
        self.get_cartesian_position(msg)
        if not self.received_first_joint_state:
            self.received_first_joint_state = True
            # On first joint state, update GUI fields to match robot
            self.gui.set_joint_positions(list(msg.position))
            # FK will update Cartesian fields
            self.status_signal.emit("Robot state synchronized.")

    def get_cartesian_position(self, joint_state_msg):
        if not self.fk_client.wait_for_service(timeout_sec=0.5):
            return
        req = GetPositionFK.Request()
        req.header.frame_id = 'base_link'
        req.fk_link_names = [EE_LINK]
        req.robot_state.joint_state = joint_state_msg
        future = self.fk_client.call_async(req)
        future.add_done_callback(self.handle_fk_response)

    def rpy_to_quaternion(self, roll, pitch, yaw):
        cy = math.cos(yaw * 0.5)
        sy = math.sin(yaw * 0.5)
        cp = math.cos(pitch * 0.5)
        sp = math.sin(pitch * 0.5)
        cr = math.cos(roll * 0.5)
        sr = math.sin(roll * 0.5)
        qw = cr * cp * cy + sr * sp * sy
        qx = sr * cp * cy - cr * sp * sy
        qy = cr * sp * cy + sr * cp * cy
        qz = cr * cp * sy - sr * sp * cy
        return qx, qy, qz, qw

    def quaternion_to_rpy(self, qx, qy, qz, qw):
        sinr_cosp = 2 * (qw * qx + qy * qz)
        cosr_cosp = 1 - 2 * (qx * qx + qy * qy)
        roll = math.atan2(sinr_cosp, cosr_cosp)

        sinp = 2 * (qw * qy - qz * qx)
        pitch = math.asin(sinp) if abs(sinp) <= 1 else math.copysign(math.pi / 2, sinp)

        siny_cosp = 2 * (qw * qz + qx * qy)
        cosy_cosp = 1 - 2 * (qy * qy + qz * qz)
        yaw = math.atan2(siny_cosp, cosy_cosp)
        return roll, pitch, yaw

    def compute_ik(self, x, y, z, rx=0, ry=0, rz=0):
        if not self.received_first_joint_state:
            self.status_signal.emit("Waiting for real robot state...")
            return

        if self.current_joint_state is None:
            self.gui.show_status("No joint state received yet.")
            return

        try:
            x = float(x)
            y = float(y)
            z = float(z)
            rx = math.radians(float(rx))  # assume degrees from GUI
            ry = math.radians(float(ry))
            rz = math.radians(float(rz))
        except ValueError:
            self.gui.show_status("Invalid XYZ/rXrYrZ input")
            return

        if z < 0.4:
            self.gui.show_status("Z below safe limit (400mm), command blocked")
            return

        if not self.ik_client.wait_for_service(timeout_sec=2.0):
            self.gui.show_status("IK service not available")
            return

        qx, qy, qz, qw = self.rpy_to_quaternion(rx, ry, rz)
        req = GetPositionIK.Request()
        req.ik_request.group_name = 'manipulator'
        req.ik_request.ik_link_name = EE_LINK
        req.ik_request.pose_stamped.header.frame_id = 'base_link'
        req.ik_request.pose_stamped.pose.position.x = x
        req.ik_request.pose_stamped.pose.position.y = y
        req.ik_request.pose_stamped.pose.position.z = z
        req.ik_request.pose_stamped.pose.orientation.x = qx
        req.ik_request.pose_stamped.pose.orientation.y = qy
        req.ik_request.pose_stamped.pose.orientation.z = qz
        req.ik_request.pose_stamped.pose.orientation.w = qw
        req.ik_request.robot_state.joint_state = self.current_joint_state  # seed state

        future = self.ik_client.call_async(req)
        future.add_done_callback(self.handle_ik_response)

    def handle_ik_response(self, future):
        result = future.result()
        if result and result.error_code.val == 1:
            positions = result.solution.joint_state.position
            # FIX: Convert array.array to list before emitting
            self.joint_positions_signal.emit(list(positions))
            self.send_joint_command(list(positions))
            self.status_signal.emit("IK success")
        else:
            self.status_signal.emit("IK failed")

    def handle_fk_response(self, future):
        result = future.result()
        if result and result.pose_stamped:
            pose = result.pose_stamped[0].pose
            x, y, z = pose.position.x, pose.position.y, pose.position.z
            qx, qy, qz, qw = pose.orientation.x, pose.orientation.y, pose.orientation.z, pose.orientation.w
            roll, pitch, yaw = self.quaternion_to_rpy(qx, qy, qz, qw)
            self.cartesian_signal.emit(x, y, z, roll, pitch, yaw)

    def send_xyz_only(self, x, y, z):
        if not self.received_first_joint_state:
            self.status_signal.emit("Waiting for real robot state...")
            return
        # Block unreachable Z
        if z < 0.4 or z > 0.8:
            self.gui.show_status("Z outside workspace, command blocked")
            return
        pose = Pose()
        pose.position.x = float(x)
        pose.position.y = float(y)
        pose.position.z = float(z)
        # Preserve current orientation for XYZ jogs
        pose.orientation.x = self.gui.live_qx if hasattr(self.gui, 'live_qx') else 0.0
        pose.orientation.y = self.gui.live_qy if hasattr(self.gui, 'live_qy') else 0.0
        pose.orientation.z = self.gui.live_qz if hasattr(self.gui, 'live_qz') else 0.0
        pose.orientation.w = self.gui.live_qw if hasattr(self.gui, 'live_qw') else 1.0

        # Use Cartesian path planning by default
        if not self.cartesian_path_client.wait_for_service(timeout_sec=2.0):
            self.gui.show_status("Cartesian path service not available, falling back to IK")
            # Pass current rotation to IK as well
            rx = math.degrees(self.gui.live_rx) if hasattr(self.gui, 'live_rx') else 0
            ry = math.degrees(self.gui.live_ry) if hasattr(self.gui, 'live_ry') else 0
            rz = math.degrees(self.gui.live_rz) if hasattr(self.gui, 'live_rz') else 0
            self.compute_ik(x, y, z, rx, ry, rz)
            return

        from moveit_msgs.msg import RobotState
        cartesian_req = GetCartesianPath.Request()
        cartesian_req.header.frame_id = 'base_link'
        cartesian_req.group_name = 'manipulator'
        cartesian_req.link_name = EE_LINK
        # Use current joint state as seed for Cartesian path
        if self.current_joint_state:
            cartesian_req.start_state.joint_state = self.current_joint_state
        else:
            cartesian_req.start_state.joint_state.name = JOINT_NAMES
            cartesian_req.start_state.joint_state.position = [0.0] * len(JOINT_NAMES)
        cartesian_req.waypoints = [pose]
        cartesian_req.max_step = 0.005  # Finer steps for linearity
        cartesian_req.jump_threshold = 0.0  # No joint jumps
        cartesian_req.avoid_collisions = False  # Pure linear path, set True if needed

        # Add logging for diagnostics
        print(f"Requesting Cartesian path to: x={x}, y={y}, z={z} (preserving orientation)")

        future = self.cartesian_path_client.call_async(cartesian_req)
        future.add_done_callback(self.handle_cartesian_path_response)

    def handle_cartesian_path_response(self, future):
        result = future.result()
        if result:
            print(f"Cartesian path fraction: {result.fraction}")
            if result.solution.joint_trajectory.points:
                print(f"Trajectory points: {len(result.solution.joint_trajectory.points)}")
                positions = result.solution.joint_trajectory.points[-1].positions
                # FIX: Convert array.array to list before emitting
                self.joint_positions_signal.emit(list(positions))
                self.send_joint_command(list(positions))
                if result.fraction > 0.99:
                    self.status_signal.emit("Cartesian path success")
                else:
                    self.status_signal.emit("Cartesian path incomplete, fraction={:.2f}".format(result.fraction))
            else:
                self.status_signal.emit("No valid trajectory from Cartesian path")
        else:
            self.status_signal.emit("Cartesian path failed")

    def send_xyz_home(self):
        # X=0, Y=147.3, Z=681 mm -> meters
        self.send_xyz_only(0.0, 0.1473, 0.679)

    def send_rotation_only(self, rx_deg, ry_deg, rz_deg, x=None, y=None, z=None):
        if not self.received_first_joint_state:
            self.status_signal.emit("Waiting for real robot state...")
            return
        # Use current live XYZ if not provided
        if x is None or y is None or z is None:
            x = self.gui.live_x
            y = self.gui.live_y
            z = self.gui.live_z
        pose = Pose()
        pose.position.x = float(x)
        pose.position.y = float(y)
        pose.position.z = float(z)
        rx = math.radians(float(rx_deg))
        ry = math.radians(float(ry_deg))
        rz = math.radians(float(rz_deg))
        qx, qy, qz, qw = self.rpy_to_quaternion(rx, ry, rz)
        pose.orientation.x = qx
        pose.orientation.y = qy
        pose.orientation.z = qz
        pose.orientation.w = qw

        # Use Cartesian path planner for rotation jogs
        if not self.cartesian_path_client.wait_for_service(timeout_sec=2.0):
            self.gui.show_status("Cartesian path service not available, falling back to IK")
            self.compute_ik(x, y, z, rx_deg, ry_deg, rz_deg)
            return

        from moveit_msgs.msg import RobotState
        cartesian_req = GetCartesianPath.Request()
        cartesian_req.header.frame_id = 'base_link'
        cartesian_req.group_name = 'manipulator'
        cartesian_req.link_name = EE_LINK
        # Use current joint state as seed for Cartesian path
        if self.current_joint_state:
            cartesian_req.start_state.joint_state = self.current_joint_state
        else:
            cartesian_req.start_state.joint_state.name = JOINT_NAMES
            cartesian_req.start_state.joint_state.position = [0.0] * len(JOINT_NAMES)
        cartesian_req.waypoints = [pose]
        cartesian_req.max_step = 0.005  # Finer steps for linearity
        cartesian_req.jump_threshold = 0.0  # No joint jumps
        cartesian_req.avoid_collisions = False  # Pure linear path, set True if needed

        # Add logging for diagnostics
        print(f"Requesting Cartesian path to: x={x}, y={y}, z={z}, rx={rx_deg}, ry={ry_deg}, rz={rz_deg}")

        future = self.cartesian_path_client.call_async(cartesian_req)
        future.add_done_callback(self.handle_cartesian_path_response)

    def set_joint_positions(self, positions):
        # FIX: Convert array.array to list before emitting
        self.joint_positions_signal.emit(list(positions))


class RobotGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Robot Joint Control (Qt)")
        self.live_x = 0.0
        self.live_y = 0.0
        self.live_z = 0.0
        self.live_rx = 0.0
        self.live_ry = 0.0
        self.live_rz = 0.0
        self.entries_initialized = False

        layout = QVBoxLayout()
        self.sliders = []
        self.state_labels = []
        self.velocity_labels = []
        self.accel_labels = []
        self.jog_buttons = []

        for i, name in enumerate(JOINT_NAMES):
            h = QHBoxLayout()
            h.addWidget(QLabel(name))
            slider = QSlider(Qt.Horizontal)
            slider.setMinimum(-100)
            slider.setMaximum(100)
            slider.setValue(0)
            slider.setSingleStep(1)
            h.addWidget(slider)
            self.sliders.append(slider)
            state_label = QLabel("Pos: 0.0")
            h.addWidget(state_label)
            self.state_labels.append(state_label)
            vel_label = QLabel("Vel: 0.0")
            h.addWidget(vel_label)
            self.velocity_labels.append(vel_label)
            accel_label = QLabel("Acc: 0.0")
            h.addWidget(accel_label)
            self.accel_labels.append(accel_label)
            # Add jog -/+ buttons
            jog_minus = QPushButton("-")
            jog_plus = QPushButton("+")
            jog_minus.clicked.connect(lambda checked, idx=i: self.jog_joint(idx, -1))
            jog_plus.clicked.connect(lambda checked, idx=i: self.jog_joint(idx, 1))
            h.addWidget(jog_minus)
            h.addWidget(jog_plus)
            self.jog_buttons.append((jog_minus, jog_plus))
            layout.addLayout(h)

        # Cartesian jog buttons
        cartesian_jog_layout = QHBoxLayout()
        cartesian_jog_layout.addWidget(QLabel("Cartesian Jog:"))
        # X-
        jog_x_minus = QPushButton("X-")
        jog_x_minus.clicked.connect(lambda: self.jog_cartesian('x', -1))
        cartesian_jog_layout.addWidget(jog_x_minus)
        # X+
        jog_x_plus = QPushButton("X+")
        jog_x_plus.clicked.connect(lambda: self.jog_cartesian('x', 1))
        cartesian_jog_layout.addWidget(jog_x_plus)
        # Y-
        jog_y_minus = QPushButton("Y-")
        jog_y_minus.clicked.connect(lambda: self.jog_cartesian('y', -1))
        cartesian_jog_layout.addWidget(jog_y_minus)
        # Y+
        jog_y_plus = QPushButton("Y+")
        jog_y_plus.clicked.connect(lambda: self.jog_cartesian('y', 1))
        cartesian_jog_layout.addWidget(jog_y_plus)
        # Z-
        jog_z_minus = QPushButton("Z-")
        jog_z_minus.clicked.connect(lambda: self.jog_cartesian('z', -1))
        cartesian_jog_layout.addWidget(jog_z_minus)
        # Z+
        jog_z_plus = QPushButton("Z+")
        jog_z_plus.clicked.connect(lambda: self.jog_cartesian('z', 1))
        cartesian_jog_layout.addWidget(jog_z_plus)
        layout.addLayout(cartesian_jog_layout)

        # Rotation jog buttons
        rot_jog_layout = QHBoxLayout()
        rot_jog_layout.addWidget(QLabel("Rotation Jog:"))
        jog_rx_minus = QPushButton("rX-")
        jog_rx_minus.clicked.connect(lambda: self.jog_rotation('rx', -1))
        rot_jog_layout.addWidget(jog_rx_minus)
        jog_rx_plus = QPushButton("rX+")
        jog_rx_plus.clicked.connect(lambda: self.jog_rotation('rx', 1))
        rot_jog_layout.addWidget(jog_rx_plus)
        jog_ry_minus = QPushButton("rY-")
        jog_ry_minus.clicked.connect(lambda: self.jog_rotation('ry', -1))
        rot_jog_layout.addWidget(jog_ry_minus)
        jog_ry_plus = QPushButton("rY+")
        jog_ry_plus.clicked.connect(lambda: self.jog_rotation('ry', 1))
        rot_jog_layout.addWidget(jog_ry_plus)
        jog_rz_minus = QPushButton("rZ-")
        jog_rz_minus.clicked.connect(lambda: self.jog_rotation('rz', -1))
        rot_jog_layout.addWidget(jog_rz_minus)
        jog_rz_plus = QPushButton("rZ+")
        jog_rz_plus.clicked.connect(lambda: self.jog_rotation('rz', 1))
        rot_jog_layout.addWidget(jog_rz_plus)
        layout.addLayout(rot_jog_layout)

        # Separate jog step input for rotation
        self.jog_rot_step_entry = QLineEdit()
        self.jog_rot_step_entry.setText("1.0")
        layout.addWidget(QLabel("Rotation Jog Step (deg)"))
        layout.addWidget(self.jog_rot_step_entry)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(QPushButton("Reset Joints to 0", clicked=self.reset_joints))
        btn_layout.addWidget(QPushButton("Send", clicked=self.send_command))
        layout.addLayout(btn_layout)

        self.entries = []
        entry_labels = ["X (mm)", "Y (mm)", "Z (mm)", "rX (deg)", "rY (deg)", "rZ (deg)"]
        for label in entry_labels:
            h = QHBoxLayout()
            h.addWidget(QLabel(label))
            entry = QLineEdit()
            h.addWidget(entry)
            self.entries.append(entry)
            layout.addLayout(h)

        self.jog_step_entry = QLineEdit()
        self.jog_step_entry.setText("1.0")
        layout.addWidget(QLabel("Jog Step (mm/deg)"))
        layout.addWidget(self.jog_step_entry)

        self.live_xyz_label = QLabel("Live XYZ: x=0.000 y=0.000 z=0.000 | rX=0.000 rY=0.000 rZ=0.000")
        layout.addWidget(self.live_xyz_label)

        btn2_layout = QHBoxLayout()
        btn2_layout.addWidget(QPushButton("Move Cartesian", clicked=self.move_cartesian))
        btn2_layout.addWidget(QPushButton("Move to XYZ Only", clicked=self.move_xyz_only))
        btn2_layout.addWidget(QPushButton("Move to XYZ Home", clicked=self.move_xyz_home))
        btn2_layout.addWidget(QPushButton("Move Rotation Only", clicked=self.move_rotation_only))
        layout.addLayout(btn2_layout)

        self.status_label = QLabel("")
        layout.addWidget(self.status_label)

        self.setLayout(layout)

    def send_command(self):
        positions = [slider.value() / 100.0 for slider in self.sliders]
        self.ros_bridge.send_joint_command(positions)

    def reset_joints(self):
        zero_positions = [0.0] * len(self.sliders)
        for slider in self.sliders:
            slider.setValue(0)
        self.ros_bridge.send_joint_command(zero_positions)
        self.show_status("Joints reset to zero and command sent")

    def move_cartesian(self):
        try:
            x_mm = float(self.entries[0].text())
            y_mm = float(self.entries[1].text())
            z_mm = float(self.entries[2].text())
            rx_deg = float(self.entries[3].text())
            ry_deg = float(self.entries[4].text())
            rz_deg = float(self.entries[5].text())
        except ValueError:
            self.show_status("Invalid XYZ/rXrYrZ input")
            return
        self.ros_bridge.compute_ik(x_mm/1000.0, y_mm/1000.0, z_mm/1000.0, rx_deg, ry_deg, rz_deg)

    def update_joint_states(self, pos_dict):
        joint_state = self.ros_bridge.current_joint_state
        velocities = joint_state.velocity if joint_state and hasattr(joint_state, 'velocity') else [0.0]*len(JOINT_NAMES)
        accels = joint_state.effort if joint_state and hasattr(joint_state, 'effort') else [0.0]*len(JOINT_NAMES)
        for i, name in enumerate(JOINT_NAMES):
            pos = pos_dict.get(name, 0.0)
            self.state_labels[i].setText(f"Pos: {pos:.3f}")
            vel = velocities[i] if i < len(velocities) else 0.0
            self.velocity_labels[i].setText(f"Vel: {vel:.3f}")
            acc = accels[i] if i < len(accels) else 0.0
            self.accel_labels[i].setText(f"Acc: {acc:.3f}")

    def jog_joint(self, idx, direction):
        try:
            step = float(self.jog_step_entry.text())
        except ValueError:
            step = 1.0
        # Convert step to slider units (assuming 100 units = 1 radian)
        slider_step = int(step * direction)
        current_value = self.sliders[idx].value()
        new_value = current_value + slider_step
        self.sliders[idx].setValue(new_value)
        self.send_command()

    def jog_cartesian(self, axis, direction):
        try:
            step = float(self.jog_step_entry.text()) / 1000.0  # mm to meters
        except ValueError:
            step = 0.001  # default 1mm
        # Get current XYZ from entries
        try:
            x = float(self.entries[0].text()) / 1000.0
            y = float(self.entries[1].text()) / 1000.0
            z = float(self.entries[2].text()) / 1000.0
        except ValueError:
            x, y, z = self.live_x, self.live_y, self.live_z
        # Apply jog
        if axis == 'x':
            x += direction * step
        elif axis == 'y':
            y += direction * step
        elif axis == 'z':
            z += direction * step
        # Update entries and send command
        self.entries[0].setText(f"{x * 1000:.3f}")
        self.entries[1].setText(f"{y * 1000:.3f}")
        self.entries[2].setText(f"{z * 1000:.3f}")
        self.move_xyz_only()

    def jog_rotation(self, axis, direction):
        try:
            step = float(self.jog_rot_step_entry.text())  # degrees
        except ValueError:
            step = 1.0  # default 1 degree
        # Always jog from current live rotation coordinates
        rx = math.degrees(self.live_rx)
        ry = math.degrees(self.live_ry)
        rz = math.degrees(self.live_rz)
        # Apply jog
        if axis == 'rx':
            rx += direction * step
        elif axis == 'ry':
            ry += direction * step
        elif axis == 'rz':
            rz += direction * step
        # Update entries
        self.entries[3].setText(f"{rx:.3f}")
        self.entries[4].setText(f"{ry:.3f}")
        self.entries[5].setText(f"{rz:.3f}")
        # Call linear rotation jog via Cartesian path planner
        if self.ros_bridge:
            self.ros_bridge.send_rotation_only(rx, ry, rz)
        else:
            self.show_status("ROS bridge not initialized")

    def move_rotation_only(self):
        try:
            rx_deg = float(self.entries[3].text())
            ry_deg = float(self.entries[4].text())
            rz_deg = float(self.entries[5].text())
        except ValueError:
            self.show_status("Invalid rotation input")
            return
        if self.ros_bridge:
            self.ros_bridge.send_rotation_only(rx_deg, ry_deg, rz_deg)
        else:
            self.show_status("ROS bridge not initialized")

    def set_joint_positions(self, positions):
        for i, slider in enumerate(self.sliders):
            if i < len(positions):
                slider.setValue(int(positions[i] * 100))

    def set_cartesian_position(self, x, y, z, rx, ry, rz):
        self.live_x = x
        self.live_y = y
        self.live_z = z
        self.live_rx = rx
        self.live_ry = ry
        self.live_rz = rz
        # Store quaternion for current orientation (for XYZ jogs)
        qx, qy, qz, qw = self.ros_bridge.rpy_to_quaternion(rx, ry, rz)
        self.live_qx = qx
        self.live_qy = qy
        self.live_qz = qz
        self.live_qw = qw
        if not self.entries_initialized:
            self.entries[0].setText(f"{x * 1000:.3f}")
            self.entries[1].setText(f"{y * 1000:.3f}")
            self.entries[2].setText(f"{z * 1000:.3f}")
            self.entries[3].setText(f"{math.degrees(rx):.3f}")
            self.entries[4].setText(f"{math.degrees(ry):.3f}")
            self.entries[5].setText(f"{math.degrees(rz):.3f}")
            self.entries_initialized = True
        self.live_xyz_label.setText(
            f"Live XYZ: x={x * 1000:.3f} y={y * 1000:.3f} z={z * 1000:.3f} | "
            f"rX={math.degrees(rx):.3f} rY={math.degrees(ry):.3f} rZ={math.degrees(rz):.3f}"
        )

    def show_status(self, msg):
        self.status_label.setText(msg)

    def move_xyz_only(self):
        try:
            x_mm = float(self.entries[0].text())
            y_mm = float(self.entries[1].text())
            z_mm = float(self.entries[2].text())
        except ValueError:
            self.show_status("Invalid XYZ input")
            return
        if self.ros_bridge:
            self.ros_bridge.send_xyz_only(x_mm/1000.0, y_mm/1000.0, z_mm/1000.0)
        else:
            self.show_status("ROS bridge not initialized")

    def move_xyz_home(self):
        if self.ros_bridge:
            self.ros_bridge.send_xyz_home()
        else:
            self.show_status("ROS bridge not initialized")

    def move_rotation_only(self):
        try:
            rx_deg = float(self.entries[3].text())
            ry_deg = float(self.entries[4].text())
            rz_deg = float(self.entries[5].text())
        except ValueError:
            self.show_status("Invalid rotation input")
            return
        if self.ros_bridge:
            self.ros_bridge.send_rotation_only(rx_deg, ry_deg, rz_deg)
        else:
            self.show_status("ROS bridge not initialized")


def main():
    rclpy.init()
    app = QApplication(sys.argv)
    gui = RobotGUI()
    ros_bridge = ROS2Bridge(gui)
    gui.ros_bridge = ros_bridge

    # Start ROS2 spinning in a separate thread
    ros_thread = threading.Thread(target=rclpy.spin, args=(ros_bridge,), daemon=True)
    ros_thread.start()

    # No automatic /reset_moveit, no auto coordinate getting, no timers

    gui.show()
    app.exec_()

    ros_bridge.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
