# Standalone Scene Editor

A local desktop editor for arranging tools, work surfaces, fixtures, and other STL objects, with optional ROS 2 live viewing and explicit collision-object updates to MoveIt. It has its own launcher and dependencies and does not import or change platform or backend code/configuration. Offline use requires no ROS installation. This directory can be copied to a separate project without changing the code.

From the repository root, using the existing environment:

```bash
.venv/bin/python standalone/scene_editor/run.py
```

Terminal logs are enabled by default. Use `--log-level DEBUG` to include every
mesh lookup candidate and the ROS description helper command. To save logs:

```bash
.venv/bin/python standalone/scene_editor/run.py --log-level DEBUG 2>&1 | tee /tmp/scene_editor.log
```

Live view uses the same remembered mesh folder as URDF import. You can set it
directly in **ROS 2 → Connection settings… → Mesh package / workspace folder**.
Reconnect after changing it so the ROS helper uses the new folder.

Live view loads both URDF `<visual>` and `<collision>` geometry. Robot collisions
are separate orange translucent objects, with each collision's origin, mesh scale,
and current link TF. Supported geometry is STL, box, cylinder, and sphere.
They start hidden: enable **View → Show robot collision geometry** and optionally
disable **View → Show robot visual geometry** to inspect collisions alone.
The Collision explorer filter includes robot collisions; Robot includes both layers.
Display choices survive live frame updates and are retained in an editable snapshot.
This inspects the URDF geometry; it does not visualize SRDF allowed-collision rules
or modify the robot model through the world collision-object Apply actions.
Static URDF import and Load resolved URDF continue to load visuals only.

