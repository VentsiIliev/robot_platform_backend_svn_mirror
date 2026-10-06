# Module reference: `scripts`

[Package guide](README.md) · [Complete source index](../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [audit_package_dependencies.py](#audit_package_dependenciespy)
- [calibration_workflow_probe.py](#calibration_workflow_probepy)
- [charuco_live.py](#charuco_livepy)
- [charuco_test.py](#charuco_testpy)
- [charucoboard_detection_test.py](#charucoboard_detection_testpy)
- [example.py](#examplepy)
- [example_tcp_calib.py](#example_tcp_calibpy)
- [flatten_directory.py](#flatten_directorypy)
- [generate_charuco_board.py](#generate_charuco_boardpy)
- [laser_on_off.py](#laser_on_offpy)
- [live_camera_crosshair.py](#live_camera_crosshairpy)
- [migrate_global_calibration_to_work_area.py](#migrate_global_calibration_to_work_areapy)
- [network_connect.py](#network_connectpy)
- [paint_motion_plane_probe.py](#paint_motion_plane_probepy)
- [paint_web_jog.py](#paint_web_jogpy)
- [plate_workpiece_placer.py](#plate_workpiece_placerpy)
- [publish_changes.py](#publish_changespy)
- [raw_http_camera_viewer.py](#raw_http_camera_viewerpy)
- [raw_http_camera_viewer_requests.py](#raw_http_camera_viewer_requestspy)
- [read_slave10_address0.py](#read_slave10_address0py)
- [read_xinje_io.py](#read_xinje_iopy)
- [run_paint_vision_isolated.py](#run_paint_vision_isolatedpy)
- [run_platform.py](#run_platformpy)
- [sim_test.py](#sim_testpy)
- [test.py](#testpy)
- [test_paint_contour_interpolation_from_dump.py](#test_paint_contour_interpolation_from_dumppy)
- [test_paint_peripherals.py](#test_paint_peripheralspy)
- [test_relay_y1.py](#test_relay_y1py)
- [test_servo_pickup_procedure.py](#test_servo_pickup_procedurepy)
- [two_camera_preview.py](#two_camera_previewpy)
- [vacuum_pump_off.py](#vacuum_pump_offpy)
- [video_capture.py](#video_capturepy)
- [vision_aruco_test.py](#vision_aruco_testpy)
- [write_compact_paint_register.py](#write_compact_paint_registerpy)
- [write_y0.py](#write_y0py)
- [xinje_ma_manual_test.py](#xinje_ma_manual_testpy)

## `audit_package_dependencies.py`

Source: [scripts/audit_package_dependencies.py](../../scripts/audit_package_dependencies.py).

Report static imports between proposed packages without importing application code.

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `argparse`, `ast`, `collections`, `json`, `pathlib`.

Module declarations (expressions are shown without evaluating them):

```python
ROOT = Path(__file__).resolve().parents[1]
SHARED = {'src.shared_contracts': 'contracts', 'src.engine': 'engine', 'src.applications': 'applications', 'src.bootstrap': 'bootstrap', 'pl_gui': 'shell'}
```

### `owner`

```python
def owner(module: str) -> str | None
```

Map an import namespace to its proposed distribution boundary.

### `audit`

```python
def audit() -> dict
```

Collect import sites, including relative imports and imports in guarded code.

### `markdown`

```python
def markdown(report: dict) -> str
```

Render an overview and representative import sites for every dependency.

## `calibration_workflow_probe.py`

Source: [scripts/calibration_workflow_probe.py](../../scripts/calibration_workflow_probe.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtWidgets`, `__future__`, `dataclasses`, `json`, `pl_gui.settings.settings_view.styles`, `pl_gui.utils.utils_widgets.MaterialButton`, `pl_gui.utils.utils_widgets.wizards`, `src.applications.base.app_styles`, `src.applications.base.drawer_toggle`, `src.applications.base.robot_jog_widget`, `src.applications.base.styled_message_box`, `sys`, `typing`.

Module declarations (expressions are shown without evaluating them):

```python
AXES = ('x', 'y', 'z')
ROT_AXES = ('rx', 'ry', 'rz')
LINEAR_JOG_BUTTONS = ('btn_x_plus', 'btn_x_minus', 'btn_y_plus', 'btn_y_minus', 'btn_z_plus', 'btn_z_minus')
ROTATION_JOG_BUTTONS = ('btn_rx_plus', 'btn_rx_minus', 'btn_ry_plus', 'btn_ry_minus', 'btn_rz_plus', 'btn_rz_minus')
```

### `Pose6D`

```python
@dataclass(frozen=True)
class Pose6D:
```

Declared fields/defaults:

```python
x: float
y: float
z: float
rx: float
ry: float
rz: float
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def as_list(self) -> list[float]
```

### `CalibrationWorkflowState`

```python
@dataclass
class CalibrationWorkflowState:
```

Declared fields/defaults:

```python
current_pose: Pose6D = field(default_factory=lambda: Pose6D(100, -300, 300, 180, 0, 0))
board_placed: bool = False
camera_calibrated: bool = False
robot_calibrated: bool = False
camera_tcp_offset_calibrated: bool = False
camera_center_pose: Pose6D | None = None
tool_point_pose: Pose6D | None = None
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def as_summary(self) -> dict
```

### `_action_button`

```python
def _action_button(text: str) -> MaterialButton
```

### `_secondary_button`

```python
def _secondary_button(text: str) -> MaterialButton
```

### `_label`

```python
def _label(text: str) -> QLabel
```

### `PoseReadout`

```python
class PoseReadout(QWidget):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, initial: Iterable[float]=(0, 0, 300, 180, 0, 0)) -> None
```

```python
def set_pose(self, pose: Pose6D | None) -> None
```

### `_pose_group`

```python
def _pose_group(title: str, widget: QWidget) -> QGroupBox
```

### `StatusRow`

```python
class StatusRow(QWidget):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, title: str) -> None
```

```python
def set_done(self, done: bool) -> None
```

### `CalibrationWizardPage`

```python
class CalibrationWizardPage(QWizardPage):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, state: CalibrationWorkflowState, title: str, info_text: str) -> None
```

```python
def set_pose_changed_callback(self, callback) -> None
```

```python
def nextId(self) -> int
```

```python
@staticmethod
def set_jog_buttons_enabled(jog: RobotJogWidget, names: tuple[str, ...], enabled: bool) -> None
```

### `_notice_style`

```python
def _notice_style() -> str
```

### `PlaceBoardPage`

```python
class PlaceBoardPage(CalibrationWizardPage):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, state: CalibrationWorkflowState) -> None
```

```python
def initializePage(self) -> None
```

```python
def isComplete(self) -> bool
```

### `SimulatedCalibrationPage`

```python
class SimulatedCalibrationPage(CalibrationWizardPage):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, state: CalibrationWorkflowState, *, title: str, info_text: str, status_title: str, button_text: str, confirm_title: str | None=None, confirm_text: str | None=None) -> None
```

```python
def initializePage(self) -> None
```

```python
def isComplete(self) -> bool
```

### `CameraCalibrationPage`

```python
class CameraCalibrationPage(SimulatedCalibrationPage):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, state: CalibrationWorkflowState) -> None
```

### `RobotCalibrationPage`

```python
class RobotCalibrationPage(SimulatedCalibrationPage):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, state: CalibrationWorkflowState) -> None
```

### `CameraTcpOffsetPage`

```python
class CameraTcpOffsetPage(SimulatedCalibrationPage):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, state: CalibrationWorkflowState) -> None
```

### `PhysicalPointAlignmentPage`

```python
class PhysicalPointAlignmentPage(CalibrationWizardPage):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, state: CalibrationWorkflowState) -> None
```

```python
def initializePage(self) -> None
```

```python
def isComplete(self) -> bool
```

```python
def update_current_pose(self) -> None
```

### `FinishPage`

```python
class FinishPage(CalibrationWizardPage):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, state: CalibrationWorkflowState) -> None
```

```python
def initializePage(self) -> None
```

```python
def isComplete(self) -> bool
```

### `create_calibration_workflow_wizard`

```python
def create_calibration_workflow_wizard(state: CalibrationWorkflowState | None=None) -> ConfigurableWizard
```

### `_install_wizard_buttons`

```python
def _install_wizard_buttons(wizard: ConfigurableWizard) -> None
```

### `_install_jog_drawer`

```python
def _install_jog_drawer(wizard: ConfigurableWizard, state: CalibrationWorkflowState, pages: list[QWizardPage]) -> None
```

### `_wire_step_button_gating`

```python
def _wire_step_button_gating(wizard: ConfigurableWizard, pages: list[QWizardPage]) -> None
```

### `main`

```python
def main() -> int
```

## `charuco_live.py`

Source: [scripts/charuco_live.py](../../scripts/charuco_live.py).

Live ChArUco detection using the paint system's VisionService. Detector and calibrator come from the engine module: src.engine.vision.implementation.VisionSystem.features.calibration.charuco Board parameters — edit the constants below to match your physical board. Press q to quit.

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `cv2`, `numpy`, `os`, `src.engine.common_settings_ids`, `src.engine.core.message_broker`, `src.engine.repositories.settings_service_factory`, `src.engine.vision.implementation.VisionSystem.VisionSystem`, `src.engine.vision.implementation.VisionSystem.core.service.internal_service`, `src.engine.vision.implementation.VisionSystem.features.calibration.charuco`, `src.engine.vision.vision_service`, `src.engine.work_areas.work_area_service`, `src.robot_systems.paint.paint_robot_system`, `sys`, `time`.

Module declarations (expressions are shown without evaluating them):

```python
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SQUARES_X = 19
SQUARES_Y = 12
SQUARE_LENGTH = 0.015
MARKER_LENGTH = 0.011
DICT_ID = cv2.aruco.DICT_4X4_1000
```

### `_build_vision`

```python
def _build_vision() -> VisionService
```

### `_overlay`

```python
def _overlay(frame: np.ndarray, text: str, good: bool) -> np.ndarray
```

### `main`

```python
def main() -> None
```

## `charuco_test.py`

Source: [scripts/charuco_test.py](../../scripts/charuco_test.py).

Imports (including optional/function-local imports; not a startup dependency list): `cv2`, `dataclasses`, `numpy`, `pathlib`, `typing`.

### `DetectionResult`

```python
@dataclass
class DetectionResult:
```

Declared fields/defaults:

```python
mode: str
charuco_corners: Optional[np.ndarray]
charuco_ids: Optional[np.ndarray]
marker_corners: Tuple[np.ndarray, ...]
marker_ids: Optional[np.ndarray]
vis: np.ndarray
rvec: Optional[np.ndarray]
tvec: Optional[np.ndarray]
```

### `CharucoBoardDetector`

```python
class CharucoBoardDetector:
```

Single ChArUco detector for one board convention.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, squares_x: int=5, squares_y: int=6, square_length: float=0.04, marker_length: float=0.02, dictionary_id: int=cv2.aruco.DICT_4X4_50, legacy_pattern: bool=False) -> None
```

```python
def generate_board_image(self, out_size: Tuple[int, int]=(900, 1100), margin_size: int=20, border_bits: int=1) -> np.ndarray
```

```python
def detect_raw(self, image: np.ndarray)
```

### `AutoCharucoBoardDetector`

```python
class AutoCharucoBoardDetector:
```

Try new convention first, then legacy convention, and keep the better result. Also estimates board pose and draws coordinate axes when enough ChArUco corners are detected.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, squares_x: int=5, squares_y: int=6, square_length: float=0.04, marker_length: float=0.02, dictionary_id: int=cv2.aruco.DICT_4X4_50) -> None
```

```python
def detect(self, image: np.ndarray) -> DetectionResult
```

### `CharucoCalibrator`

```python
class CharucoCalibrator:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, board)
```

```python
def add_frame(self, image: np.ndarray, charuco_corners, charuco_ids) -> bool
```

```python
def calibrate(self)
```

### `put_label`

```python
def put_label(img: np.ndarray, text: str) -> np.ndarray
```

### `create_partial_view`

```python
def create_partial_view(board_img: np.ndarray, canvas_size=(1200, 900), mode: str='left_cut') -> np.ndarray
```

### `print_detection_stats`

```python
def print_detection_stats(title: str, result: DetectionResult) -> None
```

### `run_fake_calibration_smoke_test`

```python
def run_fake_calibration_smoke_test(auto_detector: AutoCharucoBoardDetector, board_img: np.ndarray) -> None
```

### `run_real_image_test`

```python
def run_real_image_test(image_path: str, auto_detector: AutoCharucoBoardDetector, output_dir: Path) -> None
```

### `run_example`

```python
def run_example(example_name: str, board_img: np.ndarray, auto_detector: AutoCharucoBoardDetector, output_dir: Path) -> None
```

## `charucoboard_detection_test.py`

Source: [scripts/charucoboard_detection_test.py](../../scripts/charucoboard_detection_test.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtGui`, `PyQt6.QtWidgets`, `__future__`, `cv2`, `datetime`, `numpy`, `os`, `pickle`, `src.engine.common_settings_ids`, `src.engine.core.message_broker`, `src.engine.repositories.settings_service_factory`, `src.engine.vision.implementation.VisionSystem.VisionSystem`, `src.engine.vision.implementation.VisionSystem.core.service.internal_service`, `src.engine.vision.vision_service`, `src.engine.work_areas.work_area_service`, `src.robot_systems.glue.glue_robot_system`, `sys`, `threading`, `time`.

Module declarations (expressions are shown without evaluating them):

```python
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
```

### `_build_vision_service`

```python
def _build_vision_service() -> VisionService
```

### `_Bridge`

```python
class _Bridge(QObject):
```

Declared fields/defaults:

```python
frame_ready = pyqtSignal(object, str, bool)
capture_added = pyqtSignal(int)
```

### `_Collector`

```python
class _Collector:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, vision: VisionService) -> None
```

```python
def configure(self, cols: int, rows: int, square_mm: float, marker_mm: float, dict_name: str, auto_capture: bool) -> None
```

```python
def request_capture(self) -> None
```

```python
def clear_frames(self) -> None
```

```python
def get_frame_count(self) -> int
```

```python
def calibrate(self) -> tuple[bool, str]
```

```python
def start(self) -> None
```

```python
def stop(self) -> None
```

### `_MainWindow`

```python
class _MainWindow(QMainWindow):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, vision: VisionService) -> None
```

```python
def closeEvent(self, event) -> None
```

### `main`

```python
def main() -> None
```

## `example.py`

Source: [scripts/example.py](../../scripts/example.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtGui`, `PyQt6.QtWidgets`, `cv2`, `numpy`, `pathlib`, `scipy.optimize`, `src.engine.common_service_ids`, `src.engine.core.message_broker`, `src.engine.repositories.settings_service_factory`, `src.engine.work_areas.work_area_service`, `src.robot_systems.default_service_builders`, `src.robot_systems.paint.paint_robot_system`, `sys`, `types`.

Module declarations (expressions are shown without evaluating them):

```python
REPO_ROOT = Path(__file__).resolve().parents[1]
ACTIVE_WORK_AREA = 'paint'
MIN_CONTOUR_AREA = 500
RESAMPLE_SPACING = 1.0
CORNER_EPSILON_RATIO = 0.004
BEZIER_MAX_ERROR = 1.5
BEZIER_MIN_POINTS = 10
BEZIER_MAX_DEPTH = 10
BLUR_KERNEL = (5, 5)
MORPH_KERNEL_SIZE = 3
MORPH_CLOSE_ITERATIONS = 2
MORPH_OPEN_ITERATIONS = 1
ORIGINAL_CONTOUR_COLOR = (0, 0, 255)
ORIGINAL_CONTOUR_THICKNESS = 1
SMOOTH_CONTOUR_COLOR = (0, 255, 0)
SMOOTH_CONTOUR_THICKNESS = 2
CORNER_COLOR = (255, 0, 0)
CORNER_RADIUS = 4
DEVIATION_THRESHOLD_PX = 2.0
DEVIATION_COLOR = (0, 165, 255)
DEVIATION_RADIUS = 3
SAVE_CAPTURED_IMAGE = True
OUTPUT_FILENAME = 'captured_bezier_contour.png'
```

### `resample_closed_contour`

```python
def resample_closed_contour(contour, spacing=RESAMPLE_SPACING)
```

### `find_corner_indices`

```python
def find_corner_indices(dense_pts, contour)
```

### `split_closed_points`

```python
def split_closed_points(points, corner_indices)
```

### `bezier`

```python
def bezier(t, p0, p1, p2, p3)
```

### `fit_cubic_bezier`

```python
def fit_cubic_bezier(points)
```

### `adaptive_bezier_fit`

```python
def adaptive_bezier_fit(points, depth=0)
```

### `sample_bezier_segment`

```python
def sample_bezier_segment(ctrl)
```

### `smooth_contour_with_beziers`

```python
def smooth_contour_with_beziers(contour)
```

### `process_frame`

```python
def process_frame(frame, contours)
```

### `normalize_contour`

```python
def normalize_contour(contour)
```

### `pick_largest_contour`

```python
def pick_largest_contour(contours)
```

### `contour_for_cv`

```python
def contour_for_cv(contour)
```

### `contour_for_drawing`

```python
def contour_for_drawing(contour)
```

### `polyline_for_drawing`

```python
def polyline_for_drawing(points)
```

### `min_rect_metrics`

```python
def min_rect_metrics(points)
```

### `normalize_rect_angle`

```python
def normalize_rect_angle(angle)
```

### `rect_angle_delta`

```python
def rect_angle_delta(before, after)
```

### `contour_deviation_metrics`

```python
def contour_deviation_metrics(raw_points, processed_points)
```

### `point_to_polyline_distances`

```python
def point_to_polyline_distances(points, polyline, closed)
```

### `print_min_rect_comparison`

```python
def print_min_rect_comparison(raw_rect, processed_rect, deviation)
```

### `draw_min_rect`

```python
def draw_min_rect(frame, rect, color, label)
```

### `draw_deviation_points`

```python
def draw_deviation_points(frame, deviation)
```

### `draw_min_rect_text`

```python
def draw_min_rect_text(frame, raw_rect, processed_rect, deviation)
```

### `ensure_bgr`

```python
def ensure_bgr(frame)
```

### `build_paint_vision_service`

```python
def build_paint_vision_service(active_area=ACTIVE_WORK_AREA)
```

### `CameraApp`

```python
class CameraApp(QWidget):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self)
```

```python
def update_camera(self)
```

```python
def capture(self)
```

```python
def show_image(self, label, frame)
```

```python
def closeEvent(self, event)
```

## `example_tcp_calib.py`

Source: [scripts/example_tcp_calib.py](../../scripts/example_tcp_calib.py).

Imports (including optional/function-local imports; not a startup dependency list): `json`, `math`, `numpy`.

Module declarations (expressions are shown without evaluating them):

```python
JSON_FILE = '/home/ilv/Desktop/robot_app_platform/scripts/example_tcp_calib_samples.json'
PARENT_FRAME = 'tool0'
CHILD_FRAME = 'tool_tcp'
ROTATION_FORMAT = 'rpy'
```

### `rpy_deg_to_rot`

```python
def rpy_deg_to_rot(rx_deg, ry_deg, rz_deg)
```

Convert roll, pitch, yaw in degrees to a rotation matrix. Convention: R = Rz(yaw) @ Ry(pitch) @ Rx(roll) This matches the usual URDF fixed-axis rpy convention.

### `rotvec_deg_to_rot`

```python
def rotvec_deg_to_rot(rx_deg, ry_deg, rz_deg)
```

Convert rotation vector in degrees to a rotation matrix. The vector direction is the rotation axis. The vector magnitude is the rotation angle in degrees.

### `read_samples_json`

```python
def read_samples_json(path)
```

JSON format: [ {"x": 412.1, "y": 103.2, "z": 522.4, "rx": 12.0, "ry": -43.0, "rz": 91.0}, ... ] x, y, z are in millimeters. rx, ry, rz are in degrees.

### `solve_tcp`

```python
def solve_tcp(samples, rotation_format)
```

Each sample must be the transform: base -> tool0 The math solves: R_i * tcp_in_tool0 + p_i = fixed_touch_point Unknowns: tcp_in_tool0 fixed_touch_point

### `print_result`

```python
def print_result(result)
```

### `main`

```python
def main()
```

## `flatten_directory.py`

Source: [scripts/flatten_directory.py](../../scripts/flatten_directory.py).

List or copy every file in a directory tree into one flat directory.

Imports (including optional/function-local imports; not a startup dependency list): `collections`, `os`, `pathlib`, `shutil`.

Module declarations (expressions are shown without evaluating them):

```python
START_DIRECTORY = Path('/home/ilv/Desktop/robot_app_platform')
DESTINATION_DIRECTORY = Path('/home/ilv/Desktop/test')
COPY_FILES = False
EXCLUDED_DIRECTORY_NAMES = {'.git', '.venv', '__pycache__'}
```

### `_flat_name`

```python
def _flat_name(path: Path, start: Path, used_names: set[str]) -> str
```

### `flatten_files`

```python
def flatten_files(start: Path, destination: Path, copy_files: bool=False) -> None
```

## `generate_charuco_board.py`

Source: [scripts/generate_charuco_board.py](../../scripts/generate_charuco_board.py).

Imports (including optional/function-local imports; not a startup dependency list): `cv2`, `matplotlib.pyplot`.

Module declarations (expressions are shown without evaluating them):

```python
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_250)
squares_x = 11
squares_y = 8
square_length_mm = 18.0
marker_length_mm = 12.0
board = cv2.aruco.CharucoBoard((squares_x, squares_y), square_length_mm, marker_length_mm, aruco_dict)
board_w_mm = squares_x * square_length_mm
board_h_mm = squares_y * square_length_mm
page_w_mm = 297.0
page_h_mm = 210.0
dpi = 300
board_w_px = int(round(board_w_mm / 25.4 * dpi))
board_h_px = int(round(board_h_mm / 25.4 * dpi))
img = board.generateImage((board_w_px, board_h_px))
fig = plt.figure(figsize=(page_w_mm / 25.4, page_h_mm / 25.4), dpi=dpi)
ax = fig.add_axes([0, 0, 1, 1])
x0_mm = (page_w_mm - board_w_mm) / 2.0
y0_mm = (page_h_mm - board_h_mm) / 2.0
```

## `laser_on_off.py`

Source: [scripts/laser_on_off.py](../../scripts/laser_on_off.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `argparse`, `json`, `pathlib`, `src.engine.hardware.communication.modbus.modbus`, `src.engine.hardware.laser`, `src.engine.hardware.vacuum_pump.modbus.modbus_vacuum_pump_transport`, `src.engine.hardware.xinje`, `sys`, `time`.

Module declarations (expressions are shown without evaluating them):

```python
ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / 'src' / 'robot_systems' / 'paint' / 'storage' / 'settings' / 'hardware' / 'modbus.json'
DEFAULT_REGISTER = 'Y5'
```

### `_load_modbus_config`

```python
def _load_modbus_config(path: Path) -> ModbusConfig
```

### `_parse_output_point`

```python
def _parse_output_point(value: str) -> int | str
```

### `_format_output_point`

```python
def _format_output_point(point: int | str) -> str
```

### `_parse_args`

```python
def _parse_args() -> argparse.Namespace
```

### `_build_transport`

```python
def _build_transport(config: ModbusConfig) -> ModbusVacuumPumpTransport
```

### `main`

```python
def main() -> int
```

## `live_camera_crosshair.py`

Source: [scripts/live_camera_crosshair.py](../../scripts/live_camera_crosshair.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `argparse`, `cv2`, `numpy`, `os`, `src.engine.common_settings_ids`, `src.engine.core.message_broker`, `src.engine.repositories.settings_service_factory`, `src.engine.vision.implementation.VisionSystem.VisionSystem`, `src.engine.vision.implementation.VisionSystem.core.service.internal_service`, `src.engine.vision.vision_service`, `src.engine.work_areas.work_area_service`, `src.robot_systems.glue.glue_robot_system`, `sys`, `time`.

Module declarations (expressions are shown without evaluating them):

```python
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
```

### `_build_vision_service`

```python
def _build_vision_service(active_area: str | None) -> VisionService
```

### `_draw_crosshair`

```python
def _draw_crosshair(frame: np.ndarray, color: tuple[int, int, int], size: int, thickness: int) -> np.ndarray
```

### `main`

```python
def main() -> int
```

## `migrate_global_calibration_to_work_area.py`

Source: [scripts/migrate_global_calibration_to_work_area.py](../../scripts/migrate_global_calibration_to_work_area.py).

Copy the current global calibration into a named work-area profile. This utility is intentionally independent of the platform runtime and uses only the Python standard library. The original global calibration is never modified.

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `argparse`, `json`, `os`, `pathlib`, `shutil`, `tempfile`.

Module declarations (expressions are shown without evaluating them):

```python
ARTIFACT_SUFFIXES = ('.npy', '_homography_residual.json', '_geometry_scale.json', '_model_report.json')
```

### `_artifact_path`

```python
def _artifact_path(matrix_path: Path, suffix: str) -> Path
```

### `_atomic_copy`

```python
def _atomic_copy(source: Path, destination: Path) -> None
```

### `_atomic_write_json`

```python
def _atomic_write_json(path: Path, payload: dict) -> None
```

### `migrate`

```python
def migrate(args: argparse.Namespace) -> None
```

### `main`

```python
def main() -> None
```

## `network_connect.py`

Source: [scripts/network_connect.py](../../scripts/network_connect.py).

Standalone launcher for the shared Network Settings application. Run from the repository root with ``python scripts/network_connect.py``.

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtWidgets`, `pathlib`, `src.applications.network_settings.network_settings_factory`, `src.applications.network_settings.service.network_settings_service`, `sys`.

### `main`

```python
def main() -> None
```

## `paint_motion_plane_probe.py`

Source: [scripts/paint_motion_plane_probe.py](../../scripts/paint_motion_plane_probe.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtGui`, `PyQt6.QtWidgets`, `__future__`, `dataclasses`, `json`, `math`, `pl_gui.settings.settings_view.styles`, `pl_gui.utils.utils_widgets.wizards`, `src.applications.base.drawer_toggle`, `src.applications.base.robot_jog_widget`, `src.applications.base.styled_message_box`, `sys`, `typing`.

Module declarations (expressions are shown without evaluating them):

```python
AXES = ('x', 'y', 'z')
ROT_AXES = ('rx', 'ry', 'rz')
LINEAR_JOG_BUTTONS = ('btn_x_plus', 'btn_x_minus', 'btn_y_plus', 'btn_y_minus', 'btn_z_plus', 'btn_z_minus')
ROTATION_JOG_BUTTONS = ('btn_rx_plus', 'btn_rx_minus', 'btn_ry_plus', 'btn_ry_minus', 'btn_rz_plus', 'btn_rz_minus')
ROTATION_PLANES = {'rx': (('y', 'z'), 'x'), 'ry': (('x', 'z'), 'y'), 'rz': (('x', 'y'), 'z')}
```

### `_action_button`

```python
def _action_button(text: str) -> QPushButton
```

### `_ghost_button`

```python
def _ghost_button(text: str) -> QPushButton
```

### `_label`

```python
def _label(text: str) -> QLabel
```

### `Pose6D`

```python
@dataclass(frozen=True)
class Pose6D:
```

Declared fields/defaults:

```python
x: float
y: float
z: float
rx: float
ry: float
rz: float
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def position_delta(self, other: 'Pose6D') -> dict[str, float]
```

```python
def rotation_delta(self, other: 'Pose6D') -> dict[str, float]
```

```python
def as_list(self) -> list[float]
```

### `PlaneInference`

```python
@dataclass(frozen=True)
class PlaneInference:
```

Declared fields/defaults:

```python
translation_axis: str
translation_direction: str
rotation_axis: str
planar_axes: tuple[str, str]
fixed_axis: str
suggested_plane_key: str
axis_offsets_deg: dict[str, float]
warnings: tuple[str, ...]
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def as_config(self) -> dict
```

```python
def as_plane_object(self) -> dict
```

### `unwrap_degrees`

```python
def unwrap_degrees(reference: float, value: float) -> float
```

### `dominant_axis`

```python
def dominant_axis(deltas: dict[str, float], *, min_abs: float) -> tuple[str, float] | None
```

### `infer_plane`

```python
def infer_plane(reference_pose: Pose6D, translation_pose: Pose6D, rotation_pose: Pose6D, *, fixed_axis_override: str | None=None, min_translation_mm: float=1.0, min_rotation_deg: float=1.0) -> PlaneInference
```

### `PoseEditor`

```python
class PoseEditor(QWidget):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, title: str, initial: Iterable[float]=(0, 0, 300, 180, 0, 0)) -> None
```

```python
def pose(self) -> Pose6D
```

```python
def set_pose(self, pose: Pose6D) -> None
```

### `PoseReadout`

```python
class PoseReadout(QWidget):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, title: str, initial: Iterable[float]=(0, 0, 300, 180, 0, 0)) -> None
```

```python
def pose(self) -> Pose6D
```

```python
def set_pose(self, pose: Pose6D) -> None
```

### `GuideIllustration`

```python
class GuideIllustration(QWidget):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, mode: str, parent=None) -> None
```

```python
def sizeHint(self) -> QSize
```

```python
def set_selected_axis(self, axis: str | None, delta: float=0.0) -> None
```

```python
def paintEvent(self, _event) -> None
```

### `ProbeState`

```python
@dataclass
class ProbeState:
```

Declared fields/defaults:

```python
current_pose: Pose6D = field(default_factory=lambda: Pose6D(100, -300, 300, 180, 0, 0))
paint_pose: Pose6D = field(default_factory=lambda: Pose6D(100, -300, 300, 180, 0, 0))
reference_pose: Pose6D = field(default_factory=lambda: Pose6D(100, -300, 300, 180, 0, 0))
translation_pose: Pose6D = field(default_factory=lambda: Pose6D(140, -300, 300, 180, 0, 0))
rotation_pose: Pose6D = field(default_factory=lambda: Pose6D(100, -300, 300, 180, 10, 0))
paint_position_reached: bool = False
reference_captured: bool = False
translation_captured: bool = False
rotation_captured: bool = False
fixed_axis: str | None = None
inference: PlaneInference | None = None
```

### `_pose_group`

```python
def _pose_group(title: str, widget: QWidget) -> QGroupBox
```

### `ProbeWizardPage`

```python
class ProbeWizardPage(QWizardPage):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, state: ProbeState, title: str, info_text: str) -> None
```

```python
def set_pose_changed_callback(self, callback) -> None
```

### `MoveToPaintPositionPage`

```python
class MoveToPaintPositionPage(ProbeWizardPage):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, state: ProbeState) -> None
```

```python
def initializePage(self) -> None
```

```python
def isComplete(self) -> bool
```

```python
def validatePage(self) -> bool
```

### `ReferencePage`

```python
class ReferencePage(ProbeWizardPage):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, state: ProbeState) -> None
```

```python
def initializePage(self) -> None
```

```python
def isComplete(self) -> bool
```

```python
def validatePage(self) -> bool
```

### `JogTranslationPage`

```python
class JogTranslationPage(ProbeWizardPage):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, state: ProbeState) -> None
```

```python
def initializePage(self) -> None
```

```python
def isComplete(self) -> bool
```

```python
def validatePage(self) -> bool
```

### `JogRotationPage`

```python
class JogRotationPage(ProbeWizardPage):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, state: ProbeState) -> None
```

```python
def initializePage(self) -> None
```

```python
def isComplete(self) -> bool
```

```python
def validatePage(self) -> bool
```

### `FixedAxisPage`

```python
class FixedAxisPage(ProbeWizardPage):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, state: ProbeState) -> None
```

```python
def initializePage(self) -> None
```

```python
def isComplete(self) -> bool
```

```python
def validatePage(self) -> bool
```

### `InferencePage`

```python
class InferencePage(ProbeWizardPage):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, state: ProbeState) -> None
```

```python
def initializePage(self) -> None
```

### `create_probe_wizard`

```python
def create_probe_wizard(state: ProbeState | None=None) -> ConfigurableWizard
```

### `_install_probe_jog_drawer`

```python
def _install_probe_jog_drawer(wizard: ConfigurableWizard, state: ProbeState, pages: list[QWizardPage]) -> None
```

### `_wire_step_button_gating`

```python
def _wire_step_button_gating(wizard: ConfigurableWizard, pages: list[QWizardPage]) -> None
```

### `main`

```python
def main() -> int
```

## `paint_web_jog.py`

Source: [scripts/paint_web_jog.py](../../scripts/paint_web_jog.py).

Small, mobile-friendly web pendant for the paint robot. Run from the repository root, then open the printed URL on a phone connected to the same trusted LAN. Each button tap performs one configured Cartesian step. Authentication is disabled by default; pass ``--token`` to enable it.

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `argparse`, `atexit`, `flask`, `pathlib`, `secrets`, `src.applications.base.robot_jog_service`, `src.engine.robot.drivers.ros2_robot`, `src.robot_systems.paint.bootstrap_provider`, `sys`.

Module declarations (expressions are shown without evaluating them):

```python
LINEAR_AXES = {'X', 'Y', 'Z'}
ROTARY_AXES = {'RX', 'RY', 'RZ'}
LINEAR_STEPS = (0.1, 0.2, 0.5, 1.0, 5.0, 10.0, 50.0, 100.0, 250.0)
ROTARY_STEPS = (0.1, 0.2, 0.5, 1.0, 5.0, 10.0, 45.0, 90.0, 180.0, 360.0)
PAGE = '<!doctype html>\n<html lang="en">\n<head>\n  <meta charset="utf-8">\n  <meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no">\n  <title>Paint Robot Jog</title>\n  <style>\n    :root { color-scheme: dark; --accent:#a975c1; --stop:#c62828; --panel:#20242b; }\n    * { box-sizing:border-box; -webkit-tap-highlight-color:transparent; }\n    body { margin:0; background:#111419; color:#f4f5f6; font:16px system-ui,sans-serif; touch-action:manipulation; }\n    main { width:min(720px,100%); margin:auto; padding:16px; }\n    h1 { margin:0 0 12px; font-size:1.4rem; }\n    .status,.controls,.axis { background:var(--panel); border-radius:14px; padding:14px; margin-bottom:12px; }\n    .status { display:flex; justify-content:space-between; gap:10px; }\n    #state.ok { color:#75d47f; } #state.bad { color:#ff7770; }\n    label { display:grid; gap:6px; }\n    input[type=range] { width:100%; min-height:44px; accent-color:var(--accent); }\n    .axis { display:grid; grid-template-columns:1fr 62px 1fr; align-items:center; gap:10px; }\n    .axis span { text-align:center; font-weight:700; }\n    button { min-height:64px; border:0; border-radius:12px; color:white; background:var(--accent); font-size:1.35rem; font-weight:800; user-select:none; }\n    button.active { filter:brightness(1.35); transform:scale(.98); }\n    button:disabled { opacity:.45; }\n    #stop { width:100%; background:var(--stop); min-height:72px; margin-top:2px; }\n    #pose { margin-top:8px; color:#bbc0c8; font:0.86rem ui-monospace,monospace; overflow-wrap:anywhere; }\n    .hint { color:#bbc0c8; font-size:.88rem; line-height:1.35; }\n  </style>\n</head>\n<body><main>\n  <h1>Paint Robot Jog</h1>\n  <section class="status"><span>Robot</span><strong id="state">Checking…</strong></section>\n  <section class="controls">\n    <label>Linear step: <b><span id="linearValue">1</span> mm</b>\n      <input id="linear" type="range" min="0" max="8" step="1" value="3">\n    </label>\n    <label>Rotation step: <b><span id="rotaryValue">1</span>°</b>\n      <input id="rotary" type="range" min="0" max="9" step="1" value="3">\n    </label>\n    <div id="pose">Pose: —</div>\n  </section>\n  <div id="axes"></div>\n  <button id="stop">STOP MOTION</button>\n  <p class="hint">Each tap performs one step. Wait for the move to finish before tapping again. Keep the physical emergency stop within reach.</p>\n</main>\n<script>\nconst token = new URLSearchParams(location.search).get(\'token\') || \'\';\nconst headers = {\'Content-Type\':\'application/json\', \'X-Jog-Token\':token};\nconst axes = [\'X\',\'Y\',\'Z\',\'RX\',\'RY\',\'RZ\'];\nconst linearSteps = [0.1,0.2,0.5,1,5,10,50,100,250];\nconst rotarySteps = [0.1,0.2,0.5,1,5,10,45,90,180,360];\nconst axesRoot = document.querySelector(\'#axes\');\nlet moving = false;\n\nfor (const axis of axes) {\n  const row = document.createElement(\'section\'); row.className = \'axis\';\n  row.innerHTML = `<button data-axis="${axis}" data-direction="MINUS">−</button><span>${axis}</span><button data-axis="${axis}" data-direction="PLUS">+</button>`;\n  axesRoot.append(row);\n}\nfor (const id of [\'linear\',\'rotary\']) {\n  const slider=document.querySelector(\'#\'+id), output=document.querySelector(\'#\'+id+\'Value\');\n  const values=id===\'linear\'?linearSteps:rotarySteps;\n  slider.addEventListener(\'input\',()=>output.textContent=values[Number(slider.value)]);\n}\nasync function api(path, body={}) {\n  const response = await fetch(path,{method:\'POST\',headers,body:JSON.stringify(body),cache:\'no-store\'});\n  if (!response.ok) throw new Error((await response.json().catch(()=>({}))).error || response.statusText);\n  return response.json();\n}\nfunction setMoving(value, button=null) {\n  moving=value;\n  document.querySelectorAll(\'[data-axis]\').forEach(item=>item.disabled=value);\n  button?.classList.toggle(\'active\', value);\n}\nasync function step(button) {\n  if (moving) return;\n  const axis=button.dataset.axis;\n  const isLinear=axes.slice(0,3).includes(axis);\n  const slider=document.querySelector(isLinear?\'#linear\':\'#rotary\');\n  const amount=(isLinear?linearSteps:rotarySteps)[Number(slider.value)];\n  setMoving(true, button);\n  try {\n    await api(\'/api/jog/step\',{axis,direction:button.dataset.direction,step:amount});\n  } catch (error) { showError(error); }\n  finally { setMoving(false, button); updateState(); }\n}\nasync function stop() {\n  try { await api(\'/api/jog/stop\'); } catch (error) { showError(error); }\n  setMoving(false);\n}\nfunction showError(error) { const s=document.querySelector(\'#state\'); s.textContent=error.message; s.className=\'bad\'; }\ndocument.querySelectorAll(\'[data-axis]\').forEach(button=>{\n  button.addEventListener(\'click\',()=>step(button));\n  button.addEventListener(\'contextmenu\',event=>event.preventDefault());\n});\ndocument.querySelector(\'#stop\').addEventListener(\'click\',stop);\nwindow.addEventListener(\'pagehide\',()=>navigator.sendBeacon(\'/api/jog/stop?token=\'+encodeURIComponent(token)));\nasync function updateState() {\n  try {\n    const r=await fetch(\'/api/state\',{headers:{\'X-Jog-Token\':token},cache:\'no-store\'}), data=await r.json();\n    if(!r.ok) throw new Error(data.error||r.statusText);\n    const s=document.querySelector(\'#state\'); s.textContent=data.connected?\'Connected\':\'Unavailable\'; s.className=data.connected?\'ok\':\'bad\';\n    document.querySelector(\'#pose\').textContent=\'Pose: \'+(data.position?.map(v=>Number(v).toFixed(2)).join(\', \')||\'—\');\n  } catch(error) { showError(error); }\n}\nupdateState(); setInterval(updateState,1000);\n</script></body></html>'
```

### `JogRuntime`

```python
class JogRuntime:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, server_url: str, tool: int, user: int) -> None
```

```python
def step(self, axis: str, direction: str, amount: float) -> None
```

```python
def stop(self) -> None
```

### `create_app`

```python
def create_app(runtime: JogRuntime, token: str | None=None) -> Flask
```

### `main`

```python
def main() -> None
```

## `plate_workpiece_placer.py`

Source: [scripts/plate_workpiece_placer.py](../../scripts/plate_workpiece_placer.py).

Calculate sequential workpiece-center positions on a rectangular plate. Coordinates use the plate's local coordinate system with (0, 0) at its bottom-left corner. Workpieces are placed left-to-right, then bottom-to-top.

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `argparse`, `dataclasses`, `math`, `matplotlib.patches`, `matplotlib.pyplot`, `pathlib`.

### `PlateLayout`

```python
@dataclass(frozen=True)
class PlateLayout:
```

Declared fields/defaults:

```python
width_mm: float
height_mm: float
margin_left_mm: float = 0.0
margin_right_mm: float = 0.0
margin_bottom_mm: float = 0.0
margin_top_mm: float = 0.0
spacing_x_mm: float = 0.0
spacing_y_mm: float = 0.0
robot_corners_xy: tuple[tuple[float, float], ...] | None = None
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def from_robot_corners(cls, corners_xy: list[tuple[float, float]] | tuple[tuple[float, float], ...], **options: float) -> 'PlateLayout'
```

Build a plate from BL, BR, TR, TL corners measured in robot XY.

```python
def to_output_xy(self, local_x_mm: float, local_y_mm: float) -> tuple[float, float]
```

Map plate-local millimetres to robot XY when corners are configured.

### `Placement`

```python
@dataclass(frozen=True)
class Placement:
```

Declared fields/defaults:

```python
width_mm: float
height_mm: float
center_x_mm: float
center_y_mm: float
```

### `PlateWorkpiecePlacer`

```python
class PlateWorkpiecePlacer:
```

Stateful shelf-layout placer supporting different workpiece sizes.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, layout: PlateLayout) -> None
```

```python
def reset(self) -> None
```

Forget prior placements and restart at the bottom-left margin.

```python
def place_workpiece(self, workpiece_width_mm: float, workpiece_height_mm: float) -> tuple[float, float] | None
```

Return the next workpiece center, or ``None`` if it cannot fit. A failed placement does not modify the current layout state.

```python
def visualize(self, *, output_path: str | Path | None=None, show: bool=True) -> None
```

Draw the current layout and optionally save it as an image.

### `_distance`

```python
def _distance(first: tuple[float, float], second: tuple[float, float]) -> float
```

### `main`

```python
def main() -> None
```

## `publish_changes.py`

Source: [scripts/publish_changes.py](../../scripts/publish_changes.py).

Commit selected changes, publish through SVN, then push rewritten history to Git. Run from this checkout (paths are relative to your current directory): python3 platform/scripts/publish_changes.py --all -m "Describe the change" python3 platform/scripts/publish_changes.py -m "Describe staged changes" python3 platform/scripts/publish_changes.py --resume Add --dry-run to inspect the plan without staging, committing or publishing.

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `argparse`, `pathlib`, `shlex`, `subprocess`, `sys`.

### `PublicationError`

```python
class PublicationError(RuntimeError):
```

A precondition or publication step failed.

### `Git`

```python
class Git:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, root: Path) -> None
```

```python
def read(self, *args: str, allowed: tuple[int, ...]=(0,)) -> str
```

```python
def run(self, *args: str) -> None
```

### `resolve_paths`

```python
def resolve_paths(root: Path, paths: list[str]) -> list[str]
```

### `ensure_clean`

```python
def ensure_clean(git: Git) -> None
```

### `publish`

```python
def publish(git: Git, args: argparse.Namespace, paths: list[str]) -> None
```

### `parse_args`

```python
def parse_args(argv: list[str] | None=None) -> argparse.Namespace
```

### `main`

```python
def main(argv: list[str] | None=None) -> int
```

## `raw_http_camera_viewer.py`

Source: [scripts/raw_http_camera_viewer.py](../../scripts/raw_http_camera_viewer.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `cv2`, `time`.

Module declarations (expressions are shown without evaluating them):

```python
STREAM_URL = 'http://192.168.222.178:5000/video_feed'
WINDOW_NAME = 'Raw HTTP Camera Viewer'
```

### `main`

```python
def main() -> int
```

## `raw_http_camera_viewer_requests.py`

Source: [scripts/raw_http_camera_viewer_requests.py](../../scripts/raw_http_camera_viewer_requests.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `cv2`, `numpy`, `requests`, `time`.

Module declarations (expressions are shown without evaluating them):

```python
STREAM_URL = 'http://192.168.222.35:5001/video_feed'
WINDOW_NAME = 'Raw HTTP Camera Viewer (requests)'
CHUNK_SIZE = 16384
```

### `_iter_jpegs`

```python
def _iter_jpegs(url: str)
```

### `main`

```python
def main() -> int
```

## `read_slave10_address0.py`

Source: [scripts/read_slave10_address0.py](../../scripts/read_slave10_address0.py).

Imports (including optional/function-local imports; not a startup dependency list): `logging`, `src.engine.hardware.communication.modbus.modbus_register_transport`.

Module declarations (expressions are shown without evaluating them):

```python
transport = ModbusRegisterTransport(port='/dev/ttyUSB0', slave_address=10, baudrate=57600, bytesize=8, stopbits=1, parity='N', timeout=0.5)
```

## `read_xinje_io.py`

Source: [scripts/read_xinje_io.py](../../scripts/read_xinje_io.py).

Read all Xinje MA-8X8YR inputs and outputs. Run from the repository root: .venv/bin/python scripts/read_xinje_io.py The script uses the configured Xinje slave from Paint's Modbus settings and does not write any outputs.

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `json`, `pathlib`, `src.engine.hardware.communication.modbus.modbus`, `src.engine.hardware.communication.transport_registry`, `src.engine.hardware.xinje`, `sys`.

Module declarations (expressions are shown without evaluating them):

```python
ROOT = Path(__file__).resolve().parents[1]
SETTINGS_DIR = ROOT / 'src' / 'robot_systems' / 'paint' / 'storage' / 'settings' / 'hardware'
MODBUS_PATH = SETTINGS_DIR / 'modbus.json'
```

### `load_modbus_config`

```python
def load_modbus_config() -> ModbusConfig
```

### `main`

```python
def main() -> None
```

## `run_paint_vision_isolated.py`

Source: [scripts/run_paint_vision_isolated.py](../../scripts/run_paint_vision_isolated.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `argparse`, `os`, `signal`, `src.engine.common_settings_ids`, `src.engine.repositories.settings_service_factory`, `src.engine.vision.implementation.VisionSystem.VisionSystem`, `src.engine.vision.implementation.VisionSystem.core.service.internal_service`, `src.engine.vision.vision_service`, `src.engine.work_areas.work_area_service`, `src.robot_systems.paint.paint_robot_system`, `sys`, `time`.

Module declarations (expressions are shown without evaluating them):

```python
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
```

### `_build_vision_service`

```python
def _build_vision_service(active_area: str | None) -> VisionService
```

### `_format_frame_shape`

```python
def _format_frame_shape(frame) -> str
```

### `main`

```python
def main() -> int
```

## `run_platform.py`

Source: [scripts/run_platform.py](../../scripts/run_platform.py).

Launch the PyQt application without OpenCV's bundled Qt environment.

Imports (including optional/function-local imports; not a startup dependency list): `cv2`, `os`, `pathlib`, `runpy`.

### `prepare_qt_environment`

```python
def prepare_qt_environment() -> None
```

Import OpenCV once, then restore the caller's Qt plugin/font settings.

## `sim_test.py`

Source: [scripts/sim_test.py](../../scripts/sim_test.py).

Imports (including optional/function-local imports; not a startup dependency list): `matplotlib.pyplot`, `numpy`.

Module declarations (expressions are shown without evaluating them):

```python
x_raw = 4.771315
y_raw = 54.873061
alpha = np.radians(16.2)
x_corr = x_raw * np.cos(alpha) - y_raw * np.sin(alpha)
y_corr = x_raw * np.sin(alpha) + y_raw * np.cos(alpha)
angles_deg = np.array([0, 15, 30, 45, 60, 75, 90])
angles_rad = np.radians(angles_deg)
target_world_x = 0.0
target_world_y = 250.0
uncorrected_x = []
uncorrected_y = []
corrected_x = [target_world_x] * len(angles_deg)
corrected_y = [target_world_y] * len(angles_deg)
```

## `test.py`

Source: [scripts/test.py](../../scripts/test.py).

Imports (including optional/function-local imports; not a startup dependency list): `minimalmodbus`, `time`.

Module declarations (expressions are shown without evaluating them):

```python
PORT = '/dev/ttyUSB0'
SLAVE_ID = 10
BAUDRATE = 57600
PARITY = 'N'
instrument = minimalmodbus.Instrument(PORT, SLAVE_ID)
```

## `test_paint_contour_interpolation_from_dump.py`

Source: [scripts/test_paint_contour_interpolation_from_dump.py](../../scripts/test_paint_contour_interpolation_from_dump.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `argparse`, `cv2`, `datetime`, `numpy`, `os`, `pathlib`, `src.engine.common_service_ids`, `src.engine.core.message_broker`, `src.engine.repositories.settings_service_factory`, `src.engine.work_areas.work_area_service`, `src.robot_systems.default_service_builders`, `src.robot_systems.paint.paint_robot_system`, `src.robot_systems.paint.processes.paint.plan.paint_contour_interpolation`, `sys`, `time`, `types`.

Module declarations (expressions are shown without evaluating them):

```python
REPO_ROOT = Path(__file__).resolve().parents[1]
WINDOW_NAME = 'Paint Contour Interpolation'
BUTTON_RECT = (16, 16, 176, 58)
DEFAULT_OUTPUT_DIR = REPO_ROOT / 'src' / 'bootstrap' / 'debug_plots'
```

### `CaptureButton`

```python
class CaptureButton:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self) -> None
```

```python
def on_mouse(self, event, x, y, _flags, _param) -> None
```

### `main`

```python
def main() -> int
```

### `_build_paint_vision_service`

```python
def _build_paint_vision_service(*, active_area: str)
```

### `_latest_frame`

```python
def _latest_frame(vision_service) -> np.ndarray | None
```

### `_latest_contours`

```python
def _latest_contours(vision_service) -> list[np.ndarray]
```

### `_capture_and_overlay`

```python
def _capture_and_overlay(*, frame: np.ndarray, contours: list[np.ndarray], interpolator: PaintContourInterpolation, output_dir: Path, save: bool) -> tuple[np.ndarray, str]
```

### `_pick_largest_contour`

```python
def _pick_largest_contour(contours: list[np.ndarray]) -> np.ndarray | None
```

### `_contour_to_pose_path`

```python
def _contour_to_pose_path(contour: np.ndarray) -> list[list[float]]
```

### `_ensure_bgr`

```python
def _ensure_bgr(frame: np.ndarray) -> np.ndarray
```

### `_draw_capture_button`

```python
def _draw_capture_button(frame: np.ndarray) -> None
```

### `_draw_status`

```python
def _draw_status(frame: np.ndarray, text: str) -> None
```

### `_draw_legend`

```python
def _draw_legend(frame: np.ndarray) -> None
```

### `_draw_polyline`

```python
def _draw_polyline(frame: np.ndarray, xy: np.ndarray, *, color: tuple[int, int, int], thickness: int) -> None
```

### `_draw_points`

```python
def _draw_points(frame: np.ndarray, xy: np.ndarray, *, color: tuple[int, int, int], radius: int) -> None
```

### `_spacing_summary`

```python
def _spacing_summary(xy: np.ndarray) -> str
```

## `test_paint_peripherals.py`

Source: [scripts/test_paint_peripherals.py](../../scripts/test_paint_peripherals.py).

Interactive manual test runner for Paint peripheral configuration. Run from the repository root: .venv/bin/python scripts/test_paint_peripherals.py No actuator is changed until an explicit ``on``, ``off``, or ``pulse`` command is entered.

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `json`, `logging`, `pathlib`, `src.engine.hardware.communication.modbus.modbus`, `src.engine.hardware.communication.transport_registry`, `src.engine.hardware.fan.modbus.modbus_fan_control`, `src.engine.hardware.laser`, `src.engine.hardware.peripherals`, `src.engine.hardware.physical_control_buttons.modbus.modbus_physical_control_buttons_factory`, `src.engine.hardware.vacuum_pump.models.vacuum_pump_config`, `src.engine.hardware.vacuum_pump.vacuum_pump_controller`, `src.engine.hardware.vacuum_sensor.models.vacuum_sensor_config`, `src.engine.hardware.vacuum_sensor.vacuum_sensor_service`, `src.engine.hardware.xinje`, `sys`, `time`.

Module declarations (expressions are shown without evaluating them):

```python
ROOT = Path(__file__).resolve().parents[1]
SETTINGS_DIR = ROOT / 'src' / 'robot_systems' / 'paint' / 'storage' / 'settings' / 'hardware'
MODBUS_PATH = SETTINGS_DIR / 'modbus.json'
PERIPHERALS_PATH = SETTINGS_DIR / 'peripherals.json'
```

### `load_configuration`

```python
def load_configuration() -> tuple[ModbusConfig, PeripheralConfig]
```

### `transport_for`

```python
def transport_for(modbus: ModbusConfig, slave_id: int)
```

### `build_devices`

```python
def build_devices(modbus: ModbusConfig, peripherals: PeripheralConfig) -> dict[str, object]
```

### `read_sensor`

```python
def read_sensor(device: VacuumSensorService) -> None
```

### `read_device`

```python
def read_device(device: object, name: str, duration_s: float) -> None
```

Read a device once or poll it for the requested duration.

### `print_help`

```python
def print_help() -> None
```

### `main`

```python
def main() -> None
```

## `test_relay_y1.py`

Source: [scripts/test_relay_y1.py](../../scripts/test_relay_y1.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `argparse`, `json`, `pathlib`, `src.engine.hardware.communication.modbus.modbus`, `src.engine.hardware.vacuum_pump.modbus.modbus_vacuum_pump_transport`, `sys`, `time`.

Module declarations (expressions are shown without evaluating them):

```python
ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / 'src' / 'robot_systems' / 'paint' / 'storage' / 'settings' / 'hardware' / 'modbus.json'
DEFAULT_REGISTER = 129
```

### `_load_modbus_config`

```python
def _load_modbus_config(path: Path) -> ModbusConfig
```

### `_parse_args`

```python
def _parse_args() -> argparse.Namespace
```

### `_build_transport`

```python
def _build_transport(config: ModbusConfig) -> ModbusVacuumPumpTransport
```

### `main`

```python
def main() -> int
```

## `test_servo_pickup_procedure.py`

Source: [scripts/test_servo_pickup_procedure.py](../../scripts/test_servo_pickup_procedure.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `logging`, `pathlib`, `src.engine.hardware.vacuum_sensor.dummy_vacuum_sensor_transport`, `src.engine.hardware.vacuum_sensor.models.vacuum_sensor_config`, `src.engine.hardware.vacuum_sensor.vacuum_sensor_service`, `src.engine.robot.drivers.client_adapters.http_websocket`, `src.engine.robot.enums.axis`, `src.engine.robot.procedures`, `sys`, `threading`, `time`.

Module declarations (expressions are shown without evaluating them):

```python
ROOT = Path(__file__).resolve().parents[1]
BACKEND = 'http'
SERVER_URL = 'http://localhost:5000'
SERVO_AXIS = RobotAxis.Z
SERVO_DIRECTION = Direction.MINUS
SERVO_LINEAR_MM_S = 100.0
SERVO_ANGULAR_DEG_S = None
SERVO_FRAME = 'user'
TOOL = 1
USER = 0
TIMEOUT_S = 5.0
POLL_INTERVAL_S = 0.02
PREFLIGHT_CONDITION_READ_ATTEMPTS = 2
CONDITION_READ_FAILURE_LIMIT = 3
DETECT_AFTER_S = 3.0
VACUUM_DETECTED_VALUE = 1
VACUUM_CLEAR_VALUE = 0
VACUUM_SENSOR_REGISTER = 0
APPROACH_POSE = None
APPROACH_VELOCITY = 10.0
APPROACH_ACCELERATION = 10.0
LOG_LEVEL = 'INFO'
```

### `LocalFakeRobot`

```python
class LocalFakeRobot:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self) -> None
```

```python
def move_ptp(self, position, tool, user, vel, acc, blocking=True)
```

```python
def start_servo_jog(self, axis, direction, linear_mm_s=None, angular_deg_s=None, *, frame='user', tool=0, user=0)
```

```python
def stop_servo_jog(self)
```

### `_build_robot`

```python
def _build_robot()
```

### `_start_vacuum_emulator`

```python
def _start_vacuum_emulator(transport: DummyVacuumSensorTransport, *, detect_after_s: float, detected_value: int, clear_value: int) -> threading.Thread | None
```

### `main`

```python
def main() -> int
```

## `two_camera_preview.py`

Source: [scripts/two_camera_preview.py](../../scripts/two_camera_preview.py).

Open two V4L2 cameras and display their live feeds side by side.

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `argparse`, `cv2`, `numpy`, `sys`, `time`.

Module declarations (expressions are shown without evaluating them):

```python
DEFAULT_PRIMARY = '/dev/v4l/by-path/pci-0000:00:14.0-usb-0:5:1.0-video-index0'
DEFAULT_AUXILIARY = '/dev/v4l/by-path/pci-0000:00:14.0-usb-0:9:1.0-video-index0'
```

### `_open_camera`

```python
def _open_camera(device: str, width: int, height: int, fps: int) -> cv2.VideoCapture
```

### `_label`

```python
def _label(frame: np.ndarray, text: str) -> np.ndarray
```

### `_read_frame`

```python
def _read_frame(camera: cv2.VideoCapture, name: str) -> np.ndarray
```

### `main`

```python
def main() -> int
```

## `vacuum_pump_off.py`

Source: [scripts/vacuum_pump_off.py](../../scripts/vacuum_pump_off.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `argparse`, `json`, `pathlib`, `src.engine.hardware.communication.modbus.modbus`, `src.engine.hardware.peripherals`, `src.engine.hardware.vacuum_pump.modbus.modbus_vacuum_pump_factory`, `src.engine.hardware.vacuum_pump.modbus.modbus_vacuum_pump_transport`, `src.engine.hardware.vacuum_pump.models.vacuum_pump_config`, `src.engine.hardware.xinje`, `sys`, `time`.

Module declarations (expressions are shown without evaluating them):

```python
ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / 'src' / 'robot_systems' / 'paint' / 'storage' / 'settings' / 'hardware' / 'modbus.json'
DEFAULT_PERIPHERALS_CONFIG = ROOT / 'src' / 'robot_systems' / 'paint' / 'storage' / 'settings' / 'hardware' / 'peripherals.json'
DEFAULT_REGISTER = 'Y0'
DEFAULT_BLOW_OFF_REGISTER = 'Y1'
DEFAULT_BLOW_OFF_SECONDS = 0.2
```

### `_load_modbus_config`

```python
def _load_modbus_config(path: Path) -> ModbusConfig
```

### `_load_peripheral_config`

```python
def _load_peripheral_config(path: Path) -> PeripheralConfig | None
```

### `_print_settings`

```python
def _print_settings(args: argparse.Namespace, config: ModbusConfig, peripherals: PeripheralConfig | None) -> None
```

### `_parse_int`

```python
def _parse_int(value: str) -> int
```

### `_parse_output_point`

```python
def _parse_output_point(value: str) -> int | str
```

### `_format_output_point`

```python
def _format_output_point(point: int | str | None) -> str
```

### `_parse_args`

```python
def _parse_args() -> argparse.Namespace
```

### `_build_transport`

```python
def _build_transport(config: ModbusConfig) -> ModbusVacuumPumpTransport
```

### `_apply_connection`

```python
def _apply_connection(config: ModbusConfig, connection) -> None
```

### `_write_direct`

```python
def _write_direct(transport: ModbusVacuumPumpTransport, mode: str, address: int | str, image_register: int, value: int) -> None
```

### `_run_direct_mode`

```python
def _run_direct_mode(args: argparse.Namespace, config: ModbusConfig) -> int
```

### `_print_readback`

```python
def _print_readback(transport: ModbusVacuumPumpTransport, label: str, pump_register: int | str, blow_off_register: int | str | None) -> None
```

### `main`

```python
def main() -> int
```

## `video_capture.py`

Source: [scripts/video_capture.py](../../scripts/video_capture.py).

Imports (including optional/function-local imports; not a startup dependency list): `argparse`, `cv2`, `pathlib`, `src.engine.vision.implementation.plvision.PLVision.Camera`, `sys`, `time`.

Module declarations (expressions are shown without evaluating them):

```python
REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CAMERA_INDEX = 1
DEFAULT_WIDTH = 1280
DEFAULT_HEIGHT = 720
REQUESTED_FPS = 60.0
OUTPUT_PATH = 'recording.avi'
```

### `_parse_args`

```python
def _parse_args() -> argparse.Namespace
```

### `main`

```python
def main() -> int
```

## `vision_aruco_test.py`

Source: [scripts/vision_aruco_test.py](../../scripts/vision_aruco_test.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `argparse`, `cv2`, `numpy`, `os`, `src.engine.common_settings_ids`, `src.engine.core.message_broker`, `src.engine.repositories.settings_service_factory`, `src.engine.vision.implementation.VisionSystem.VisionSystem`, `src.engine.vision.implementation.VisionSystem.core.service.internal_service`, `src.engine.vision.vision_service`, `src.engine.work_areas.work_area_service`, `src.robot_systems.paint.paint_robot_system`, `sys`, `time`.

Module declarations (expressions are shown without evaluating them):

```python
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GRID_IDS = {1: 'TL', 7: 'TC', 13: 'TR', 132: 'ML', 140: 'MC', 164: 'MR', 297: 'BL', 321: 'BC', 262: 'BR'}
```

### `_build_vision_service`

```python
def _build_vision_service(active_area: str | None) -> VisionService
```

### `_draw_markers`

```python
def _draw_markers(frame: np.ndarray, corners, ids) -> np.ndarray
```

### `_draw_status_bar`

```python
def _draw_status_bar(frame: np.ndarray, total: int, in_grid: int) -> np.ndarray
```

### `main`

```python
def main() -> int
```

## `write_compact_paint_register.py`

Source: [scripts/write_compact_paint_register.py](../../scripts/write_compact_paint_register.py).

Move by a specified angle using the compact paint Modbus config.

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `json`, `pathlib`, `src.engine.hardware.communication.modbus.modbus`, `src.engine.hardware.communication.transport_registry`, `sys`.

Module declarations (expressions are shown without evaluating them):

```python
REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
MIN_WRITE_VALUE = 45
REGISTER_ADDRESS = 2
MOVE_DEGREES = 10
MIN_DEGREES = 0.0
MAX_DEGREES = 90.0
MIN_REGISTER_VALUE = 47
MAX_REGISTER_VALUE = 141
MODBUS_CONFIG_PATH = REPOSITORY_ROOT / 'src/robot_systems/paint/profiles/tray_dryer/storage/settings/hardware/modbus.json'
```

### `degrees_to_register_delta`

```python
def degrees_to_register_delta(degrees: float) -> int
```

### `main`

```python
def main() -> int
```

## `write_y0.py`

Source: [scripts/write_y0.py](../../scripts/write_y0.py).

Imports (including optional/function-local imports; not a startup dependency list): `logging`, `src.engine.hardware.communication.modbus.modbus_register_transport`, `sys`.

Module declarations (expressions are shown without evaluating them):

```python
PORT = '/dev/ttyUSB0'
SLAVE_ID = 10
ADDRESS = 1
value = int(requested_value)
transport = ScriptModbusTransport(port=PORT, slave_address=SLAVE_ID, baudrate=57600, bytesize=8, stopbits=1, parity='N', timeout=0.5)
```

### `ScriptModbusTransport`

```python
class ScriptModbusTransport(ModbusRegisterTransport):
```

Standard Modbus RTU transport used by this diagnostic script.

## `xinje_ma_manual_test.py`

Source: [scripts/xinje_ma_manual_test.py](../../scripts/xinje_ma_manual_test.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `pathlib`, `src.engine.hardware.vacuum_pump.modbus.modbus_vacuum_pump_transport`, `src.engine.hardware.xinje`, `sys`, `time`.

Module declarations (expressions are shown without evaluating them):

```python
ROOT = Path(__file__).resolve().parents[1]
PORT = '/dev/ttyUSB0'
SLAVE_ADDRESS = 1
BAUDRATE = 57600
BYTESIZE = 8
PARITY = 'E'
STOPBITS = 1
TIMEOUT = 0.5
transport = ModbusVacuumPumpTransport(port=PORT, slave_address=SLAVE_ADDRESS, baudrate=BAUDRATE, bytesize=BYTESIZE, parity=PARITY, stopbits=STOPBITS, timeout=TIMEOUT)
```

### `read_input`

```python
def read_input(point: str | int) -> int
```

### `read_output`

```python
def read_output(point: str | int) -> int
```

### `write_output`

```python
def write_output(point: str | int, value: int | bool) -> None
```

### `pulse_output`

```python
def pulse_output(point: str | int, hold_s: float=1.0) -> None
```

### `read_all_inputs`

```python
def read_all_inputs() -> dict[str, int]
```

### `read_all_outputs`

```python
def read_all_outputs() -> dict[str, int]
```
