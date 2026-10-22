# Machine diagnostics

Bootstrap composes an optional `IDiagnosticsService` before application startup;
`setup_logging()` configures console logging only. The writer captures INFO and higher records from the Python logging
hierarchy, including exceptions. Startup records the configured release, platform and backend versions. Console logging defaults to INFO. Structured
observations remain enabled independently of component logger verbosity when the
diagnostics capability is enabled.

## Enable, disable and resource policy

Edit the single platform policy in `config/platform.json`, then restart:

```json
"diagnostics": {
  "enabled": true,
  "capture_logs": true,
  "console_events": false
}
```

`enabled: false` selects `NullDiagnosticsService`: no recorder, writer/console
worker, diagnostics directory creation, database or log writes. Structured calls
become no-ops and Paint evidence adapters return before reading/copying domain
state. `ROBOT_PLATFORM_DIAGNOSTICS_ENABLED=0` or `=1` overrides the JSON flag for
one launch; other values and non-boolean JSON flags are configuration errors.
An omitted JSON section keeps history enabled, compatibility capture enabled and
structured console projection disabled. This default retains successful and failed
events and timing detail; it does not sample them away.

`capture_logs: false` disables only ordinary Python-log capture. Explicit events
and evidence still persist. `console_events: true` adds the optional structured
event console worker; filtering happens before its queue, and persistence is
independent of console verbosity. Ordinary console handlers remain available with
any diagnostics policy. Legacy Paint images, trajectory exports, failure registers
and backend-owned logs have their existing independent switches/lifecycles; this
policy currently controls the shared engine recorder and its inline evidence.

`EngineContext.diagnostics_service` exposes the narrow lifecycle/status contract.
Constructing an engine without the capability injects a no-op service. Bootstrap
owns start/close, draining on normal exit and startup exceptions. Status distinguishes
disabled, not_started, recording, unavailable and stopped; capture failure is not a
machine readiness requirement. Start/close are idempotent for the bootstrap owner;
close is terminal, and policy changes require a fresh process. A successful start
records `diagnostics.capture.started` with the capture policy. Bootstrap reports
disabled/unavailable state to the console. No history is written while disabled:
an empty interval is a capture gap, never evidence that nothing happened.

Disabled evidence skips identity allocation, bounded copying, encoding and hashing.
Enabled Paint settings use explicit dataclass expansion inside the bounded snapshot
walker instead of an unbounded `asdict()` copy followed by a second traversal.
Other inputs remain primitive-only unless the domain explicitly opts in. Saturated
or closed recorder ingress rejects before copying fields/formatting tracebacks,
while preserving rejection counts and the existing ordered loss epochs.

Local development probe (1,000 ordinary events, 30 default Paint settings pairs,
temporary storage, compatibility capture and console projection disabled): event
caller median about 14 µs, p95 33 µs; settings-pair median about 1.4 ms versus about
2.0 ms before removing the redundant copy. Disabled calls/adapters returned in
under 1 µs median. No drops/omissions occurred in that sample. These are observed
caller costs, not CPU budgets, durability latencies or real-time bounds. Scheduler
outliers, Python GIL contention, writer disk/CPU load and target-machine load still
require the Phase 8 sustained-load comparison. The queue remains item-bounded,
not a hard process-RSS cap; no production resource guarantee is inferred here.

Structured `observe()` events now enter the engine recorder directly, including
successes, without traversing synchronous Python log handlers. Runtime start/close
explicitly binds/unbinds the existing emitter facade. Their console projection
uses a separate bounded daemon queue (256 pending records); console failure/loss
does not determine persistence or hardware outcomes. Ordinary Python logging is
still a compatibility path and may synchronously invoke other installed handlers.
Pump command/valve diagnostics use the direct path, including exception outcomes.

The writer owns a bounded queue of 2,048 observations, rotating UTF-8 JSONL logs and SQLite lifetime
statistics. Producers enqueue observations without waiting for filesystem I/O.
A single writer lease prevents two applications from using the same directory.
The implementation targets the deployed Linux machines.

## Deployment

Directory precedence:

1. `ROBOT_PLATFORM_DIAGNOSTICS_DIR`, when explicitly configured.
2. `$ROBOT_PLATFORM_DATA_ROOT/diagnostics`, when external machine data is configured.
3. `$XDG_STATE_HOME/robot-platform/diagnostics`, or
   `~/.local/state/robot-platform/diagnostics`.

