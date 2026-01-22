from dataclasses import dataclass

from PyQt6.QtWidgets import QGridLayout, QLabel, QSizePolicy, QCheckBox, QComboBox, QPushButton
from PyQt6.QtCore import Qt
from frontend.virtualKeyboard.VirtualKeyboard import FocusSpinBox
from plugins.core.settings.ui.robot_settings_tab.robot_config_groups.base import SettingGroupBox

@dataclass
class ModbusSettings:
    enabled: bool
    port: str
    baudrate: int
    slave_id: int
    byte_size: int
    parity: str
    stop_bits: int
    timeout: float

    def to_dict(self):
        return {
            "enabled": self.enabled,
            "port": self.port,
            "baudrate": self.baudrate,
            "slave_id": self.slave_id,
            "byte_size": self.byte_size,
            "parity": self.parity,
            "stop_bits": self.stop_bits,
            "timeout": self.timeout
        }

class ModbusSettingsGroup(SettingGroupBox):
    def __init__(self):
        super().__init__("Modbus Communication Settings (Xinje MA-8X8YR)")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.layout = self.build_layout()
        self.build_ui()
        self.setMaximumHeight(self.sizeHint().height())

    def build_layout(self):
        layout = QGridLayout()
        return layout

    def build_ui(self):
        modbus_layout = QGridLayout()

        # Enable/Disable Modbus
        self.modbus_enabled_label = QLabel("Enable Modbus:")
        modbus_layout.addWidget(self.modbus_enabled_label, 0, 0)
        self.modbus_enabled = QCheckBox()
        self.modbus_enabled.setChecked(False)
        self.modbus_enabled.stateChanged.connect(self._on_modbus_enabled_changed)
        modbus_layout.addWidget(self.modbus_enabled, 0, 1)

        # Connection Status
        self.status_label = QLabel("Status: Disconnected")
        self.status_label.setStyleSheet("color: #f44336; font-weight: bold; padding: 5px;")
        modbus_layout.addWidget(self.status_label, 0, 2, 1, 2)

        # Port with dropdown and auto-detect
        self.port_label = QLabel("Port:")
        modbus_layout.addWidget(self.port_label, 1, 0)
        self.port = QComboBox()
        self.port.setEditable(True)
        self.port.setPlaceholderText("/dev/ttyUSB0 or COM1")
        self.port.addItem("/dev/ttyUSB0")
        modbus_layout.addWidget(self.port, 1, 1)

        # Scan ports button
        self.scan_ports_btn = QPushButton("Scan Ports")
        self.scan_ports_btn.clicked.connect(self._scan_ports)
        self.scan_ports_btn.setStyleSheet("background-color: #9C27B0; color: white; padding: 5px; font-weight: bold;")
        modbus_layout.addWidget(self.scan_ports_btn, 1, 2)

        # Auto-detect button
        self.auto_detect_btn = QPushButton("Auto-Detect")
        self.auto_detect_btn.clicked.connect(self._auto_detect)
        self.auto_detect_btn.setStyleSheet("background-color: #00BCD4; color: white; padding: 5px; font-weight: bold;")
        modbus_layout.addWidget(self.auto_detect_btn, 1, 3)

        # Baudrate
        self.baudrate_label = QLabel("Baudrate:")
        modbus_layout.addWidget(self.baudrate_label, 2, 0)
        self.baudrate = QComboBox()
        self.baudrate.addItems(["9600", "19200", "38400", "57600", "115200"])
        self.baudrate.setCurrentText("19200")
        modbus_layout.addWidget(self.baudrate, 2, 1)

        # Slave ID
        self.slave_id_label = QLabel("Slave ID:")
        modbus_layout.addWidget(self.slave_id_label, 3, 0)
        self.slave_id = FocusSpinBox()
        self.slave_id.setRange(1, 247)
        self.slave_id.setValue(8)
        modbus_layout.addWidget(self.slave_id, 3, 1)

        # Byte Size
        self.byte_size_label = QLabel("Byte Size:")
        modbus_layout.addWidget(self.byte_size_label, 4, 0)
        self.byte_size = QComboBox()
        self.byte_size.addItems(["7", "8"])
        self.byte_size.setCurrentText("8")
        modbus_layout.addWidget(self.byte_size, 4, 1)

        # Parity
        self.parity_label = QLabel("Parity:")
        modbus_layout.addWidget(self.parity_label, 5, 0)
        self.parity = QComboBox()
        self.parity.addItems(["NONE", "EVEN", "ODD"])
        self.parity.setCurrentText("NONE")
        modbus_layout.addWidget(self.parity, 5, 1)

        # Stop Bits
        self.stop_bits_label = QLabel("Stop Bits:")
        modbus_layout.addWidget(self.stop_bits_label, 6, 0)
        self.stop_bits = QComboBox()
        self.stop_bits.addItems(["1", "2"])
        self.stop_bits.setCurrentText("1")
        modbus_layout.addWidget(self.stop_bits, 6, 1)

        # Timeout
        self.timeout_label = QLabel("Timeout:")
        modbus_layout.addWidget(self.timeout_label, 7, 0)
        self.timeout = FocusSpinBox()
        self.timeout.setRange(1, 1000)
        self.timeout.setValue(100)
        self.timeout.setSuffix(" ms")
        modbus_layout.addWidget(self.timeout, 7, 1)

        # Test Connection and Refresh buttons
        self.test_btn = QPushButton("Test Connection")
        self.test_btn.clicked.connect(self._test_connection)
        self.test_btn.setStyleSheet("background-color: #2196F3; color: white; padding: 5px; font-weight: bold;")
        modbus_layout.addWidget(self.test_btn, 8, 0)

        self.refresh_btn = QPushButton("Refresh States")
        self.refresh_btn.clicked.connect(self._manual_refresh)
        self.refresh_btn.setStyleSheet("background-color: #FF9800; color: white; padding: 5px; font-weight: bold;")
        modbus_layout.addWidget(self.refresh_btn, 8, 1)

        # Relay Output Controls (Y0-Y7)
        self.output_label = QLabel("Relay Outputs (Y0-Y7):")
        self.output_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        modbus_layout.addWidget(self.output_label, 9, 0, 1, 2)

        # Create output buttons in 2 rows of 4
        self.output_buttons = []
        for i in range(8):
            row = 10 + (i // 4)
            col = i % 4

            btn = QPushButton(f"Y{i}")
            btn.setCheckable(True)
            btn.setMinimumHeight(40)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #555;
                    color: white;
                    border: 2px solid #666;
                    border-radius: 5px;
                    font-weight: bold;
                }
                QPushButton:checked {
                    background-color: #4CAF50;
                    border: 2px solid #45a049;
                }
                QPushButton:hover {
                    background-color: #666;
                }
                QPushButton:checked:hover {
                    background-color: #45a049;
                }
                QPushButton:disabled {
                    background-color: #333;
                    color: #666;
                }
            """)
            btn.clicked.connect(lambda checked, output_num=i: self._on_output_clicked(output_num, checked))
            modbus_layout.addWidget(btn, row, col)
            self.output_buttons.append(btn)

        # Add X0-X7 input indicators (read-only)
        self.input_label = QLabel("Digital Inputs (X0-X7):")
        self.input_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        modbus_layout.addWidget(self.input_label, 12, 0, 1, 2)

        # Create input indicators in 2 rows of 4
        self.input_indicators = []
        for i in range(8):
            row = 13 + (i // 4)
            col = i % 4

            indicator = QLabel(f"X{i}")
            indicator.setMinimumHeight(40)
            indicator.setAlignment(Qt.AlignmentFlag.AlignCenter)
            indicator.setStyleSheet("""
                QLabel {
                    background-color: #333;
                    color: #888;
                    border: 2px solid #444;
                    border-radius: 5px;
                    font-weight: bold;
                }
            """)
            modbus_layout.addWidget(indicator, row, col)
            self.input_indicators.append(indicator)

        self.setLayout(modbus_layout)
        self.layout.addWidget(self)
        self.setLayout(self.layout)

        # Don't auto-poll inputs - only refresh when button is clicked
        # (Xinje relay doesn't respond to read commands reliably)

        self._on_modbus_enabled_changed(self.modbus_enabled.isChecked())

    def _on_modbus_enabled_changed(self, enabled):
        self.port.setEnabled(enabled)
        self.baudrate.setEnabled(enabled)
        self.slave_id.setEnabled(enabled)
        self.byte_size.setEnabled(enabled)
        self.parity.setEnabled(enabled)
        self.stop_bits.setEnabled(enabled)
        self.timeout.setEnabled(enabled)
        self.test_btn.setEnabled(enabled)
        self.refresh_btn.setEnabled(enabled)
        for btn in self.output_buttons:
            btn.setEnabled(enabled)

    def _test_connection(self):
        """Test modbus connection and initialize controller"""
        from modules.modbusCommunication.ModbusController import ModbusController
        from PyQt6.QtWidgets import QMessageBox

        # Get current settings from UI
        settings = self.get_settings().to_dict()

        try:
            # Try to initialize with current settings
            ModbusController.initialize(settings)
            relay = ModbusController.get_relay_controller()

            if relay:
                # Test by writing to output 0 (toggle it)
                # Note: Xinje relay might not support reading, so we just test writing
                try:
                    relay.write_output(0, True)
                    import time
                    time.sleep(0.1)
                    relay.write_output(0, False)
                    test_success = True
                except:
                    test_success = False

                self.status_label.setText("Status: Connected")
                self.status_label.setStyleSheet("color: #4CAF50; font-weight: bold; padding: 5px;")
                QMessageBox.information(
                    self,
                    "Connection Successful",
                    f"Successfully connected to Xinje relay at {settings['port']}\n"
                    f"Slave ID: {settings['slave_id']}\n"
                    f"Baudrate: {settings['baudrate']}\n"
                    f"Parity: {settings['parity']}\n\n"
                    f"Test write: {'Success' if test_success else 'Failed'}\n"
                    f"Check if Y0 LED blinked on the relay."
                )
                # Don't try to refresh button states since reading might not work
                # self.refresh_output_states()
            else:
                self.status_label.setText("Status: Connection Failed")
                self.status_label.setStyleSheet("color: #f44336; font-weight: bold; padding: 5px;")
                QMessageBox.warning(
                    self,
                    "Connection Failed",
                    "Failed to initialize relay controller.\n"
                    "Check port and connection."
                )
        except Exception as e:
            self.status_label.setText("Status: Error")
            self.status_label.setStyleSheet("color: #f44336; font-weight: bold; padding: 5px;")
            QMessageBox.critical(
                self,
                "Connection Error",
                f"Error connecting to relay:\n{str(e)}\n\n"
                "Please check:\n"
                "- Port is correct (/dev/ttyUSB0 or COM1)\n"
                "- Device is connected and powered\n"
                "- No other application is using the port"
            )
            import traceback
            traceback.print_exc()

    def _manual_refresh(self):
        """Manually refresh output states"""
        from modules.modbusCommunication.ModbusController import ModbusController
        from PyQt6.QtWidgets import QMessageBox

        relay = ModbusController.get_relay_controller()
        if relay:
            try:
                self.refresh_output_states()
                QMessageBox.information(
                    self,
                    "Refresh Complete",
                    "Output states refreshed successfully"
                )
            except Exception as e:
                QMessageBox.warning(
                    self,
                    "Refresh Failed",
                    f"Failed to refresh states:\n{str(e)}"
                )
        else:
            QMessageBox.warning(
                self,
                "Not Connected",
                "Relay controller not initialized.\n"
                "Click 'Test Connection' first."
            )

    def _on_output_clicked(self, output_num, checked):
        """Handle relay output button click"""
        from modules.modbusCommunication.ModbusController import ModbusController
        from PyQt6.QtWidgets import QMessageBox

        # Check if modbus is enabled first
        if not self.modbus_enabled.isChecked():
            self.output_buttons[output_num].setChecked(not checked)
            QMessageBox.warning(
                self,
                "Modbus Disabled",
                "Please enable Modbus communication first and save settings."
            )
            return

        relay = ModbusController.get_relay_controller()
        if relay:
            success = relay.write_output(output_num, checked)
            if not success:
                # Revert button state if write failed
                self.output_buttons[output_num].setChecked(not checked)
                print(f"[ModbusSettings] Failed to set output Y{output_num}")
                QMessageBox.warning(
                    self,
                    "Communication Error",
                    f"Failed to set output Y{output_num}. Check connection and settings."
                )
        else:
            # Revert button state if relay not initialized
            self.output_buttons[output_num].setChecked(not checked)
            print("[ModbusSettings] Relay controller not initialized")
            QMessageBox.warning(
                self,
                "Not Initialized",
                "Modbus controller not initialized.\n\n"
                "Please:\n"
                "1. Enable Modbus\n"
                "2. Configure settings (port, baudrate, etc.)\n"
                "3. Save settings\n"
                "4. Reload settings or restart application"
            )

    def get_settings(self) -> ModbusSettings:
        return ModbusSettings(
            enabled=self.modbus_enabled.isChecked(),
            port=self.port.currentText(),
            baudrate=int(self.baudrate.currentText()),
            slave_id=self.slave_id.value(),
            byte_size=int(self.byte_size.currentText()),
            parity=self.parity.currentText(),
            stop_bits=int(self.stop_bits.currentText()),
            timeout=self.timeout.value() / 1000.0
        )

    def update_values(self, settings: ModbusSettings):
        self.modbus_enabled.setChecked(settings.enabled)
        self.port.setCurrentText(settings.port)
        self.baudrate.setCurrentText(str(settings.baudrate))
        self.slave_id.setValue(settings.slave_id)
        self.byte_size.setCurrentText(str(settings.byte_size))
        self.parity.setCurrentText(settings.parity)
        self.stop_bits.setCurrentText(str(settings.stop_bits))
        self.timeout.setValue(int(settings.timeout * 1000))

        # Refresh output button states
        if settings.enabled:
            self.refresh_output_states()

    def refresh_output_states(self):
        """Read current relay output states and update buttons (if supported)"""
        from modules.modbusCommunication.ModbusController import ModbusController

        relay = ModbusController.get_relay_controller()
        if relay:
            try:
                outputs = relay.read_all_outputs()
                for i, state in enumerate(outputs):
                    if i < len(self.output_buttons):
                        # Block signals to prevent triggering write during refresh
                        self.output_buttons[i].blockSignals(True)
                        self.output_buttons[i].setChecked(state)
                        self.output_buttons[i].blockSignals(False)
            except Exception as e:
                # Reading not supported - this is OK for write-only relays
                print(f"[ModbusSettings] Cannot read relay states (write-only device?): {e}")
                pass

    def _scan_ports(self):
        """Scan for available serial ports"""
        from PyQt6.QtWidgets import QMessageBox
        import serial.tools.list_ports

        # Get list of available ports
        ports = serial.tools.list_ports.comports()

        if not ports:
            QMessageBox.information(
                self,
                "No Ports Found",
                "No serial ports detected.\n\n"
                "Please check:\n"
                "- Device is connected\n"
                "- USB drivers are installed\n"
                "- Device has power"
            )
            return

        # Clear and update port dropdown
        self.port.clear()
        port_list = []
        for port in ports:
            port_name = port.device
            port_desc = f"{port_name} - {port.description}"
            self.port.addItem(port_desc, port_name)
            port_list.append(f"{port_name}: {port.description}")

        # Select first port
        if self.port.count() > 0:
            self.port.setCurrentIndex(0)

        QMessageBox.information(
            self,
            "Ports Found",
            f"Found {len(ports)} serial port(s):\n\n" + "\n".join(port_list)
        )

    def _auto_detect(self):
        """Auto-detect Xinje relay on available ports with all settings combinations"""
        from PyQt6.QtWidgets import QMessageBox, QProgressDialog
        from PyQt6.QtCore import Qt
        from modules.modbusCommunication.ModbusController import ModbusController
        import serial.tools.list_ports

        # Get list of available ports
        ports = serial.tools.list_ports.comports()

        if not ports:
            QMessageBox.warning(
                self,
                "No Ports Found",
                "No serial ports detected.\n"
                "Please connect the device and try again."
            )
            return

        # Define common settings to try
        baudrates = [19200, 9600, 38400, 115200, 57600]  # Most common first
        parities = ['NONE', 'EVEN', 'ODD']
        slave_ids = [8, 1, 2, 3, 4, 5, 6, 7, 9, 10]  # Default 8 first

        # Calculate total combinations
        total_tests = len(ports) * len(baudrates) * len(parities) * len(slave_ids)

        # Ask user if they want to test all combinations
        reply = QMessageBox.question(
            self,
            "Auto-Detect Mode",
            f"Found {len(ports)} port(s).\n\n"
            f"Quick Mode: Test only current settings on all ports\n"
            f"Full Mode: Test {total_tests} combinations (all ports, baudrates, parities, slave IDs)\n\n"
            f"This may take several minutes.\n\n"
            f"Use Full Mode?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Cancel:
            return

        full_mode = reply == QMessageBox.StandardButton.Yes

        if full_mode:
            total_combinations = total_tests
            test_label = "Full scan with all combinations"
        else:
            total_combinations = len(ports)
            test_label = "Quick scan with current settings"

        # Create progress dialog
        progress = QProgressDialog(
            f"{test_label}...",
            "Cancel",
            0,
            total_combinations,
            self
        )
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setWindowTitle("Auto-Detecting Device")
        progress.setMinimumWidth(400)

        found_port = None
        found_settings = None
        test_count = 0

        # Quick mode: Use current settings
        if not full_mode:
            current_baudrate = int(self.baudrate.currentText())
            current_parity = self.parity.currentText()
            current_slave_id = self.slave_id.value()

            for port in ports:
                if progress.wasCanceled():
                    break

                progress.setValue(test_count)
                progress.setLabelText(f"Testing {port.device}...\n{port.description}")
                test_count += 1

                test_settings = {
                    'enabled': True,
                    'port': port.device,
                    'baudrate': current_baudrate,
                    'slave_id': current_slave_id,
                    'byte_size': int(self.byte_size.currentText()),
                    'parity': current_parity,
                    'stop_bits': int(self.stop_bits.currentText()),
                    'timeout': 0.2  # Faster timeout for scanning
                }

                if self._test_settings(test_settings):
                    found_port = port.device
                    found_settings = test_settings
                    break

        # Full mode: Try all combinations
        else:
            for port in ports:
                if progress.wasCanceled() or found_port:
                    break

                for baudrate in baudrates:
                    if progress.wasCanceled() or found_port:
                        break

                    for parity in parities:
                        if progress.wasCanceled() or found_port:
                            break

                        for slave_id in slave_ids:
                            if progress.wasCanceled() or found_port:
                                break

                            progress.setValue(test_count)
                            progress.setLabelText(
                                f"Testing {port.device}...\n"
                                f"Baudrate: {baudrate}, Parity: {parity}, Slave: {slave_id}\n"
                                f"Progress: {test_count}/{total_combinations}"
                            )
                            test_count += 1

                            test_settings = {
                                'enabled': True,
                                'port': port.device,
                                'baudrate': baudrate,
                                'slave_id': slave_id,
                                'byte_size': 8,
                                'parity': parity,
                                'stop_bits': 1,
                                'timeout': 0.1  # Very fast timeout for full scan
                            }

                            if self._test_settings(test_settings):
                                found_port = port.device
                                found_settings = test_settings
                                break

        progress.setValue(progress.maximum())

        if found_port and found_settings:
            # Update UI with found settings
            self.port.setCurrentText(found_port)
            self.baudrate.setCurrentText(str(found_settings['baudrate']))
            self.slave_id.setValue(found_settings['slave_id'])
            self.parity.setCurrentText(found_settings['parity'])
            self.byte_size.setCurrentText(str(found_settings['byte_size']))
            self.stop_bits.setCurrentText(str(found_settings['stop_bits']))

            self.status_label.setText("Status: Connected")
            self.status_label.setStyleSheet("color: #4CAF50; font-weight: bold; padding: 5px;")

            # Refresh button states
            self.refresh_output_states()

            QMessageBox.information(
                self,
                "Device Found!",
                f"Xinje relay detected and configured!\n\n"
                f"Port: {found_port}\n"
                f"Baudrate: {found_settings['baudrate']}\n"
                f"Parity: {found_settings['parity']}\n"
                f"Slave ID: {found_settings['slave_id']}\n"
                f"Byte Size: {found_settings['byte_size']}\n"
                f"Stop Bits: {found_settings['stop_bits']}\n\n"
                f"Tested {test_count} configuration(s).\n"
                f"Connection established successfully!"
            )
        else:
            self.status_label.setText("Status: Not Found")
            self.status_label.setStyleSheet("color: #FF9800; font-weight: bold; padding: 5px;")

            QMessageBox.warning(
                self,
                "Device Not Found",
                f"Could not detect Xinje relay after testing {test_count} configuration(s).\n\n"
                f"Tested:\n"
                f"- {len(ports)} port(s)\n"
                f"- {'All baudrates and settings' if full_mode else 'Current settings only'}\n\n"
                "Please check:\n"
                "1. Device is powered on\n"
                "2. Cable connections are secure\n"
                "3. Device is Xinje MA-8X8YR or compatible\n"
                "4. Try Full Mode if you used Quick Mode"
            )

    def _test_settings(self, test_settings):
        """
        Test a single settings configuration.
        Returns True if connection successful, False otherwise.
        """
        from modules.modbusCommunication.ModbusController import ModbusController

        try:
            ModbusController.initialize(test_settings)
            relay = ModbusController.get_relay_controller()

            if relay:
                # Test by writing (reading might not be supported)
                try:
                    relay.write_output(0, True)
                    import time
                    time.sleep(0.05)
                    relay.write_output(0, False)
                    return True  # Write succeeded
                except:
                    pass
        except Exception as e:
            # Silently fail and continue to next configuration
            pass

        return False

    def _poll_inputs(self):
        """Poll X0-X7 inputs and update UI indicators"""
        if not self.modbus_enabled.isChecked():
            return

        from modules.modbusCommunication.ModbusController import ModbusController

        relay = ModbusController.get_relay_controller()
        if not relay:
            return

        try:
            # Read all 8 inputs
            for i in range(8):
                try:
                    state = relay.read_input(i)
                    indicator = self.input_indicators[i]

                    # Update indicator based on input state
                    if state:
                        indicator.setStyleSheet("""
                            QLabel {
                                background-color: #4CAF50;
                                color: white;
                                border: 2px solid #45a049;
                                border-radius: 5px;
                                font-weight: bold;
                            }
                        """)
                    else:
                        indicator.setStyleSheet("""
                            QLabel {
                                background-color: #333;
                                color: #888;
                                border: 2px solid #444;
                                border-radius: 5px;
                                font-weight: bold;
                            }
                        """)
                except Exception as e:
                    # On error, show gray indicator
                    pass
        except Exception as e:
            # Silently fail if relay not available
            pass



