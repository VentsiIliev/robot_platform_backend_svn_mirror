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

The tray-dryer uses the corrected detailed compact STL for visualization.
Collision geometry consists of the unchanged 10-triangle table-surface mesh plus
21 independent `cell_fixture_tray_01` … `cell_fixture_tray_21` box objects in MoveIt's
world scene. The boxes preserve the exact bounds of the original 262-triangle
`paint_tray_dry_compact.surface_3levels_above.stl` proxy. They are not duplicated
inside the robot URDF. The surfaces have zero thickness.

Fixture definitions and enabled states live in `paint_tray_dry/cell_scene.yaml`.
Scene Editor's **Collision objects → Cell collision configuration…** reads and
saves them through `/configuration/cell_scene`. **Save and apply** writes the
profile atomically, checks the loaded revision, and applies a world-scene diff
only when the robot is stationary. Saved-but-pending changes are shown separately;
use **Apply saved configuration** after stopping motion. Backend restart restores
the saved enabled states. The table surfaces remain enabled. Workspace bounds
continue to use the original fixed cell envelope, independent of fixture states.
Visibility checkboxes never change collision checking.

The mesh assets use `scale="0.001 0.001 0.001"` and zero mounting translation.
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
- `<profile>/sensorless_collision.yaml`: sensorless controller startup parameters,
  monitor/model values and runtime stop/recovery policy. Each profile can include
  `../shared/sensorless_collision.yaml` and override its own values. The backend
  configuration API writes profile overrides, never the shared defaults.
- `<profile>/runtime.yaml`: explicit composition (`RUNTIME_INCLUDES`), URDF/SRDF
  selection, frame settings and calibration save path.

A different robot base attachment and a mesh origin are separate transforms.
Apply each once: use the component's geometry origin for its authored mesh frame
and the profile's macro arguments for the component attachment. TCP calibration
is a separate working-point transform, not a mesh-placement correction.

## Cartesian feedback timing

`paint_tray_dry` overrides `TF_PUBLISH_RATE_HZ` and `STATE_PUBLISH_RATE_HZ`
to 100 Hz and enables `STATE_USE_TF_SOURCE_TIMESTAMPS`. The Cartesian pose
header then retains the TF transform timestamp, including when repeated lookups
return the same transform. Republishing a cached transform does not establish
new feedback. The source timestamp is a ROS TF timestamp, not a hardware encoder
acquisition timestamp.

These are profile-local settings. Other profiles retain the 15 Hz TF launch
default, their existing Cartesian publication rate, and publication-time pose
stamps. The shared derivative implementation, joint input/derivative rates,
10 Hz monitor store, UI WebSocket rates, pose frames, and units are unchanged.
The tray profile already disables Cartesian and joint derivative topics.
The diagnostic plot removes duplicate source timestamps before calculating
its motion profile; calibration coverage logging keeps its own time throttle.

The higher configured rates support the platform's 50 ms feedback-age bound;
actual scheduling and HTTP latency must still satisfy that bound. They do not
relax the 200 ms settling window or the prepared-start position/orientation
limits. Rebuild and restart before measuring deployed timing.

## Loading and rebuilding

`runtime.yaml` selects the standalone default. `ZEROERR_ACTIVE_PROFILE` takes
precedence for both launch and the runtime. The platform selects its backend
profile in `platform/config/platform.json`; the tray-dryer now selects its own
`paint_tray_dry` profile.

Both readers use the same include loader. Included mappings merge in listed
order, then explicit values in the including file override them. This is a
**top-level** runtime include merge: explicitly supplied registries/lists replace those from an
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

## Configuration authority and live edits

The backend profile is the durable authority. Platform editors use the same
backend connection and revision-checked configuration API; platform robot-system
storage owns UI/process settings and measurement history. Backend startup does
not depend on the platform or replay platform geometry into the profile.

Sensorless files use their own section-aware inheritance: nested mappings merge
and lists replace inherited lists. This differs from the top-level runtime include
merge described above. Read effective values and revision through
`GET /configuration/sensorless_collision`; a small profile file can inherit most
of its settings without using hardcoded runtime defaults.

A successful save does not prove all values are live. Check `pending_application`,
`application_error_info`, `applied` and `restart_required`. Supported monitor
fields can apply live; controller/model/stop/recovery changes require restart.
See [backend configuration](../../erob_moveit_runtime/docs/backend_configuration.md)
and the [sensorless runbook](../collision_detection/docs/SENSORLESS_COLLISION_DETECTION.md).