Or use a separate environment:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python run.py
```

The second example assumes this directory is the working directory. Requires a desktop session and OpenGL 3.3; no ROS installation is required.

## Appearance

### Mate two surfaces

Choose **Edit → Mate surfaces…** (also available on the viewport tool strip),
then hover over a face on the object to move and click it, followed by a face on
the target object. Hover highlights the connected flat surface in amber; selected
source and target surfaces are purple and green. Internal STL triangle edges are
hidden so a tessellated flat face behaves as one selectable region. Sharp edges
and disconnected coplanar patches remain separate.
The moving object must be unlocked; the target may remain locked. Left- or
right-drag to orbit and middle-drag to pan while picking or viewing the preview.
A click selects a face; dragging preserves the faces already selected and never
moves the objects. Clicking the source again before
choosing the target replaces the source face.

Click **Move**, **Select** or **Rotate** (or use G/Q/R with the viewport focused)
to leave face picking and return to normal editing. This also works when the
same tool was selected before mating. The mate tool stays highlighted while
face picking is active.

The preview aligns the selected surface area centers and makes their normals oppose each
other. In **General → Mate surfaces**, adjust **Gap / offset** in millimeters,
**Rotate on face**, or **Flip** for same-facing normals. Positive offset follows
the target surface's normal. Highlighted surfaces and normal arrows identify
the selections. Click **Apply surface mate** to commit one undoable local pose
change. **Pick faces again** restarts; **Cancel** or Escape discards the preview.
Changing selection or making another scene edit also discards it. No ROS scene
update or robot command is sent.

This is a one-time placement operation on a mesh, not a persistent CAD assembly
constraint. Flat regions are recognized through shared edges, with a 0.1-degree
normal tolerance and a small mesh-relative plane tolerance. Normals and distances
are compared to the starting face, so selection cannot gradually wrap around a
curve. On curved meshes it uses the local facet region; it does not infer cylinder
axes, hole centers or the original CAD face definitions. Face centers are weighted
by triangle area and may lie in a hole or outside a concave region. STL winding
determines normal direction; Flip corrects the desired facing. The operation does
not check the rest of the mesh for collisions.
Mesh size, mounting origin and source files are preserved.

The workspace has one main toolbar, a searchable scene explorer with source filters,
floating viewport tools, General / Visual / Collision / ROS 2 property tabs, and
a bottom local/live/snapshot bar with explicit ROS actions. Search and filters
only affect the explorer; the eye checkboxes control scene visibility.

Use **View** or the clickable orientation cube for perspective and orthographic
camera presets. Double-click the cube to return to perspective. Grid and transform
handles can be toggled independently. In Move mode, drag a colored axis handle
to constrain the selected object or group along that world axis; each drag is one
undo operation. Object origin/pivot controls expand inside General properties.
The Visual tab provides color and opacity controls.

The selected object's mounting origin is marked by a labeled circle/cross,
including when the object is locked or in live view. Toggle it under
**View → Show selected object origin**. This marker is independent of the transform
handles, which appear at the editable pivot. An STL initially uses its source
coordinate origin, which may lie outside its geometry.

To align an STL by its mounting point:

1. Select and unlock the local STL. Confirm its source units first.
2. In **General → Mounting origin**, click **Pick mounting point on object**,
   then click a visible surface of the selected STL. Right-drag to orbit or
   middle-drag to pan while picking. Other objects and empty space are ignored.
   A temporary **New origin** marker shows the chosen point; the scene is
   unchanged until confirmation. Pick again to replace it, or press Escape /
   **Cancel** to discard the preview. Selection changes also cancel it.
3. Optional: expand **Fine adjustment (local mm)** for exact X/Y/Z coordinates,
   measured before the object's rotation or scene translation. **Use preset**
   previews the mesh bounding-box center, bottom/top center along local Z,
   current pivot, or original STL origin. Surface picking does not automatically
   find hole centers, vertices or other mechanical features.
4. Click **Confirm mounting point** to keep it, or **Confirm and align to another
   object…** to immediately choose the target robot visual or other object in
   the view/list. The mounting point moves to the target's origin. Rotation is
   preserved, so adjust orientation separately if needed. Setting the mounting
   point keeps geometry in place and sets the rotation pivot; confirming and
   snapping are separate undoable changes.

The mounting origin is saved with the scene, independently for each object,
without changing the original STL. It follows source-unit corrections. The
normal transformed-STL export still bakes the geometry into scene coordinates;
use the scene JSON to retain the editable origin. For robot visuals, the snap
target is the selected visual's origin, which can differ from the link's TF frame
when the URDF contains a visual offset. Setting an STL origin does not change
URDF or ROS configuration.

For a local imported STL, **General → STL source units** changes its interpretation
between millimeters, centimeters and meters without reimporting. This preserves
the current pose in millimeters, reframes the object, supports Undo/Redo, and is
saved with the scene. The source file is unchanged. Locked objects and live ROS
geometry cannot be rescaled through this control.

This is the first layout pass toward the supplied design references. A hierarchical
scene tree, material library, measurement tools, and rotation rings are future work.

The editor follows the platform's light/dark palette, purple accent, typography, rounded settings cards, outlined secondary actions and 44-pixel buttons. **Appearance → Light / Dark** switches immediately and remembers the editor's choice. The 3D background, grid, selection outline, row padlocks, dialogs and native Qt palette follow the same theme; scene object colors are unchanged.

Presentation tokens live in the editor's own `scene_editor/styles.py`, matching the platform presets and common control dimensions without importing platform modules. Appearance preferences are local to this standalone app; changing them does not change platform settings or scene data.

## Current ROS 2 scene

1. Start the robot/MoveIt stack normally. RViz itself can be open or closed.
2. Open **ROS 2 → Connect to ROS 2…**. Choose the same ROS domain and fixed frame as your existing RViz view (the current ZeroErr setup uses domain **42**, frame **base_link**).
3. Select the ROS and workspace `setup.bash` / `local_setup.bash` files if they were not sourced before launching the editor. **Workspace setup** must match the running stack so `package://` mesh resources resolve to the correct files. The dialog has file pickers and remembers accepted settings.
4. In **Live view**, the robot and scene follow incoming data. You can orbit, pan, zoom, select objects, and inspect their current poses. Editing is disabled.
5. Click **Editable snapshot** to stop the reader and retain a local, editable copy. Move/rotate objects and save/export normally. Further ROS updates cannot overwrite the snapshot. **Disconnect** also keeps the last received scene as a local snapshot. Reconnecting asks you to save any local edits first.

For the current checkout, the running stack's workspace file is:

```text
/home/ilv/Desktop/25488_ZeroErr_git/backend/ros2_ws/install/local_setup.bash
```

This path is documentation for this machine, not a dependency in the code. A shell sourced from the older `/home/ilv/ros2_ws` workspace may discover ROS topics but fail to locate current mesh files. Choose the current workspace file in the connection dialog to resolve that mismatch. The ROS Python executable defaults to `/usr/bin/python3`; it needs the matching ROS distribution's `rclpy`, message packages, `ament_index_python`, and NumPy. These are separate from the editor's virtual environment. No ROS packages are imported by the GUI process.

