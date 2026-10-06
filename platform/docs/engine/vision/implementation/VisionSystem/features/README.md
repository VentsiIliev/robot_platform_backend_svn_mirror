# `VisionSystem/features/` — Vision Features

Self-contained subsystems providing optional or specialised vision capabilities. Unlike `services/` (which are always active during `run()`), features are invoked on demand or wired explicitly.

---

## `contour_matching/` — Workpiece Contour Matching

**Entry point:** `contour_matcher.py` → `find_matching_workpieces()`

Matches a list of live camera contours against a library of saved workpiece contours, then computes the precise rotation and translation needed to align each match.

```python
find_matching_workpieces(
    workpieces:    list,          # objects with get_main_contour(), get_spray_pattern_contours(), get_spray_pattern_fills()
    new_contours:  list[np.ndarray],
    debug:         bool = False,
) -> tuple[dict, list, list]
    # returns (final_matches, unmatched_contours, matched_contours)
```

### Pipeline

```
1. Matching
   ├── GeometricMatchingStrategy  (default) — shape similarity + centroid/rotation comparison
   └── MLMatchingStrategy         (optional) — loads a trained model from saved_models/
       Selects by ContourMatchingSettings.get_use_comparison_model()

2. Alignment  (for each matched pair)
   ├── prepare_data_for_alignment()  — attaches Contour objects to MatchInfo
   └── _alignContours()
       ├── rotate + translate contour to match template
       ├── mask_refinement           (optional — crops spray pattern to corrected region)
       └── update_workpiece_data()   — writes final spray path back to workpiece object
```

### Key Types

| Type | File | Role |
|------|------|------|
| `MatchInfo` | `matching/match_info.py` | One matched pair: workpiece + contour + centroid/rotation diff |
| `BestMatchResult` | `matching/best_match_result.py` | Result from a matching strategy: `is_match`, `workpiece`, `confidence` |
| `MatchingStrategy` | `matching/strategies/matching_strategy_interface.py` | ABC: `find_best_match(workpieces, contour) → BestMatchResult` |
| `GeometricMatchingStrategy` | `matching/strategies/` | Shape-hash + Hu moments comparison |
| `MLMatchingStrategy` | `matching/strategies/ml_matching_strategy.py` | ML model inference |
| `ContourMatchingSettings` | `settings/ContourMatchingSettings.py` | Similarity threshold, debug flags, model toggle |
| `ContourAligner` | `alignment/contour_aligner.py` | Rotation + translation computation |

### Debug Output

When `debug=True` or individual `ContourMatchingSettings` debug flags are set, `plot_generator.py` saves debug plots to `features/contour_matching/debug/output/`.

---

## `calibration/` — Camera Calibration (Internal)

**Entry point:** `calibration/cameraCalibration/CameraCalibrationService.py`

Implements chessboard-based lens distortion calibration using OpenCV `calibrateCamera`. Called by `services/CalibrationService` — not used directly.

```python
CameraCalibrationService(
    chessboardWidth:   int,
    chessboardHeight:  int,
    squareSizeMM:      float,
    skipFrames:        int,
    storagePath:       str,
    message_publisher: MessagePublisher | None = None,
    messaging_service: IMessagingService | None = None,
)

result = svc.run(raw_image)
# result.success, result.camera_matrix, result.distortion_coefficients, result.perspective_matrix
```

Saves calibration data (`.npz`) to `storagePath`. Also includes `stereo_calibration/` for dual-camera setups (standalone, not integrated into the main pipeline).

---

## Laser height detection

Laser detection now belongs to the shared [robot height-measuring package](../../../../robot/height_measuring/README.md), not a `VisionSystem/features/laser_detection` directory. See that guide and its source reference for detection/control contracts.

## `brigthtness_control/` — Brightness Manager

**File:** `brigthtness_control/brightness_manager.py`

Higher-level brightness control that can manage brightness across multiple camera regions or modes. Wraps `BrightnessController` from `plvision/PID/`. The main-loop `BrightnessService` supports active-work-area regions, area-specific adjustments and adjustment locks. See its source reference for the current contract.

---

## `hand_eye/` — Hand-Eye Calibration

**Files:** `hand_eye/collect_robot_poses.py`, `ttest_eye_in_hand.py`

Utilities for collecting matched robot pose / camera pose pairs to solve the hand-eye calibration problem (`cv2.calibrateHandEye`). Standalone scripts — not integrated into the platform startup.

---

## `camera_pose_solver/` — Camera Pose Estimation

**File:** `camera_pose_solver/pose_solver.py`

Estimates camera pose (rotation + translation) relative to a known marker pattern using `cv2.solvePnP`. Used in research/development workflows.

---

## Height measurement ownership

There is no `heightMeasuring/` feature directory in this checkout. Height calibration, laser detection and correction are implemented under `src/engine/robot/height_measuring/`.

---

## `qr_scanner/` — QR Code Scanner

**File:** `qr_scanner/QRcodeScanner.py`

Wraps `cv2.QRCodeDetector` or `pyzbar` (whichever is available) to decode QR codes from a frame. Used by `services/QrDetectionService`.

<!-- source-navigation:start -->
## Source navigation

[Module reference](MODULES.md) — signatures, fields, imports and source links for every Python file in this directory.

| Source subdirectory | Guide |
|---|---|
| `brigthtness_control/` | [brigthtness_control](brigthtness_control/README.md) |
| `calibration/` | [calibration](calibration/README.md) |
| `camera_pose_solver/` | [camera_pose_solver](camera_pose_solver/README.md) |
| `contour_matching/` | [contour_matching](contour_matching/README.md) |
| `hand_eye/` | [hand_eye](hand_eye/README.md) |
| `qr_scanner/` | [qr_scanner](qr_scanner/README.md) |
| `shape_matching_training/` | [shape_matching_training](shape_matching_training/README.md) |

[Complete source index](../../../../../SOURCE_INDEX.md).
<!-- source-navigation:end -->
