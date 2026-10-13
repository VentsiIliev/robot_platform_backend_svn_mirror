# Paint contour preparation and matching

The current source separates saved-workpiece matching from contour-payload normalization. The former `align/alignment/core.py` and `align/dxf_image_placement.py` solvers are absent; `align_raw_workpiece_to_contour()` and `map_raw_workpiece_mm_to_image()` are not current repository entry points.

## Current path

1. Capture-time frame/contours/robot pose arrive through the capture-snapshot service.
2. `PaintWorkpieceMatchingService` in `match/` loads candidates through injected list/load callbacks, optionally filters selected IDs, and invokes the injected matching implementation.
3. Matching returns raw workpiece data plus identity/candidate/confidence metadata. Missing dependencies, no candidates, unsuccessful matching and conversion errors return explicit failure results.
4. `PaintWorkpiecePreparationService` in `planning/` decides between matched data and raw captured-contour preparation. Enabled/available matching failure produces an unknown-workpiece result; fallback applies when matching is disabled/unavailable.
5. Shared `DefaultWorkpiecePathPreparationService` transforms the resulting payload into an execution plan with the selected targeting/calibration context.

`align/alignment/io.py` extracts, normalizes, replaces and resamples raw contour payloads. `sampling.py` supplies closed-path resampling/smoothing, length, area and diagnostics. The `align` package exports these helpers; it does not currently implement the previously documented standalone rigid/reference-smooth solver.

The actual vision matcher lives under [vision implementation](../../../../engine/vision/implementation/VisionSystem/features/contour_matching/README.md). Paint adapts its result to storage/editor/production contracts. Matching tests and source references identify the concrete implementation supplied by composition.

See [match reference](match/MODULES.md), [preparation reference](planning/MODULES.md), [alignment helpers](align/alignment/MODULES.md) and [historical algorithm description](../../../../archive/robot_systems/paint/processes/paint/ALIGNMENT.md). Historical equations are not guarantees about the active matcher.