The connector requests one full **GetPlanningScene** snapshot, then follows **/monitored_planning_scene** updates, including ADD, REMOVE, APPEND, MOVE, object colors, and attached geometry. Robot visuals come from **/robot_description**, positioned through **/tf** and **/tf_static**. The default MarkerArray topics match the current RViz setup: **/rviz_visual_tools**, **/safety_walls**, and **/active_tool_markers**. Names can be changed in the connection dialog. Data is converted from ROS meters/quaternions to editor millimeters/Euler angles, with mesh scales preserved.

The ROS helper is a separate read-only process. It creates subscriptions and a `GetPlanningScene` client; it has no apply-scene, robot-motion, or parameter-write clients. It does not start or stop the backend. Updates are coalesced to the latest complete frame at up to 5 Hz, geometry is cached separately from poses, and helper shutdown never blocks the GUI. Closing waits for the helper to stop. Connection errors and unavailable transforms appear in **ROS 2 → Connection details**. A failed connection preserves the existing local scene; a lost live connection freezes the last received scene for local editing.

Supported visuals: STL resources; box, cylinder, sphere/ellipsoid, and cone collision primitives; triangle collision meshes; cube, sphere, cylinder, arrow, line, point/list, triangle-list and STL mesh markers. Marker deletion, topic/namespace scoping, lifetimes, and frame locking are handled. Inline ROS geometry is kept in memory when disconnected and saved to a companion `<scene>.assets` directory, so saved snapshots survive after temporary session files disappear. Keep that directory with the saved JSON.

This is a scene viewer/editor, not a complete RViz display-plugin implementation. Text labels, textures/embedded materials, DAE meshes, octomaps, point-cloud displays, and RViz camera/display settings are not reproduced. Per-point marker colors use the marker-wide color; line and point markers use small geometric approximations. Unsupported geometry is reported in connection details. Frame placement uses the latest received transforms rather than a timestamped TF history. Joint motion is reflected through TF; the editable snapshot contains independent objects rather than a robot kinematic model. Live viewing and ordinary local edits do not write to ROS. Collision writes require the separate explicit actions below.

## Authoring collision objects

1. Configure ROS using **ROS 2 → ROS connection settings…**, or connect to the running scene and choose **Editable snapshot** for context. The live reader is stopped in snapshot mode, but the saved ROS connection settings remain available for explicit service calls.
2. Choose **Collision objects → New collision…**. Enter a unique object ID, reference frame, shape and dimensions in **mm**. Box dimensions are full X/Y/Z extents; cylinder dimensions are radius and height along local Z; sphere dimension is radius. Set position in mm and roll/pitch/yaw in degrees, relative to the reference frame.
3. Accept to create a **local draft**. If the reference frame differs from the editor frame, the editor queries TF to place the preview correctly. Failure to resolve TF retains the current scene without adding a draft. The default frame can be used offline. Poses in the inspector use the draft's reference frame. Mouse translation converts world/screen movement back into that frame. The preview frame transform is captured when the draft is created and is saved with it; it does not follow moving frames after disconnecting.
4. Adjust the pose by dragging the primitive directly in the 3D view, or edit position/rotation in the inspector. The **Size** section near the top of the inspector edits box X/Y/Z, cylinder radius/height or sphere radius with an immediate preview. **Edit dimensions…** also allows changing shape. These edits remain local. The collision ID and frame stay fixed for that definition. Duplicate creates an independent draft with a new collision ID.
5. Select the draft and choose **Add to ROS**. This explicitly calls the configured **/apply_planning_scene** service with a one-object diff. The local UI reports MoveIt's success response; changes can then be seen in RViz and used by subsequent planning. Add checks the current scene and rejects an existing world ID rather than silently replacing it.
6. After editing a previously added draft, choose **Update in ROS**. Update requires that world object ID to exist and replaces its geometry/pose using a one-object ADD diff. It does not change other objects, the robot state, attached bodies, or allowed collision rules.
7. **Remove from ROS** removes only the selected definition's ID from the world scene. The local definition stays available for reapplying or saving. **Delete** and undo/redo only affect local editing; they do not undo or remove ROS changes. Removing an already absent ID reports that it is absent. Attached-object IDs are rejected by all write operations.

