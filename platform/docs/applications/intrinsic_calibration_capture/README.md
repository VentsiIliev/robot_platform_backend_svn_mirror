# Intrinsic Calibration Capture

Automated chessboard or ChArUco acquisition combines robot movement, fresh camera snapshots and calibration output. The MVC contract `IIntrinsicCaptureService` exposes start/stop/liveness, latest frame, configuration query and configuration update. Core capture mathematics live in `core/`; robot/vision operations stay in the runtime service.

`IntrinsicCaptureConfig` declares board type/geometry, dictionary/marker sizes, image-grid spacing/margins, tilt/Z offsets, translational/rotational probes, ChArUco sweep limits, minimum corner count, motion settings, stabilization/retry policy and output directory. Zero-valued board dimensions/square size are resolved from the vision service; zero marker size is derived from square size. See [service reference](service/MODULES.md) for exact defaults and dictionary choices.

The runtime service acquires on a worker thread. Capture progress uses `INTRINSIC_CAPTURE_PROGRESS`; the controller/view display the resulting frame/status. Stopping is cooperative: review the service before treating it as an immediate motion-halt command.

Artifacts can include captured frames, `coverage_map.png`, `capture_poses.json`, camera calibration NPZ files and, for enabled ChArUco hand-eye calculation, a camera/flange transform. Output resolution prefers configured paths and the vision/system storage context; it is not one global calibration directory. Calibration acceptance and storage writes are distinct from editing the acquisition settings.

Shared robot calibration embeds these controls too, so standalone application availability and the calibration screen's capture workflow are separate integration paths. Read `example_usage.py` before running: capture can move a robot and write calibration data.

<!-- source-navigation:start -->
## Source navigation

[Module reference](MODULES.md) — signatures, fields, imports and source links for every Python file in this directory.

| Source subdirectory | Guide |
|---|---|
| `controller/` | [controller](controller/README.md) |
| `core/` | [core](core/README.md) |
| `model/` | [model](model/README.md) |
| `service/` | [service](service/README.md) |
| `view/` | [view](view/README.md) |

[Complete source index](../../SOURCE_INDEX.md).
<!-- source-navigation:end -->