Run the service with a writable, persistent data directory. Set
`ROBOT_PLATFORM_MACHINE_ID` to the machine serial number. An unset identity is
recorded as empty; the application never invents a serial number. Preserve the
statistics database when deploying software updates. Different profile events
are recorded in the same machine history; lifetime totals belong to that machine.

Files:

- `events.jsonl` and five rotated backups: 10 MiB per file by default.
- `statistics.sqlite3`, with SQLite WAL files while running.
- `writer.lock`: the writer's exclusive lease.

`ROBOT_PLATFORM_LOG_LEVEL=DEBUG` enables console debugging. Persistent ordinary
logs remain INFO and higher. Existing debug plots, contour comparison images,
and timing CSVs are separate artifacts; this retention policy does not manage
those legacy directories.

## Events and counters

`diagnostic_context()` attaches correlation fields to ordinary logs and structured
observations. Paint runs have a run ID; execution cycles have a unique cycle ID
and stage events. Context is explicitly carried into the asynchronous dryer
release sequence and hardware-stop worker. Camera streams are session-scoped;
the capture and matching operations are cycle-scoped.

`observe()` accepts an event name, fields and additive metric samples. Metric
names must be stable and bounded: never put cycle IDs, paths, workpiece IDs or
user-entered names into metric names. Those values belong in event fields.

Each metric stores sample count, sum and maximum. Use the sum for counters and
lifetime durations. For operation durations, sample count and sum yield a mean;
maximum is the maximum observed operation duration. For output runtime, maximum
is a checkpoint fragment, not a maximum complete ON interval.

Output statistics describe successful output writes, not measured physical use:

- `*.commands.on/off`: successful commands, including repeated writes.
- `*.commanded_on_intervals`: observed ON intervals, including the first ON from
  unknown startup state. Repeated ON writes do not start another interval.
- `*.off_to_on_transitions`: successful OFF-to-ON command transitions observed
  within a session. This distinguishes transitions from an unknown-to-ON start.
- `*.commanded_on_seconds`: monotonic elapsed time between successful output
  observations, checkpointed while ON. No downtime is credited after restart.
- `*.unknown_state_events`: failed output writes.
- `*.unconfirmed_intervals`: interruption, missing observations, or application
  exit while an output still had a commanded ON state.

A pump OFF write is observed separately from its blow-off pulse. A failed
blow-off pulse therefore does not falsely leave the pump's commanded state ON.

## Reliability and support

Counters commit transactionally every five seconds and at normal shutdown.
A hard power loss can lose observations since the last checkpoint. On restart,
unfinished sessions are flagged, persisted ON states become unknown, and no
physical output state is assumed. Lifetime counters are never reset on startup.
The database has schema version 1; unknown future versions are rejected rather
than modified. Recent session metadata is bounded to 1,000 entries.

Invalid accounting data is rejected before enqueueing. Optional invalid fields
(including NaN) are omitted with an explicit count while a valid output transition
is preserved. Primitive snapshots enforce depth (6), container items (64), nodes
(256), per-string characters (4,096) and per-section character (16,384) bounds
before serialization. Unsupported objects never invoke arbitrary string/repr hooks.
Context and detail fields have independent budgets; message, source and exception
metadata also have separate budgets. A large configuration cannot consume the
cycle/action identity or source envelope. Enum values have an explicit primitive
adapter; compatibility message arguments additionally support standard pathlib
paths. An absent exception does not produce a placeholder traceback.
Arrays preserve invalid element positions as null with omission metadata. Metrics
remain finite, nonnegative additive values; signed sensor values belong in fields.
Compatibility message formatting and exception frame metadata are bounded too.

Queue overflow or a rejected record increments `diagnostics.dropped_events`.
Admission loss epochs are ordered with the queue, invalidating tracked output
certainty before a later transition can credit a missing interval. Writer-side
data errors roll back the record's SQLite changes and staged in-memory effects,
mark loss, and continue with valid records. Storage failures remain a separate
fault domain. Rejections emit bounded recorder-health records. Usage around missing
observations must be considered uncertain. Disk or database errors stop persistence and are reported
to stderr and `DiagnosticsRuntime.status`; hardware command results are retained.
Restart after fixing a persistence failure. Shutdown drains within five seconds;
an unfinished writer leaves a session unclean.

