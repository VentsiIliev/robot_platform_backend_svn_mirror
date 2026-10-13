# Paint planning

Planning is grouped by the kind of geometry it produces:

- [Contours](contours/README.md): contour selection/conversion and interpolation.
- [Pickup](pickup/README.md): pickup-to-paint transfer poses and safe travel.
- [Projection](projection/README.md): source contact plans, configuration, execution planes, projection inputs, and contact-motion mathematics.

`workpiece_preparation_service.py` combines injected matching, live defaults, and coordinate transformation to produce raw workpiece input. Typed matching and preparation failures are preserved. `pose_helpers.py` contains pose transformations shared by pickup planning and incremental adjustment, including calibration-to-destination orientation mapping used by magazine transfer and plate reservation.

Interpolation debug plots belong to `src/robot_systems/paint/diagnostics/contour_interpolation.py`. Editor preview generation belongs to the system-level visualization package. These moves preserve existing algorithms and motion behavior.

[Module reference](MODULES.md).
