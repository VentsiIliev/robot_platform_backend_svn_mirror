from PyQt6.QtCore import (
    pyqtSignal
)
from PyQt6.QtWidgets import (
    QWidget, QGridLayout, QSizePolicy
)

from frontend.core.utils.localization import TranslatableWidget, TranslationKeys
from frontend.widgets.MaterialButton import MaterialButton
from plugins.core.dashboard.ui.widgets.ControlButtonsWidget import ControlButtonsWidget
from plugins.core.dashboard.ui.widgets.RobotTrajectoryWidget import RobotTrajectoryWidget
from plugins.core.dashboard.ui.config.dashboard_styles import DashboardConfig
from plugins.core.dashboard.ui.factories.GlueCardFactory import GlueCardFactory
from plugins.core.dashboard.ui.managers.DashboardLayoutManager import DashboardLayoutManager
from plugins.core.dashboard.ui.managers.DashboardMessageManager import DashboardMessageManager
from plugins.core.dashboard.ui.widgets.DashboardCard import DashboardCard


class CardContainer(QWidget):
    select_card_signal = pyqtSignal(object)

    def __init__(self, columns=3, rows=2):
        super().__init__()
        self.columns = columns
        self.rows = rows
        self.total_cells = columns * rows

        self.layout = QGridLayout()
        self.layout.setSpacing(10)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        # Set equal stretch for all rows and columns for uniform sizing
        # This ensures all cells have the same size
        for row in range(self.rows):
            self.layout.setRowStretch(row, 1)
            # FIX: Use dynamic minimum height based on available space
            self.layout.setRowMinimumHeight(row, 180)  # Reduced from 200

        for col in range(self.columns):
            self.layout.setColumnStretch(col, 1)
            # FIX: Use dynamic minimum width based on available space
            self.layout.setColumnMinimumWidth(col, 200)  # Reduced from 250

        # Set size policy for the container to ensure it expands properly
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