`DiagnosticsRuntime.status` includes rejection counts, dropped events, omitted
fields, console projection losses, queue depth and persistence health. These are
distinct: omitted optional detail need not mean the command record was lost.
The database schema remains version 1; SQLite and JSONL are not one atomic store.

This is the first Gate H implementation slice, not the complete machine-history
architecture. Indexed user timelines, sensor history, receipt/commit APIs, schema
redaction policies, reserved priority admission and full artifact lifecycle/shutdown
integration remain planned. Console daemon shutdown has a bounded runtime join;
this is not a guarantee that arbitrary external logging handlers can be terminated.
See `docs/plans/machine_observability_architecture.md` for the remaining gates.

## Operator actions currently captured

Bootstrap injects an `ActionRecorder` with the authentication session into the
shell adapter and the paint system's Robot Settings service. Records carry an
action ID, user ID, role, authentication mode and authentication-session ID.
Development login bypass is explicit. The actor is captured before a collision
Save worker starts and retained through its result, even if the session changes.

- `user.login` / `user.logout`: session transitions and logout close-veto outcomes.
- `navigation.application`: started and succeeded/rejected/failed; a displayed
  loader fallback is failed and links to the original loader exception ID.
- `navigation.main_menu`: started and succeeded/rejected/failed, including Back.
- `navigation.settings_tab`: selected tab using stable, untranslated IDs.
- `settings.collision.edited`: operator active-response toggle, old/new values,
  explicitly not yet persisted/applied. Backend loads do not invent operator edits.
- Collision Save: `settings.collision.save_requested`,
  `settings.collision.persistence_reported`, `settings.collision.application_reported`
  and `settings.collision.save_result`. One action links requested values,
  backend-reported saved/effective configuration, revision, pending application and
  result/error. A raised Save records a bounded traceback as
  `settings.collision.save_exception`, preserving the original error.

Saved/applied observations report the backend contract, without independently
inspecting its files or proving physical state. Legacy responses without those
fields remain unknown. A pending application can coexist with reported persistence
and a failed overall result. Snapshots retain the standard bounds/omission counts.

This is selective coverage: generic settings multi-resource Save, all other
control edits, failed login attempts, folder expansion and other applications'
actions are not yet fully instrumented. Queued actions have the same crash/loss
limits as other events. Restart the application to activate these hooks; historical
actions that were never captured cannot be reconstructed. The standalone desktop
viewer below presents the same retained history; it cannot add missing coverage.

Read committed statistics:

```bash
.venv/bin/python -m src.engine.diagnostics.report
```

## Operation evidence and incident export

`ActionRecorder.operation_context()` allocates an operation ID alongside the actor
and action ID before validation or resource acquisition. The Paint dashboard carries
that token through Start/preparation and explicitly into its worker threads. Start
acceptance, cycle execution and the terminal outcome are separate observations.
Non-dashboard entry points use explicit unknown actor identity unless supplied a
caller context. See the Paint guide for the implemented path and remaining coverage.

The engine's domain-independent `publish_snapshot(name, primitives)` captures small
immutable contributions immediately. It uses a bounded primitive copy: 4,096 nodes,
128 items/container, depth 10, 32,768 characters total and 4,096 characters/string.
The encoded payload is capped at 65,536 ASCII bytes. A manifest and indexed parts
of at most 2,048 characters use the same ordered event ingress. Parts are DEBUG
observations that persist independently of console verbosity; the desktop timeline
hides transport parts. Producers select/redact fields; arbitrary objects, geometry
and NumPy arrays are never expanded implicitly. Invalid/oversized/missing data is
reported as partial or unavailable. Paint provides raw/effective settings, selected
workpiece metadata and bounded job metadata; the core imports no Paint types.

A returned reference means submitted, with no admission or commit acknowledgement.
There is no retained provider registry, durable evidence table or background artifact
pipeline in this slice. Queue loss, crashes or rotation can remove a manifest/part.
`reconstruct_evidence()` requires every indexed part and a matching SHA-256 digest.
It distinguishes complete, partial (capture omissions), unavailable and incomplete
evidence, including conflicting retransmissions and unsupported snapshot versions.
Successful reconstruction proves the retained encoded content, not physical state
or an earlier recorder durability receipt.

