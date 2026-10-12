# Machine diagnostics

`setup_logging()` starts one platform diagnostics writer before application
startup. The writer captures INFO and higher records from the Python logging
hierarchy, including exceptions. Startup records the configured release, platform and backend versions. Console logging defaults to INFO. Structured
observations remain enabled independently of component logger verbosity.

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

Queue overflow increments `diagnostics.dropped_events` and invalidates tracked
output states at the next checkpoint. Usage around missing observations must be
considered uncertain. Disk or database errors stop persistence and are reported
to stderr and `DiagnosticsRuntime.status`; hardware command results are retained.
Restart after fixing a persistence failure. Shutdown drains within five seconds;
an unfinished writer leaves a session unclean.

Read committed statistics:

```bash
.venv/bin/python -m src.engine.diagnostics.report
```

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
