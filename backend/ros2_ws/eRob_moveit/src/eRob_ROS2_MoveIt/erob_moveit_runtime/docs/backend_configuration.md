# Backend profile configuration

The backend profile is the authority for robot configuration. The platform is a
client of the backend configuration API; the backend also starts independently.
The API shares the existing backend HTTP listener and connection settings.
It does not start ROS, restart the backend, release a collision hold, or move the robot.

## Ownership

| Data | Owner |
| --- | --- |
| Absolute TCP calibration, relative tool geometry, reference tool, tool collision binding | Backend profile `calibration.yaml` |
| USER / work-object transforms | Backend profile `calibration.yaml` |
| Sensorless controller, monitor/model, collision stop and recovery settings | Backend profile `sensorless_collision.yaml` |
| Tool display names, magazine slots, pickup/dropoff procedures, selected IDs, process/UI settings | Platform robot-system storage |
| Calibration measurements and timestamps | Platform history; evidence, never replayed configuration |

Platform tool activation selects an existing backend tool. It never composes or
uploads geometry. A tool without a backend definition must be explicitly edited
or calibrated before activation. Backend TCP values take precedence over older
platform offsets.

Old platform geometry is retained under `legacy_backend_geometry` when that
settings file is next saved. This is migration evidence, not operational settings.
It is never uploaded automatically. Existing backend absolute TCPs are preserved
exactly; no transforms are inferred from old platform files.

## HTTP contract

All routes are relative to the configured backend URL.

| Method | Route | Purpose |
| --- | --- | --- |
| GET | `/configuration` | Active profile and supported sections |
| GET | `/configuration/calibration` | Saved and applied frame configuration, resolved tools, revision |
| GET | `/configuration/sensorless_collision` | Saved/effective profile values, observed controller values, revision |
| PATCH | `/configuration/<section>` | Validated partial changes |
| PATCH | `/configuration/calibration/tools/<id>` | Explicit absolute or relative tool edit |
| PATCH | `/configuration/calibration/workobjects/<id>` | Explicit work-object edit |
| POST | `/configuration/<section>/apply` | Retry application of the saved revision |

Read before editing. Every mutation requires the revision from that read:

```json
{
  "expected_revision": "revision returned by GET",
  "changes": {
    "reference_tool_id": 1,
    "relative_transform": [0, 0, 25, 0, 0, 0],
    "collision_profile": ""
  }
}
```

This example is a tool-route payload. Transform units are millimetres and degrees.
The reference tool is set through `REFERENCE_TOOL_ID` in the calibration section.
Reference TCP calibration uses an absolute `transform`. Relative tool translation
is rotated by the reference orientation; orientation offsets retain the existing
platform Euler-addition convention. Cycles and missing references are rejected.
Relative edits are not a switch to general rigid-transform composition.

Sensorless edits use nested section patches, for example:

```json
{
  "expected_revision": "revision returned by GET",
  "changes": {"monitor": {"confirm_duration_ms": 50.0}}
}
```

Revisions cover effective values (including inherited values), the selected
profile, and section. A stale/wrong-profile revision returns HTTP 409. Validation
errors return 400; unavailable storage returns 503. There is no profile-switch
endpoint or client-supplied filesystem path.

A successful configuration response includes:

- `profile`, `section`, `revision`;
- `saved`: effective values saved for the selected profile, including inheritance;
- `applied`: runtime values, or null when they cannot be observed;
- `pending_application`, `application_error`, `restart_required` (null when runtime state is unknown);
- `tools`: resolved absolute TCPs plus canonical relative definitions for the editor.

`success: true` means the save succeeded. It does **not** mean application is
complete: clients must check `pending_application`. Do not report a pending save
as a completed calibration. Retry `/apply` with the saved revision, or restart the
backend as appropriate. Application errors do not silently discard a durable save.

## Persistence and runtime application

Domain validation, application use cases, YAML storage, runtime application, and
HTTP transport are separate modules under `scripts/configuration/`. Domain and
application code have no Flask or ROS dependency. The repository/runtime ports
allow a different store or transport without changing validation/use cases.

The repository serializes cooperating writers with a profile lock, checks the
revision, writes a temporary sibling file, flushes/fsyncs, atomically replaces the
original, then fsyncs its directory. Runtime changes happen only after persistence.
Sensorless files retain explicit includes and store only profile differences;
shared files and other profiles are never written by this API.

On an explicit calibration save, legacy `TOOL_REGISTRY` and collision bindings
become canonical `TOOL_DEFINITIONS`. Each tool has either an absolute `transform`
or `reference_tool_id` plus `relative_transform`, with optional `collision_profile`.
Runtime registries are derived from these definitions on standalone startup.
Read-only access does not rewrite calibration files.

Calibration application requires an idle executor, an empty motion queue, stopped
Cartesian Servo, and a fresh stationary joint-state sample. The execution lock is
held while applying frames. Busy/unavailable runtimes leave the saved revision
pending. The adapter preserves dictionary identities used by existing planner
imports and attempts to restore the previous frames if application fails.

The sensorless controller applies commands and reports state; it no longer writes
profile files. The backend persists settings and uses a unique command ID to
confirm the matching controller response. Controller parameter reports are actual
declared values, not an assumption that the saved file was applied. Stale reports
are unavailable. Supported live monitor settings apply immediately; controller,
model and runtime/stop/recovery changes remain pending until a backend restart.
No restart or observer recalibration is triggered by a configuration save.

Collision suppression is a transient process command, separate from a persistent
configuration edit. Diagnostics commands also remain transient. Direct ROS
configuration messages affect runtime only; durable changes use this API (or the
profile file while stopped). Offline model-fitting tools may still explicitly edit
profile files; revision checks detect those edits on the next API save.

## Compatibility

Existing `/tool/registry`, `/workobject/registry`, and collision monitor REST write
routes delegate to the same configuration application. They do not introduce a
second file writer. Legacy registry writes require `persist: true` and report a
pending application as unsuccessful, while retaining the saved revision/status.
Legacy routes do not supply an editor-held revision; new editors must use the
revision-checked configuration routes. The platform tool and sensorless editors
use the new routes through their configured robot connection, without a separate
hardcoded localhost client. Work-object calibration retains its compatible route
and platform measurement history.

This API deliberately exposes registered sections rather than arbitrary backend
YAML or parameter names. Extend the section schema, repository registration,
runtime adapter and tests together for additional backend configuration.