The viewer's **Export incident** writes a new ZIP without overwriting an existing
file. If the selected row carries an operation ID, export rescans that exact retained
operation, including INFO/DEBUG evidence regardless of display search/severity/time
filters. Otherwise it exports the current filters. It uses one background worker;
reader/export work does not overlap. The archive contains `events.jsonl`, a readable
UTC `timeline.txt`, reconstructed `evidence/*.json` and `manifest.json`. Payload
parts remain in the JSONL and are omitted from the readable text timeline.

Exports share the reader's file/byte/processing limits and maximum 500 events.
The manifest states the actual filters/time coverage, selected machine/operation
IDs, parse/scan/selection warnings, omitted detail, missing expected evidence and
snapshot completeness. Evidence resolution caps references/part sets at 128 each.
The archive is staged beside its destination and published exclusively; failure
removes the staging file. Logs/settings/evidence sources are read-only. Only the
new archive and its output directory are created.

This export is a best-effort retained-file view, without a consistent indexed
history transaction. Losses outside the selected records remain unknown. External
artifact paths are never followed/copied; image, geometry, backend-log and physical
feedback completeness is not established. The global quota/pinning/replay/receipt
guarantees in the architecture plan remain pending.

## Standalone desktop viewer

Launch with no arguments from the repository root:

```bash
.venv/bin/python -m src.applications.diagnostics
```

The dedicated application lives in `src/applications/diagnostics`, outside helper
scripts. Choose a folder, preset/custom local time range, minimum severity and
text search. Select an event for raw captured fields and traceback. Search covers
messages, sources, actor/cycle/action IDs and settings fields. Optional live refresh
polls every three seconds through a background worker with no overlapping reads.
English and Bulgarian UI chrome supports runtime switching.

The app reads retained JSONL rotations and a failure register in the selected
folder. It starts no recorder, backend or hardware. By default it uses the machine
diagnostics directory; Open folder also supports copied logs and legacy evidence
directories. No files are moved or deleted. Extract a support ZIP before opening.
The viewer's language preference is persisted beside the diagnostics folder.
Incident exports are written only to the destination selected in the save dialog.

The table displays the newest 500 matches in time order. Each scan caps input at
32 files, 64 MiB and approximately two seconds of processing, with a bounded folder
inventory. Limits, parse failures and incomplete writes appear as warnings. The
filesystem can still block an individual read, and concurrent rotation is best
effort. The optional incident export is described above; consistent indexed history
and bundle/image inspection remain future work.
See [application guide](../../applications/diagnostics/README.md).

## Readable terminal timeline

The earlier terminal launcher remains available for compatibility:

```bash
python scripts/diagnostics.py --follow
python scripts/diagnostics.py --since "2026-10-21T10:35:00+03:00" --until "2026-10-21T10:40:00+03:00" --details
python scripts/diagnostics.py --level WARNING --last 100
python scripts/diagnostics.py --cycle-id FULL_CYCLE_ID --details
```

The launcher discovers the configured system's existing failure index without
starting Qt, services or hardware. The generic engine reader is also directly usable:

```bash
python -m src.engine.diagnostics.timeline --directory /path/to/diagnostics --evidence-directory /path/to/system/diagnostics --follow
```

The timeline merges retained `events.jsonl` rotations and optional failure indexes,
showing the last 50 matching records by default (`--last` accepts 1–10,000). It prints
local dates/times; `--utc` changes display to UTC. ISO range values with no offset
are interpreted in the machine's local timezone. Filters include exact `--cycle-id`,
`--run-id`, logger substring `--source` and minimum `--level`. ID filters exclude
uncorrelated records: use a time range for broader incident context.

`--details` expands fields, available metrics, bounded tracebacks and failure-bundle
section previews. Bundle/image paths report presence, not artifact integrity or
physical correctness. Data omitted during capture cannot be recovered by this tool.
The reader does not move/delete evidence, infer success or mutate machine settings.
Missing/invalid/oversized input is reported. Live following handles partial lines,
rename rotation and truncation; reading across concurrent history/rotation is best
effort and can overlap or miss records. This is a first viewer over existing files,
not the future indexed, transactionally consistent incident timeline/export.

Export a support archive:

```bash
.venv/bin/python -m src.engine.diagnostics.report --export /tmp/machine-support.zip
```

Use `--directory /path/to/diagnostics` to inspect another machine's data. Export
includes a consistent SQLite backup, summary JSON, retained log files and a
manifest. Live log files are best-effort because they can rotate during export.
An existing destination is never overwritten. Machine settings and credentials
are not added to the archive by the exporter. Log content remains the content
emitted by the application.
