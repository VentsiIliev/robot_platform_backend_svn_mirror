# Configuration ownership and robot descriptions

Every backend profile owns a robot-description entry point:

| Profile | Entry point | Arm parameters | Cell / tool |
|---|---|---|---|
| `paint_auto_dry` | `paint_auto_dry/urdfs/robot.urdf.xacro` | `models/zeroerr_extended.yaml` | automatic-dryer mounting / centered disk |
| `paint` | `paint/urdfs/robot.urdf.xacro` | `models/zeroerr_extended.yaml` | paint mounting / centered disk |
| `paint_short_links` | `paint_short_links/urdfs/robot.urdf.xacro` | `models/zeroerr_short.yaml` | simple table / pointer |
| `paint_tray_dry` | `paint_tray_dry/urdfs/robot.urdf.xacro` | `models/zeroerr_short.yaml` | compact tray-dryer cell / pointer |
| `development_short_links` | `development_short_links/urdfs/robot.urdf.xacro` | `models/zeroerr_short.yaml` | basic square table / pointer |
| `development_extended_links` | `development_extended_links/urdfs/robot.urdf.xacro` | `models/zeroerr_extended.yaml` | basic square table / centered disk |
| `welding` | `welding/urdfs/robot.urdf.xacro` | `models/zeroerr_extended_motor_masses.yaml` | welding table / welding disk |

The tray-dryer uses the corrected detailed compact STL for visualization and
`paint_tray_dry_compact.surface_3levels_above.stl` (262 triangles) for collision
geometry. The collision proxy includes the three stepped surfaces plus simplified
fixtures and equipment above them. The surfaces have zero thickness and do not
represent a filled volume underneath them; small hardware details remain omitted.
Both meshes use `scale="0.001 0.001 0.001"` and zero mounting translation.
The profile rotates their shared mounting joint +90 degrees about Z (counterclockwise
viewed from above), so visual, collision and extracted workspace rotate together.
The asset metadata records its mounting-hole-centred origin and mounting surface
at Z=0; its original 90-degree correction is already baked into the mesh.
Do not apply that correction a second time.

`paint` retains the legacy automatic-dryer cell for compatibility. Use the
explicit `paint_auto_dry` profile for the automatic-dryer system; its calibrated
TCPs and workobjects are saved independently from the legacy profile.

The two development profiles use the same 2 x 2 m, 30 mm-thick square table
for visual and collision geometry, with its upper surface at base Z=0. They
retain their respective base profile's tool geometry and initial calibration,
but save calibration independently. Neither development profile enables the
production cell's guarded drop-opening passage.

## What to edit

- `<profile>/urdfs/robot.urdf.xacro`: that profile's component selection and
  mounting offsets (`mount_xyz` in metres, `mount_rpy` in radians).
- `shared/urdf/zeroerr_arm.xacro`: arm structure common to all profiles.
- `models/*.yaml`: variant-specific joint origins, limits, meshes and inertias.
  Welding currently uses different masses/limits despite sharing some meshes;
  those differences are intentionally preserved.
- `shared/cells/*.xacro`: a particular mounting/fixture component's geometry,
  including visual/collision origins, scales and materials.
- `shared/tools/*.xacro`: a physical tool component's geometry. Its attachment to
  the flange is selected separately in each profile's URDF entry point.
- `<profile>/cell.yaml`: runtime cell collision objects and guarded passages.
- `<profile>/tools.yaml`: runtime tool collision settings. Shared paint defaults
  live in `shared/tools/paint_runtime.yaml`; an installation can override them.
- `<profile>/calibration.yaml`: measured TCPs, tool ID associations and
  workobject registration. API saves write here, not into shared defaults or
  another installation's profile. Existing values are migrated unchanged.
- `shared/motion/paint.yaml`: runtime motion values common to the paint profiles.
  Dedicated contour/PTP/Servo/trajectory-limit files remain beside their profile.
- `<profile>/runtime.yaml`: explicit composition (`RUNTIME_INCLUDES`), URDF/SRDF
  selection, frame settings and calibration save path.

A different robot base attachment and a mesh origin are separate transforms.
Apply each once: use the component's geometry origin for its authored mesh frame
and the profile's macro arguments for the component attachment. TCP calibration
is a separate working-point transform, not a mesh-placement correction.

## Loading and rebuilding

`runtime.yaml` selects the standalone default. `ZEROERR_ACTIVE_PROFILE` takes
precedence for both launch and the runtime. The platform selects its backend
profile in `platform/config/platform.json`; the tray-dryer now selects its own
`paint_tray_dry` profile.

Both readers use the same include loader. Included mappings merge in listed
order, then explicit values in the including file override them. This is a
**top-level** merge: explicitly supplied registries/lists replace those from an
include. Missing includes and cycles fail startup rather than silently falling
back. Keep calibration as the last included component.

Both launch and runtime expand the selected Xacro through the same resolver.
The resulting plain URDF is written atomically under
`${XDG_CACHE_HOME:-~/.cache}/zeroerr/descriptions/<content-hash>.urdf`. MoveIt,
workspace extraction, KDL and collision dynamics consume this plain description;
no consumer needs to interpret Xacro. Shared changes produce a new content hash,
so an old cached description is never substituted after an expansion failure.
Profile-specific SRDF files remain explicit because their collision exclusions
must match the selected cell and tool links.

Rebuild `zeroerr` and `erob_moveit_runtime` together in the deployed ROS workspace,
then restart the backend. This installs the shared Python composition package,
Xacro/model files and updated loaders together. Source edits do not update an
already-running robot. No hardware motion is part of configuration generation.

The older full `*.urdf` files are retained as legacy/offline reference snapshots
and regression fixtures. Active profiles select `robot.urdf.xacro`; edit its
shared components rather than those snapshots. Root `urdfs` also contains the
ros2_control wrapper and standalone legacy fallback, which remain in place.

Run the offline composition tests from a sourced ROS environment:

```bash
python3 -B zeroerr/test/test_profile_composition.py -v
```

Tests verify original geometry/limits/inertias, matching launch/runtime
selection, shared-change propagation, local mounting isolation and independent
calibration persistence without starting ROS nodes or commanding the robot.
