# Module reference: `pl_gui/utils/utils_widgets`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [Drawer.py](#drawerpy)
- [MaterialButton.py](#materialbuttonpy)
- [SwitchButton.py](#switchbuttonpy)
- [__init__.py](#__init__py)
- [camera_view.py](#camera_viewpy)
- [camera_view_demo.py](#camera_view_demopy)
- [clickable_label.py](#clickable_labelpy)
- [int_list_widget.py](#int_list_widgetpy)
- [table_helpers.py](#table_helperspy)
- [touch_spinbox.py](#touch_spinboxpy)
- [wizards.py](#wizardspy)

## `Drawer.py`

Source: [pl_gui/utils/utils_widgets/Drawer.py](../../../../pl_gui/utils/utils_widgets/Drawer.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtWidgets`.

### `Drawer`

```python
class Drawer(QWidget):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, parent=None, animation_duration=300, side='right')
```

```python
def toggle(self)
```

Animate drawer open/close from left or right, respecting heightOffset

```python
def resize_to_parent_height(self)
```

Adjust height and position based on parent size and drawer side, respecting heightOffset

## `MaterialButton.py`

Source: [pl_gui/utils/utils_widgets/MaterialButton.py](../../../../pl_gui/utils/utils_widgets/MaterialButton.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtGui`, `PyQt6.QtWidgets`, `sys`.

### `MaterialButton`

```python
class MaterialButton(QPushButton):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, text, color='#6750A4', font_size=12)
```

```python
def apply_style(self)
```

### `WizardStep`

```python
class WizardStep(QWizardPage):
```

Base class for wizard steps with image and text support

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, title, subtitle, description, image_path=None)
```

### `WelcomeStep`

```python
class WelcomeStep(WizardStep):
```

Welcome page - Step 1

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self)
```

### `UserInfoStep`

```python
class UserInfoStep(WizardStep):
```

User information page - Step 2

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self)
```

### `PreferencesStep`

```python
class PreferencesStep(WizardStep):
```

Preferences page - Step 3

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self)
```

### `SummaryStep`

```python
class SummaryStep(WizardStep):
```

Summary page - Step 4

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self)
```

```python
def initializePage(self)
```

Update summary when page is shown

### `SetupWizard`

```python
class SetupWizard(QWizard):
```

Main wizard class

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self)
```

```python
def on_finish(self)
```

Handle wizard completion

```python
def customize_buttons(self)
```

Customize the appearance of wizard buttons using MaterialButton styling

```python
def apply_material_style(self, button, color='#6750A4', font_size=12)
```

Apply MaterialButton style to a wizard button

### `main`

```python
def main()
```

## `SwitchButton.py`

Source: [pl_gui/utils/utils_widgets/SwitchButton.py](../../../../pl_gui/utils/utils_widgets/SwitchButton.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtGui`, `PyQt6.QtWidgets`.

### `QToggle`

```python
class QToggle(QCheckBox):
```

Declared fields/defaults:

```python
bg_color = pyqtProperty(QColor, lambda self: self._bg_color, lambda self, col: setattr(self, '_bg_color', col))
circle_color = pyqtProperty(QColor, lambda self: self._circle_color, lambda self, col: setattr(self, '_circle_color', col))
active_color = pyqtProperty(QColor, lambda self: self._active_color, lambda self, col: setattr(self, '_active_color', col))
disabled_color = pyqtProperty(QColor, lambda self: self._disabled_color, lambda self, col: setattr(self, '_disabled_color', col))
text_color = pyqtProperty(QColor, lambda self: self._text_color, lambda self, col: setattr(self, '_text_color', col))
circle_pos = pyqtProperty(float, lambda self: self._circle_pos, lambda self, pos: (setattr(self, '_circle_pos', pos), self.update()))
intermediate_bg_color = pyqtProperty(QColor, lambda self: self._intermediate_bg_color, lambda self, col: (setattr(self, '_intermediate_bg_color', col), self.update()))
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, parent=None)
```

```python
def setDuration(self, duration: int)
```

Set the duration for the animation. :param duration: Duration in milliseconds.

```python
def update_pos_color(self, checked=None)
```

```python
def sync_visual_state(self, checked: bool) -> None
```

Force a state from the backend, cancelling stale click animations.

```python
def start_transition(self, state)
```

```python
def mousePressEvent(self, event)
```

```python
def create_animation(self, state)
```

```python
def create_bg_color_animation(self, state)
```

```python
def showEvent(self, event)
```

```python
def resizeEvent(self, event)
```

```python
def sizeHint(self)
```

```python
def hitButton(self, pos: QPoint)
```

```python
def paintEvent(self, event)
```

## `__init__.py`

Source: [pl_gui/utils/utils_widgets/__init__.py](../../../../pl_gui/utils/utils_widgets/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `camera_view.py`

Source: [pl_gui/utils/utils_widgets/camera_view.py](../../../../pl_gui/utils/utils_widgets/camera_view.py).

CameraView — zoomable, pannable camera preview with multi-area overlay support. Combines the area-editing API of ``ClickableLabel`` with the zoom/pan capabilities of ``_ZoomableImageWidget`` into a single reusable ``QWidget`` that lives in ``pl_gui/`` and is free of numpy / cv2. All area coordinates are normalised to [0, 1]. Frame delivery (BGR→RGB→ QImage→QPixmap conversion) stays in application controllers — this widget only accepts a ``QPixmap``. Signals ------- corner_updated(area_name, index, x_norm, y_norm) A corner in *area_name* was moved (click-to-place or drag). empty_clicked(area_name, x_norm, y_norm) The user clicked on an empty spot while *area_name* is active and all four corners are already placed. Useful for custom append logic.

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtGui`, `PyQt6.QtWidgets`, `__future__`, `typing`.

### `CameraView`

```python
class CameraView(QWidget):
```

Camera preview widget with zoom/pan and draggable corner-area overlays. Drop-in replacement for ``ClickableLabel`` — exposes the same area-management API and signals while adding zoom/pan and a subclass paint hook. Quick-start:: view = CameraView() view.add_area("working_area") view.set_area_corners("working_area", [(0.1, 0.1), (0.9, 0.1), (0.9, 0.9), (0.1, 0.9)]) view.set_active_area("working_area") view.corner_updated.connect(on_corner) # (area, idx, xn, yn) view.empty_clicked.connect(on_click) # (area, xn, yn) # Push live frames from a controller view.set_frame(pixmap)

Declared fields/defaults:

```python
corner_updated = pyqtSignal(str, int, float, float)
empty_clicked = pyqtSignal(str, float, float)
zoom_changed = pyqtSignal(int)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, parent=None)
```

```python
def set_toolbar_visible(self, visible: bool) -> None
```

Show or hide the built-in zoom toolbar for custom host layouts.

```python
def resizeEvent(self, event) -> None
```

```python
def set_frame(self, pixmap: QPixmap) -> None
```

Push a new camera frame (QPixmap). Zoom/pan state is preserved.

```python
def zoom_in(self) -> None
```

```python
def zoom_out(self) -> None
```

```python
def reset_zoom(self) -> None
```

```python
def add_area(self, name: str, color: str | QColor | None=None) -> None
```

Register a named area with an optional colour. Corners start empty.

```python
def set_active_area(self, name: Optional[str]) -> None
```

Activate an area for editing. Pass *None* for view-only mode.

```python
def set_area_corners(self, name: str, points: List[Tuple[float, float]]) -> None
```

Set corner positions for *name* (normalised [0, 1] coords).

```python
def get_area_corners(self, name: str) -> List[Tuple[float, float]]
```

Return a copy of the corner list for *name*.

```python
def clear_area(self, name: str) -> None
```

Remove all corners for *name*.

```python
def mousePressEvent(self, event: QMouseEvent) -> None
```

```python
def mouseMoveEvent(self, event: QMouseEvent) -> None
```

```python
def mouseReleaseEvent(self, event: QMouseEvent) -> None
```

```python
def wheelEvent(self, event: QWheelEvent) -> None
```

```python
def paintEvent(self, event) -> None
```

### `_nearest`

```python
def _nearest(pts: List[Tuple[float, float]], xn: float, yn: float) -> int
```

Return index of the closest point within _HIT_THRESHOLD, else -1.

## `camera_view_demo.py`

Source: [pl_gui/utils/utils_widgets/camera_view_demo.py](../../../../pl_gui/utils/utils_widgets/camera_view_demo.py).

CameraView demo — no robot, no broker, no real camera. Simulates a live feed via a QTimer that generates simple gradient frames. Pre-registers two areas and activates one for interactive editing. Run with: python pl_gui/utils/utils_widgets/camera_view_demo.y_pixels

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtGui`, `PyQt6.QtWidgets`, `numpy`, `pl_gui.utils.utils_widgets.camera_view`, `random`, `sys`.

### `_make_frame`

```python
def _make_frame(width: int=640, height: int=480, tick: int=0) -> QPixmap
```

Generate a simple animated gradient frame as QPixmap (no cv2).

### `_DemoWindow`

```python
class _DemoWindow(QMainWindow):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self)
```

### `main`

```python
def main() -> None
```

## `clickable_label.py`

Source: [pl_gui/utils/utils_widgets/clickable_label.py](../../../../pl_gui/utils/utils_widgets/clickable_label.py).

ClickableLabel — camera preview with multi-area overlay support. Displays a QPixmap (camera frame) and overlays any number of named corner areas (e.g. "working_area", "brightness_area") as draggable, filled polygons. All coordinates are normalised to [0, 1]. The caller converts to/from the camera resolution (e.g. 1280×720) before passing points in and after reading them back. Signals ------- corner_updated(area_name, index, x_norm, y_norm) A corner in *area_name* was moved (click-to-place or drag). empty_clicked(area_name, x_norm, y_norm) The user clicked on an empty spot while *area_name* is active (no corner hit). Useful for appending a new corner: add the point and call set_area_corners().

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtGui`, `PyQt6.QtWidgets`, `__future__`, `typing`.

### `ClickableLabel`

```python
class ClickableLabel(QLabel):
```

Camera preview with draggable corner areas. Quick-start:: label = ClickableLabel() # Register areas (optional — auto-registered on first set_area_corners call) label.add_area("working_area") # green by default label.add_area("brightness_area") # amber by default # Load saved corners (normalised [0,1]) label.set_area_corners("working_area", [(0.1, 0.1), (0.9, 0.1), (0.9, 0.9), (0.1, 0.9)]) label.set_area_corners("brightness_area", [(0.3, 0.4), (0.7, 0.4), (0.7, 0.6), (0.3, 0.6)]) # Activate one area for editing label.set_active_area("brightness_area") # React to changes label.corner_updated.connect(on_corner) # (area, idx, xn, yn) label.empty_clicked.connect(on_click) # (area, xn, yn) # Push live frames label.set_frame(pixmap)

Declared fields/defaults:

```python
corner_updated = pyqtSignal(str, int, float, float)
empty_clicked = pyqtSignal(str, float, float)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, parent=None)
```

```python
def add_area(self, name: str, color: str | QColor | None=None) -> None
```

Register a named area with an optional colour. Corners start empty.

```python
def set_active_area(self, name: Optional[str]) -> None
```

Activate an area for editing (clicks / drags are routed to it). Pass *None* to enter view-only mode (no editing).

```python
def set_area_corners(self, name: str, points: List[Tuple[float, float]]) -> None
```

Set the corner positions for *name* (normalised [0, 1] coords).

```python
def get_area_corners(self, name: str) -> List[Tuple[float, float]]
```

Return a copy of the corner list for *name* (normalised coords).

```python
def clear_area(self, name: str) -> None
```

Remove all corners for *name*.

```python
def set_frame(self, pixmap: QPixmap) -> None
```

Push a new camera frame. Scaled to fit the label on paint.

```python
def mousePressEvent(self, event: QMouseEvent) -> None
```

```python
def mouseMoveEvent(self, event: QMouseEvent) -> None
```

```python
def mouseReleaseEvent(self, event: QMouseEvent) -> None
```

```python
def paintEvent(self, event) -> None
```

### `_nearest`

```python
def _nearest(pts: List[Tuple[float, float]], xn: float, yn: float) -> int
```

Return index of the closest point within _HIT_THRESHOLD, else -1.

## `int_list_widget.py`

Source: [pl_gui/utils/utils_widgets/int_list_widget.py](../../../../pl_gui/utils/utils_widgets/int_list_widget.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtWidgets`, `pl_gui.settings.settings_view.styles`, `pl_gui.utils.utils_widgets.touch_spinbox`, `typing`.

### `_IntEditorDialog`

```python
class _IntEditorDialog(QDialog):
```

Compact single-value integer editor used by IntListWidget.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, title: str, initial: int, min_val: int, max_val: int, parent=None)
```

```python
def get_value(self) -> int
```

### `IntListWidget`

```python
class IntListWidget(QFrame):
```

Touch-friendly editor for a list of integers. Displays items in a QListWidget with Add / Edit / Remove buttons. Fits into GenericSettingGroup via widget_type="int_list". Signals: valueChanged(list) — emits the full list of ints on every change

Declared fields/defaults:

```python
valueChanged = pyqtSignal(list)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, min_val: int=0, max_val: int=255, parent=None)
```

```python
def get_ids(self) -> List[int]
```

```python
def set_ids(self, value: Union[List[int], str]) -> None
```

```python
def value(self) -> List[int]
```

```python
def setValue(self, val: Union[List[int], str]) -> None
```

## `table_helpers.py`

Source: [pl_gui/utils/utils_widgets/table_helpers.py](../../../../pl_gui/utils/utils_widgets/table_helpers.py).

table_helpers — shared QTableWidget factory for application views. Eliminates the ~8-line table-construction boilerplate + duplicated stylesheet that appeared identically in tool_settings, user_management, workpiece_library, broker_debug, and contour_matching_tester views. Usage:: from pl_gui.utils.utils_widgets.table_helpers import make_table # Simple — all columns stretch equally self._table = make_table(["Name", "Role", "Status"], min_height=200) self._table.horizontalHeader().setSectionResizeMode( QHeaderView.ResizeMode.Stretch) layout.addWidget(self._table) # Custom column widths — caller configures the header after make_table() self._table = make_table(["Topic", "Subs", "Actions"], fixed_height=280) hdr = self._table.horizontalHeader() hdr.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch) hdr.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed) self._table.setColumnWidth(1, 90)

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtWidgets`, `__future__`, `typing`.

Module declarations (expressions are shown without evaluating them):

```python
TABLE_STYLE = '\nQTableWidget {\n    background: white;\n    border: 1px solid #E0E0E0;\n    border-radius: 6px;\n    gridline-color: #F0F0F0;\n    font-size: 9pt;\n    alternate-background-color: #F8F9FA;\n}\nQHeaderView::section {\n    background: #EDE7F6;\n    color: #1A1A2E;\n    font-weight: bold;\n    font-size: 9pt;\n    padding: 6px 4px;\n    border: none;\n    border-bottom: 1px solid #D0C8E0;\n}\nQTableWidget::item { padding: 4px; }\nQTableWidget::item:selected {\n    background: rgba(144, 91, 169, 0.15);\n    color: #1A1A2E;\n}\n'
```

### `make_table`

```python
def make_table(headers: list[str], *, alternate_rows: bool=True, hide_vertical_header: bool=True, sortable: bool=False, min_height: Optional[int]=None, fixed_height: Optional[int]=None) -> QTableWidget
```

Build a pre-configured ``QTableWidget`` matching the app visual style. The caller is responsible for setting column resize modes after this call — that part always varies per table, so ``make_table()`` does not abstract it. Parameters ---------- headers: Column header labels. ``setColumnCount`` is derived from this list. alternate_rows: Enable alternating row colors (default ``True``). hide_vertical_header: Hide the left-side row-number header (default ``True``). sortable: Enable column-header click sorting (default ``False``). min_height: If provided, calls ``setMinimumHeight``. fixed_height: If provided, calls ``setFixedHeight`` (overrides *min_height*).

## `touch_spinbox.py`

Source: [pl_gui/utils/utils_widgets/touch_spinbox.py](../../../../pl_gui/utils/utils_widgets/touch_spinbox.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtGui`, `PyQt6.QtWidgets`, `pl_gui.settings.settings_view.styles`.

### `TouchSpinBox`

```python
class TouchSpinBox(QFrame):
```

Touch-friendly stepper: large – button / value label / + button. Parameters ---------- min_val : lower bound (inclusive) max_val : upper bound (inclusive) initial : starting value (clamped to [min_val, max_val]) step : initial increment/decrement per tap (default 1.0) decimals : decimal places shown in the label (0 → integer display) suffix : text appended to the displayed value (e.g. " mm", "°") step_options : optional list of step sizes shown as selectable pills e.g. [0.01, 0.1, 1, 10]. When provided a compact row of pills is shown below the stepper so the user can switch precision without extra dialog clutter.

Declared fields/defaults:

```python
valueChanged = pyqtSignal(float)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, min_val, max_val, initial=0.0, step=1.0, decimals=1, suffix='', step_options=None, parent=None)
```

```python
def value(self) -> float
```

```python
def setValue(self, val)
```

```python
def clear(self)
```

## `wizards.py`

Source: [pl_gui/utils/utils_widgets/wizards.py](../../../../pl_gui/utils/utils_widgets/wizards.py).

Generic configurable wizard framework for step-by-step processes. Provides base classes for creating wizards with: - Configurable steps with title, subtitle, description, and optional images - Selection steps with radio buttons or dropdowns - Summary/review steps - Material design buttons - Customizable styling

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtGui`, `PyQt6.QtWidgets`, `dashboard.styles`, `dataclasses`, `pathlib`, `pl_gui.dashboard.resources.styles`, `pl_gui.utils.utils_widgets.MaterialButton`, `typing`.

### `WizardStepConfig`

```python
@dataclass
class WizardStepConfig:
```

Configuration for a wizard step.

Declared fields/defaults:

```python
title: str
subtitle: str
description: str
image_path: Optional[str] = None
step_number: Optional[int] = None
```

### `GenericWizardStep`

```python
class GenericWizardStep(QWizardPage):
```

Generic wizard step with title, subtitle, description, and optional image.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, config: WizardStepConfig)
```

### `SelectionStep`

```python
class SelectionStep(GenericWizardStep):
```

Generic selection step with radio buttons.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, config: WizardStepConfig, options: List[str], selection_label: str='Select an option:', empty_message: str='No options available', empty_instructions: str='Please configure options first')
```

```python
def get_selected_option(self) -> Optional[str]
```

Get the currently selected option.

### `SummaryStep`

```python
class SummaryStep(GenericWizardStep):
```

Generic summary/review step with HTML content.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, config: WizardStepConfig, summary_generator: Optional[Callable[[QWizard], str]]=None)
```

```python
def initializePage(self)
```

Called when the page is shown - generate summary dynamically.

### `ConfigurableWizard`

```python
class ConfigurableWizard(QWizard):
```

Generic configurable wizard base class. Usage: wizard = ConfigurableWizard( title="My Wizard", pages=[step1, step2, step3], icon_path="path/to/icon.ico", logo_path="path/to/logo.png", min_width=600, min_height=500 )

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, title: str, pages: List[QWizardPage], icon_path: Optional[str]=None, logo_path: Optional[str]=None, min_width: int=600, min_height: int=500, on_finish_callback: Optional[Callable[[Any], None]]=None, use_material_buttons: bool=True, parent=None)
```
