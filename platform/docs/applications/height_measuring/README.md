# `src/applications/height_measuring/` — Height Measuring

Settings screen for the laser-based height measurement system. Operators tune laser detection, laser calibration, and measuring parameters here. The operational laser workflow now lives in the `Calibration` application.

---

## MVC Structure

```
height_measuring/
├── service/
│   ├── i_height_measuring_app_service.py        ← IHeightMeasuringAppService (11 methods)
│   ├── height_measuring_application_service.py ← Live impl delegating to engine services
│   └── stub_height_measuring_app_service.py    ← Returns default settings, no hardware
├── model/
│   ├── height_measuring_model.py               ← Thin delegation
│   └── mapper.py                               ← HeightMeasuringSettingsMapper (flat dict ↔ settings)
├── view/
│   ├── height_measuring_view.py                ← CollapsibleSettingsView + overview/status
│   └── height_measuring_schema.py              ← Settings form schema
├── controller/
│   └── height_measuring_controller.py          ← BackgroundWorker, broker subscription for frames
├── height_measuring_factory.py
└── example_usage.py
```

---

## `IHeightMeasuringAppService`

```python
@dataclass
class LaserDetectionResult:
    ok:           bool
    message:      str
    pixel_coords: Optional[tuple[float, float]]   # laser centroid in camera pixels
    height_mm:    Optional[float]                  # measured Z offset in mm
    debug_image:  Optional[np.ndarray]             # annotated frame for display
    mask:         Optional[np.ndarray]             # binary laser mask

class IHeightMeasuringAppService(ABC):
    def run_calibration(self) -> tuple[bool, str]: ...
    def cancel_calibration(self) -> None: ...
    def is_calibrated(self) -> bool: ...
    def get_calibration_info(self) -> Optional[dict]: ...
    def get_settings(self) -> HeightMeasuringModuleSettings: ...
    def save_settings(self, settings: HeightMeasuringModuleSettings) -> tuple[bool, str]: ...
    def get_latest_frame(self) -> Optional[np.ndarray]: ...
    def reload_calibration(self) -> None: ...
    def laser_on(self) -> tuple[bool, str]: ...
    def laser_off(self) -> tuple[bool, str]: ...
    def detect_once(self) -> LaserDetectionResult: ...
    def cleanup(self) -> None: ...
```

---

## `HeightMeasuringModuleSettings`

Nested dataclass from `src/engine/robot/height_measuring/settings.py` with three sub-objects:

| Sub-object | Key fields |
|------------|-----------|
| `detection` | `min_intensity`, `gaussian_blur_kernel`, `gaussian_blur_sigma`, `default_axis`, `detection_delay_ms`, `image_capture_delay_ms`, `detection_samples`, `max_detection_retries` |
| `calibration` | `step_size_mm`, `num_iterations`, `calibration_velocity`, `calibration_acceleration`, `movement_threshold`, `movement_timeout`, `delay_between_move_detect_ms`, `calibration_max_attempts`, `max_polynomial_degree` |
| `measuring` | `measurement_velocity`, `measurement_acceleration`, `measurement_threshold`, `measurement_timeout`, `delay_between_move_detect_ms` |

`HeightMeasuringSettingsMapper` converts between this nested structure and the flat `dict` used by the form schema.

---

## Settings Form Schema

**File:** `view/height_measuring_schema.py`

Defines the `CollapsibleSettingsView` groups for the three settings sub-objects. Fields are collapsed by default; each sub-object forms one collapsible group.

---

## Controller behaviour

- `load()` — fetches current settings via `get_settings()` → `mapper.to_flat_dict()` → populates form; queries `is_calibrated()` to update the overview status.
- `save_settings()` — persists tuned detection/calibration/measuring parameters.
- Live laser calibration and one-shot detection are no longer owned by this application.

---

## Wiring in `GlueRobotSystem`

```python
service = HeightMeasuringApplicationService(
    height_measuring_service=robot_system.get_height_measuring_provider().build_service(),
    settings_service=robot_system.get_settings(SettingsID.HEIGHT_MEASURING_SETTINGS),
)
```

`ApplicationSpec`: `folder_id=2` (Service), icon `fa5s.ruler`.

---

## Design Notes

- **`cleanup()` on stop** — the service's `cleanup()` must be called when the application is closed to release any laser hardware resources (e.g., stopping the laser if it was left on).
- **`reload_calibration()`** — forces the service to re-read the calibration file from disk; call after a successful `run_calibration()` to make `is_calibrated()` reflect the new state immediately.
- **`LaserDetectionResult.debug_image`** — the annotated frame is only available when `detect_once()` succeeds. Controllers should check `ok` before trying to display it.
- **Gaussian blur kernel** — `blur_kernel_size` must be odd; the mapper enforces this by incrementing even values before applying them.

<!-- source-navigation:start -->
## Source navigation

[Module reference](MODULES.md) — signatures, fields, imports and source links for every Python file in this directory.

| Source subdirectory | Guide |
|---|---|
| `controller/` | [controller](controller/README.md) |
| `model/` | [model](model/README.md) |
| `service/` | [service](service/README.md) |
| `view/` | [view](view/README.md) |

[Complete source index](../../SOURCE_INDEX.md).
<!-- source-navigation:end -->
