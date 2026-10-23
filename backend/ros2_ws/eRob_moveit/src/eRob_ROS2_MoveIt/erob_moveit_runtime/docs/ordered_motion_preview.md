# Ordered-motion preview

The ordered scheduler publishes finalized plans for observation, including while
preplanning waits for execution authorization. This does not command the robot.

- `/ordered_motion/preview`: `std_msgs/msg/String`, version 1 JSON snapshots with
  chain `plan_id`, monotonic `revision`, base/tip frames, tool transform (meters),
  initial joints (radians/meters), and segment states and sampled joint positions.
  Cartesian failure targets are millimeters in `frame_id`.
- `/ordered_motion/display_planned_path`: `moveit_msgs/msg/DisplayTrajectory`,
  cumulative finalized joint trajectories and the first planning start state.
  Updated when the trajectory set changes, rather than restarting RViz playback
  on every execution status change.

Both use reliable transient-local QoS with depth 1. The event snapshot includes
all available segment paths so a late subscriber does not need old events.
Snapshots and standard messages are serialized/published by a separate worker;
pending updates coalesce to the latest complete snapshot. Preview observation
errors are isolated from planning/controller results. Joint positions in preview
snapshots are sampled to at most 512 points per segment, retaining both endpoints;
the actual controller trajectory and standard DisplayTrajectory are unchanged.

Planner exceptions record the original segment index/label and requested target
when coordinate conversion is available. A red target is explicitly inexact:
`location_kind=requested_target`, `exact_location=false`. It is not a confirmed
collision point. Group/blending errors identify a planning group when there is
no more precise member failure. Execution errors identify the active segment
where available; no Cartesian point is invented. Earlier planned paths remain
for inspection after failures. Explicit stopped/cancelled/discarded statuses clear
paths; each new chain has a new plan ID and replaces the previous preview.

The scene editor uses the JSON snapshots, URDF forward kinematics, and the selected
planning tool offset to draw a sampled TCP trace. It does not use live joint TF
as a substitute for planned joint values. Unknown/missing joints or unsupported
kinematic types report a preview warning while live scene display continues.

Rebuild `erob_moveit_runtime` and restart the backend to load these publishers.
The editor has a Show planned trajectory toggle and failure details in its ROS 2
panel. This feature does not expose an exact failed waypoint or collision contact
if the underlying planner only reports a segment-level exception.