class DashboardWidget(TranslatableWidget):
    start_requested = pyqtSignal()
    stop_requested = pyqtSignal()
    pause_requested = pyqtSignal()
    clean_requested= pyqtSignal()
    reset_errors_requested = pyqtSignal()
    glue_type_changed_signal = pyqtSignal(int, str)
    nesting_toggled = pyqtSignal(bool)
    contour_comparison_toggled = pyqtSignal(bool)
    operation_mode_changed = pyqtSignal(str)
    operation_params_changed = pyqtSignal(dict)
    alignment_mode_changed = pyqtSignal(str)


    def __init__(self, updateCameraFeedCallback, config=None, parent=None):
        super().__init__(parent, auto_retranslate=False)

        # Configuration
        self.config = config or DashboardConfig()
        self.updateCameraFeedCallback = updateCameraFeedCallback

        # Managers - composition over inheritance
        self.message_manager = DashboardMessageManager()
        self.card_factory = GlueCardFactory(self.config, self.message_manager)

        # Shared components
        self.shared_card_container = CardContainer(columns=1, rows=3)

        # State tracking for toggles
        self.nesting_enabled = False
        self.contour_comparison_enabled = False
        self.operation_mode = "Painting"
        self.alignment_mode = "Horizontal"

        # Initialize UI
        self.init_ui()
        self.init_translations()

    """GLUE DISPENSING APPLICATION SPECIFIC"""
    def on_mode_toggle(self):
        if self.operation_mode == "Painting":
            self.operation_mode = "Glueing"
        else:
            self.operation_mode = "Painting"

        self.mode_toggle_button.setText(self.operation_mode)
        self.operation_mode_changed.emit(self.operation_mode)
        print(f"Operation mode changed to {self.operation_mode}")

    def on_nesting_toggle(self):
        """Toggle nesting feature ON/OFF"""
        self.nesting_enabled = not self.nesting_enabled
        state_text = "ON" if self.nesting_enabled else "OFF"
        self.nesting_toggle_button.setText(f"Nesting: {state_text}")
        self.nesting_toggled.emit(self.nesting_enabled)
        print(f"Nesting toggled: {state_text}")

    def on_contour_comparison_toggle(self):
        """Toggle contour comparison feature ON/OFF"""
        self.contour_comparison_enabled = not self.contour_comparison_enabled
        state_text = "ON" if self.contour_comparison_enabled else "OFF"
        self.contour_comparison_toggle_button.setText(f"Contour Check: {state_text}")
        self.contour_comparison_toggled.emit(self.contour_comparison_enabled)
        print(f"Contour comparison toggled: {state_text}")

    def on_alignment_toggle(self):
        """Toggle alignment mode between Horizontal and Vertical"""
        if self.alignment_mode == "Horizontal":
            self.alignment_mode = "Vertical"
        else:
            self.alignment_mode = "Horizontal"

        self.alignment_toggle_button.setText(f"Align: {self.alignment_mode}")
        self.alignment_mode_changed.emit(self.alignment_mode)
        print(f"Alignment mode changed to {self.alignment_mode}")

    def get_operation_params(self):
        """Get current operation parameters from the dialog if available, otherwise return defaults"""
        # Try to get params from the dialog if it exists
        from PyQt6.QtWidgets import QApplication

        main_window = None
        for widget in QApplication.topLevelWidgets():
            if widget.__class__.__name__ == 'MainWindow':
                main_window = widget
                break

        if main_window and hasattr(main_window, 'operation_params_dialog') and main_window.operation_params_dialog:
            return main_window.operation_params_dialog.get_params()

        # Return default values if dialog not created yet
        return {
            'velocity': 20,
            'acceleration': 20,
            'z_offset': 6.0,
            'lift_z': 200.0,
            'iterations': 1,
            'wait_time': 0.0,
            'enable_pressure_adjustment': True,
            'target_force_x': 2.0,
            'force_adjustment_gain': 0.1,
            'force_deadband': 0.5,
            'max_search_distance': 15.0,
            'search_step_size': 0.5,
            'contact_threshold': 1.0,
            'search_velocity': 5,
            'search_at_all_corners': True,
            'max_position_adjustment': 12.0,
            'rotation_coefficient': 0.05,
            'max_rotation_adjustment': 2.0
        }

    def init_ui(self):
        # Create layout manager
        self.layout_manager = DashboardLayoutManager(self, self.config)

        # Create trajectory widget
        """GLUE DISPENSING APPLICATION SPECIFIC"""
        self.trajectory_widget = RobotTrajectoryWidget(
            image_width=self.config.trajectory_width,
            image_height=self.config.trajectory_height
        )

        # Subscribe trajectory widget
        self.message_manager.subscribe_trajectory_widget(self.trajectory_widget)

        # Create control buttons
        self.control_buttons = ControlButtonsWidget()
        self.control_buttons.start_clicked.connect(self.start_requested.emit)
        self.control_buttons.stop_clicked.connect(self.stop_requested.emit)
        self.control_buttons.pause_clicked.connect(self.pause_requested.emit)

        """GLUE DISPENSING APPLICATION SPECIFIC"""
        self.clean_button = MaterialButton("Clean", font_size=20)
        self.clean_button.clicked.connect(self.clean_requested.emit)

        self.reset_errors_button = MaterialButton("Reset Errors", font_size=20)
        self.reset_errors_button.clicked.connect(self.reset_errors_requested.emit)

        """GLUE DISPENSING APPLICATION SPECIFIC"""
        self.mode_toggle_button = MaterialButton("Painting", font_size=20)
        self.mode_toggle_button.clicked.connect(self.on_mode_toggle)

        """GLUE DISPENSING APPLICATION SPECIFIC"""
        # Nesting toggle button
        self.nesting_toggle_button = MaterialButton("Nesting: OFF", font_size=16)
        self.nesting_toggle_button.clicked.connect(self.on_nesting_toggle)

        # Contour comparison toggle button
        self.contour_comparison_toggle_button = MaterialButton("Contour Check: OFF", font_size=16)
        self.contour_comparison_toggle_button.clicked.connect(self.on_contour_comparison_toggle)

        # Alignment toggle button
        self.alignment_toggle_button = MaterialButton("Align: Horizontal", font_size=16)
        self.alignment_toggle_button.clicked.connect(self.on_alignment_toggle)

        """GLUE DISPENSING APPLICATION SPECIFIC"""
        # Create glue cards
        glue_cards = []
        self.glue_cards_dict = {}  # Store cards for easy access by index
        for i in range(1, self.config.glue_meters_count + 1):
            card = self.create_glue_card(i, f"Glue {i}")
            glue_cards.append(card)
            self.glue_cards_dict[i] = card  # Store reference by index

        # Subscribe card container
        self.message_manager.subscribe_card_container(self.shared_card_container)

        # Setup layout (params now accessed via CTRL+O instead of inline widget)
        self.layout_manager.setup_complete_layout(
            self.trajectory_widget,
            glue_cards,
            self.control_buttons,
            self.clean_button,
            self.reset_errors_button,
            self.mode_toggle_button,
            self.nesting_toggle_button,
            self.contour_comparison_toggle_button,
            self.alignment_toggle_button,
            None  # params_widget removed - use CTRL+O shortcut instead
        )

    def retranslate(self) -> None:

        self.clean_button.setText(self.tr(TranslationKeys.Dashboard.CLEAN))
        for card in self.glue_cards_dict.values():
            # update the title of each glue card: "Glue {id}"
            card.title_label.setText(f"{self.tr(TranslationKeys.Dashboard.GLUE)} {card.card_index}")

    """GLUE DISPENSING APPLICATION SPECIFIC"""
    def create_glue_card(self, index: int, label_text: str) -> DashboardCard:
        """Create glue card using factory"""
        card = self.card_factory.create_glue_card(index, label_text, self.shared_card_container)
        # Connect signals
        card.glue_type_combo.currentTextChanged.connect(
            lambda value, idx=index: self.glue_type_changed_signal.emit(idx, value)
        )
        card.long_press_detected.connect(self.on_glue_card_long_press)

        return card

    """GLUE DISPENSING APPLICATION SPECIFIC"""
    def on_glue_card_long_press(self, card_index: int):
        """Handle long press on glue card - show glue change wizard"""
        from new_development.setupWizard import SetupWizard

        wizard = SetupWizard()
        wizard.setWindowTitle(f"Change Glue for Cell {card_index}")

        # Store the card index in the wizard for later use
        wizard.card_index = card_index

        # Connect wizard finished signal
        wizard.finished.connect(lambda result: self.on_wizard_finished(result, wizard))

        wizard.exec()

    """GLUE DISPENSING APPLICATION SPECIFIC"""
    def on_wizard_finished(self, result, wizard):
        """Handle wizard completion"""
        print(f"Wizard finished with result: {result}")

        if result == 1:  # QDialog.Accepted
            # Get selected glue type from wizard
            selected_glue_type = wizard.get_selected_glue_type()
            card_index = wizard.card_index

            print(f"Selected glue type: {selected_glue_type}, Card index: {card_index}")

            if selected_glue_type and card_index:
                # Use the stored dictionary to find the card
                if card_index in self.glue_cards_dict:
                    card = self.glue_cards_dict[card_index]
                    print(f"Found card with index {card_index}, updating combo to {selected_glue_type}")
                    card.glue_type_combo.setCurrentText(selected_glue_type)
                else:
                    print(f"Warning: Card with index {card_index} not found in dictionary")
                    print(f"Available card indices: {list(self.glue_cards_dict.keys())}")

                # Emit signal to update configuration
                print(f"Emitting glue_type_changed_signal: {card_index}, {selected_glue_type}")
                self.glue_type_changed_signal.emit(card_index, selected_glue_type)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Resize event handling can be added here if needed

    def clean_up(self):
        """Clean up resources when the widget is closed"""
        print("Cleaning up DashboardWidget")
        self.message_manager.cleanup()
        self.shared_card_container = None
        self.control_buttons.clean_up()



