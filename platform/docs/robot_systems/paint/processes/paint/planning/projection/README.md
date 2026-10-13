# Painting motion projection

- `source_plan.py`: prepares source contact contours and selected intervals.
- `core.py`: projects contours into robot contact poses and rebases rotations.
- `config.py`: normalizes projection settings.
- `planes.py`: selects XY/RZ or XZ/RY plane behavior.
- `inputs.py`: supplies shared source-path/anchor helpers and `PaintProjectionContext`.

The geometry keeps each sampled contour point at the paint contact axis. Preview providers reuse this mathematics; this package does not depend on visualization.

[Module reference](MODULES.md).

`command_job.py` defines motion settings for a generated painting-contact path, shared by projection, pickup-chain assembly, and painting execution.