Only authored box/cylinder/sphere definitions have write actions; imported STL objects and the robot/world visuals in a snapshot cannot accidentally be applied as new collisions. The separate one-shot collision helper creates `GetPlanningScene` and `ApplyPlanningScene` clients only. It validates dimensions, frames, rigid poses and IDs, converts mm to ROS meters and rotation to quaternion, and sets both `scene.is_diff` and `robot_state.is_diff` to preserve the rest of the scene. It does not create motion/hardware clients or start/restart the backend. Operations run in a background worker, are serialized by the UI, and report service unavailability, rejection and timeout. A timed-out apply may have an unknown result; the editor does not automatically retry it. Check the live scene before retrying. ID checks are a preflight query, not a transaction locking out other ROS writers.

**Save scene** persists collision IDs, frames, dimensions, poses and preview-frame transforms with the local scene. Loading does not publish anything. After restarting MoveIt, reload the file, select each definition and explicitly **Add to ROS**. If objects already exist, use Update. Runtime planning-scene changes are not written into backend configuration and may be removed by a backend restart or another scene writer. A world object specified relative to a moving reference frame is placed at apply time; it is not automatically attached to that frame/robot link. Use a stationary frame for persistent world obstacles.

## Editing

- Use **File → Example scene** to try a work surface, tool, and fixture.
- **Add STL** imports one or more meshes. Choose their source units explicitly: STL has no unit metadata. Original coordinates are preserved; objects are not automatically recentered.
- Click an object in the viewport or object list. The list checkboxes control visibility.
- Select a box, cylinder or sphere to edit its dimensions in the inspector's **Size** section. This works for local primitives and collision drafts, preserves pose/identity, supports undo/redo and is disabled in live view. Scaled imported visuals and STL meshes do not expose primitive size fields.
- First select the object in the list or click it in the view. In **View / orbit** mode, left-drag the **already-selected** primitive to reposition it in the screen plane. Drop it by releasing the mouse. Clicking/dragging on a different object only selects it for that gesture, without moving either object or orbiting the camera. This protection also applies in Move and Rotate modes; dragging empty space never transforms the selection. Right-drag or drag empty space to orbit instead. Small click movement does not change position. Each drag is one undo step. Primitive dragging is disabled in live view.
- Edit position offsets in **mm** and roll/pitch/yaw in **degrees**. Changes appear immediately. These fields edit the selected object, not the camera.
- Choose **Move object** or **Rotate object**, then drag with the left mouse button. Move uses the selected world axis, or the screen plane. Rotate uses X, Y, or Z (Screen uses Z). Positive screen drag is right/up. Rotation uses the displayed Euler angles, composed as `Rz(yaw) × Ry(pitch) × Rx(roll)`.
- **Pivot at mesh center** is useful when rotating a tool or surface. Source origin is the default pivot. Changing the pivot preserves the current geometry pose. Position is an offset from original coordinates; at a nonzero pivot, the world pivot equals position plus local pivot.
- In View mode, left-drag on empty space or an STL mesh orbits; left-drag on a primitive moves it. Right drag always orbits; middle drag pans; the wheel zooms. **F** frames the selection; **Frame scene** frames visible objects.
- Undo/redo covers transforms, imports, duplication, deletion, appearance, and visibility. One mouse drag is one undo step.
- **Undo**, **Redo**, and **Reset transform** are visible below the object list. The standard undo/redo keyboard shortcuts and Edit menu actions also remain available. Reset transform sets the selected object's position, rotation and pivot to zero in its reference frame; it preserves size, mesh, identity, frame and other properties. Reset is an undoable local edit and is disabled for locked objects or live viewing. None of these actions automatically changes the ROS planning scene.

## Locking and snapping origins

- Every object row has a clickable padlock on its right: **closed purple = locked**, **open muted = unlocked**. Click to toggle that object's lock without changing the current selection or visibility. The separate Lock/Unlock button has been removed; the selected-object command remains in **Edit**. Locked objects remain selectable and can be hidden or used as snap targets, but moving, rotating, resizing, changing their properties, deleting, and collision Add/Update/Remove are blocked. Duplicating a locked object makes an unlocked copy. Padlocks are disabled during live viewing and pending operations. Lock/unlock supports undo/redo and the state is saved in scene files; older files load as unlocked.
- To align origins, select the **source** object, click **Snap origin to…**, then click the **target** in either the viewport or object list. Only the source moves; its rotation, scale, pivot and collision identity stay unchanged. The target can be locked. The source must be unlocked. Clicking the source or empty space keeps target selection active; **Escape** or **Cancel snap** cancels it. The target click never begins a drag.
- Origin means the source geometry's local `(0,0,0)` transformed into the editor frame, **not** the bounding-box center or editable pivot. Snapping accounts for both objects' rotations, pivots, unit scales and collision reference frames. A single undo restores the source pose. These are local edits; choose **Update in ROS** separately for an authored collision draft.

