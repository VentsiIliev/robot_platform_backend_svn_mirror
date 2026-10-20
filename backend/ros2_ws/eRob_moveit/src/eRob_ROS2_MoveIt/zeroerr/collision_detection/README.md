# Collision detection

This directory owns the ZeroErr sensorless-collision detector and its supporting
tooling. Runtime code is deliberately separated from offline calibration so that
production behavior can be reviewed without navigating data-analysis scripts.

## Layout

```text
collision_detection/
├── runtime/
│   ├── src/                    # 2 kHz ros2_control C++ implementation
│   ├── include/                # Runtime controller interface
│   ├── legacy/                 # Deprecated Python observer; never launched
│   └── zeroerr_controllers.xml # controller_interface plugin registration
├── calibration/
│   ├── data_collection/        # Calibration runner, coverage and peak recorder
│   └── modeling/               # Offline fit, threshold calibration and audits
├── config/
│   └── archive/                # Local safety backups; JSON files are ignored
├── diagnostics/                # Status GUI and PlotJuggler layout
├── docs/                       # Architecture and calibration procedures
└── test/                       # Collision-specific unit tests
```

The source files are installed with their existing executable basenames. Commands
such as `ros2 run zeroerr zeroerr_peak_recorder.py` therefore remain unchanged.
The active configuration is `config/<ACTIVE_PROFILE>/sensorless_collision.yaml`,
with explicit shared defaults in `config/shared/sensorless_collision.yaml`.
Nested overrides and GUI saves are profile-specific. The PlotJuggler layout remains
installed into `share/zeroerr/config`. The existing platform/API field names are
preserved; the old global monitor JSON is no longer used.

## Ownership rules

- `runtime/` must remain deterministic and must not import calibration tooling.
- `calibration/data_collection/` records evidence but does not change runtime
  configuration.
- `calibration/modeling/` operates offline and only changes configuration when an
  explicit `--apply` option is supplied.
- `diagnostics/` is observational and must not participate in the real-time loop.
- Archived configuration snapshots are local recovery artifacts and are not
  published.

See [docs/SENSORLESS_COLLISION_DETECTION.md](docs/SENSORLESS_COLLISION_DETECTION.md)
for the runtime design and [docs/COLLISION_CALIBRATION_RUNNER.md](docs/COLLISION_CALIBRATION_RUNNER.md)
for the calibration workflow.