## Moving multiple objects

- **Ctrl-click** adds/removes objects in the list or viewport. **Shift-click** selects a range in the list (adds an object in the viewport). All selected objects are highlighted. The inspector shows the selection count. A normal list click selects one object; in the viewport, clicking an unselected object replaces the selection, while pressing an already-selected group member keeps the group selected so it can be dragged.
- Drag **any already-selected member** in **View / orbit** mode to move the whole selection in the screen plane. For an axis constraint, use **Move object** and choose X/Y/Z. STL meshes and primitives can be moved together. Every object receives the same editor/world-space translation, converted into its own reference frame, preserving relative positions, orientations, pivots, scales and collision IDs.
- For exact offsets, use the inspector's **Move selection — editor frame** section: enter Δ X/Y/Z in mm and click **Move selection**. Values reset after applying the offset. Each group drag or numeric move is one undo/redo step, and undo/redo retains the group selection. **Frame selected** frames all visible selected members.
- If **any** selected member is locked, movement of the whole group is blocked. Unlock it using its row padlock or Ctrl-click to remove it from the selection. Live view remains read-only. Group rotation, resize, reset, snap, duplication, deletion and collision service actions are disabled or require a single selection, so those actions cannot silently modify only part of a group.
- Group moves remain local and are saved through normal scene saving. Select collision definitions individually and explicitly **Update in ROS** to apply their changed poses; group movement never publishes automatically. This is a temporary editing selection, not a persisted parent/child hierarchy.

## Files and safety

**Save scene** writes a separate `.scene.json` file with transforms, units, colors, visibility, and mesh references. STL paths are relative to the scene file; keep the source meshes with it when moving the project. Built-in primitives are stored directly in JSON. Open/save preserves the editing pivot and full mesh resolution.

**Export selected STL** writes a transformed binary STL copy in millimeters, baking its position and rotation. Original meshes cannot be overwritten. Export contains geometry only; STL has no colors or transform metadata. Scene files and exports are written atomically.

**Add / Load → Load resolved URDF** reads the running robot's resolved
`robot_description` automatically, using the domain, description topic, ROS Python
and setup paths in **ROS 2 → Connection settings…**. This is a one-shot,
read-only load of static visual geometry at zero joint positions; use Live view
for the current joint poses and planning scene. The description wait is bounded
to five seconds and runs outside the GUI thread. Reloading replaces the robot
from the previous automatic load while keeping other objects, with Undo support.
Mesh lookup also uses the package folder remembered by manual import. If a mesh
cannot be found, the editor asks for a package or workspace folder, remembers it,
and retries the automatic load. Cancelling leaves the scene unchanged.
If ROS or its description publisher is unavailable, the editor explains that
automatic resolution failed and opens a URDF file picker for manual selection.
Invalid descriptions and missing mesh resources report their specific errors.

**Import URDF file…** always opens a file picker. It supports STL, box, cylinder, and sphere visuals, visual origins, joint origins, mesh scales, and RGBA materials. For `package://` references, the mesh-folder picker accepts the package directory, a ROS install directory (merged or isolated), or a workspace root containing `install/`. The selection is remembered. Cancel that folder picker to use automatic lookup: nearby source packages, the remembered folder, the workspace setup directory in ROS connection settings, and inherited `AMENT_PREFIX_PATH` / `COLCON_PREFIX_PATH`. This also supports resolved URDFs stored separately in cache directories. Offline package lookup reads local files without starting ROS. Expand xacro separately before import; unexpanded definitions produce an explicit error. The editor does not run xacro, ROS, drivers, controllers, or launch files. Import adds independent visual objects; it does not retain robot kinematics, collision models, or editable joint relationships.

Full-resolution meshes stay on the GPU while transforms change. Large meshes can still require substantial RAM and GPU memory. Loading and exporting run in background workers; closing waits for active file operations to finish. Saving a snapshot with new inline ROS geometry writes companion STL assets as well as JSON. Transparent surfaces are sorted per object, so intersecting translucent meshes can have visual sorting artifacts.

## Checks

```bash
.venv/bin/python -m unittest discover -s standalone/scene_editor/tests -v
```

Run from the repository root with the existing environment. The geometry/model tests do not need a display or robot. GUI checks require a working OpenGL context.

```bash
xvfb-run -a .venv/bin/python -B standalone/scene_editor/tests/check_gui.py
```

Optional read-only integration check against an **already running** ROS graph:

```bash
xvfb-run -a .venv/bin/python -B standalone/scene_editor/tests/check_ros_live.py \
  --workspace-setup /path/to/ros_workspace/install/local_setup.bash
```

It checks the live robot view, the editing lock, snapshot isolation, saving/reloading, reconnection and shutdown. It never launches the stack or sends robot/scene commands. The unit suite checks frame transforms, collision diffs and attachments, marker lifecycle/frame locking, cached geometry, and persistent snapshot assets without ROS.

Collision write-path verification uses fake MoveIt services on isolated ROS domain 173, never the running robot's domain:

```bash
xvfb-run -a .venv/bin/python -B standalone/scene_editor/tests/check_collision_gui.py
```

This exercises the authoring dialogs and real ROS message/service transport for box/cylinder/sphere Add, Update and Remove; reference frames and unit conversion; duplicate/missing/attached ID guards; rejection recovery; local-only edits; and save/reload.

Multi-selection and group movement checks (no ROS required):

```bash
xvfb-run -a .venv/bin/python -B standalone/scene_editor/tests/check_group_move.py
```

## Persistent cell collision configuration

Use **Collision objects → Cell collision configuration…** in live view or offline.
The dialog connects to the backend URL (initially read from the platform's shared
`backend_network.json`) and identifies the active backend profile. It lists the
profile's independently managed equipment boxes, their requested enabled states,
and the states last confirmed by MoveIt. Select a world fixture before opening
the dialog to select the matching configuration row.

Unchecking **Enable collision checking** stages a configuration change. **Save and
apply** saves it atomically in the profile's `cell_scene.yaml`, then asks the
backend to apply a MoveIt scene diff while stationary. This changes actual robot
collision checking and survives backend restart. Visibility checkboxes remain local
and never change collision checking. Table surfaces remain enabled.

If a save succeeds but application is blocked, the dialog shows the saved values
separately from the applied state. Stop motion and use **Apply saved configuration**.
Concurrent edits produce a revision conflict; reload before editing again. A timeout
can leave an unknown result; reload rather than assuming nothing changed. No operation
automatically restarts the backend or moves the robot. The editor never writes
backend profile files directly. An older backend without the `cell_scene` section
must be rebuilt and restarted before this dialog can manage the cell.

### Configure equipment from the selected object

Select an equipment collision box in the viewport or Scene Explorer, then
right-click it. **Enable collision checking (save)** and **Disable collision
checking (save)** use the same backend configuration URL as the configuration
dialog, read a fresh revision, and save/apply only that fixture's enabled state.
These commands work in live view and editable snapshots. **Cell collision
configuration…** opens the full dialog with the selected equipment row highlighted.
Right-drag in the viewport still orbits the camera; a stationary right-click opens
the menu. The fixed table surfaces do not expose equipment enable/disable actions.

A disabled fixture remains as a dim, locked, selectable preview during the current
connection so you can right-click it and enable it again. This preview is not a
MoveIt obstacle. The backend's removal/restoration is the actual collision change.
Previously disabled fixtures after reconnecting can be restored from the saved
configuration dialog. Failed writes do not change the displayed applied state;
saved-but-pending results remain pending until the backend can apply them.

### Merge equipment collision objects

Ctrl-click two or more equipment collision objects in the viewport or Scene
Explorer. Right-click the selection and choose **Merge selected collision objects
(save)…**, then enter a unique name using letters, digits and underscores.
The backend saves one compound object containing the original boxes. Their exact
sizes, positions, rotations and intervening gaps are preserved; no bounding box,
convex hull or mesh simplification replaces them. The compound is rendered and
selected as one object and its collision-enabled state controls every part.

All selected objects must belong to the active profile, use the same reference
frame, and have the same enabled state. Table surfaces and robot links cannot be
merged through this action. Previously merged groups can be merged again with
other objects. The source definitions remain in the profile as disabled members,
so startup removes their old world IDs instead of duplicating the grouped geometry.
Grouping survives backend restart. A saved-but-pending merge leaves the currently
applied objects intact until the backend confirms application.
