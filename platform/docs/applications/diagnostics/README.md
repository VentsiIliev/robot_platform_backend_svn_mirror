# Diagnostics desktop application

Run `.venv/bin/python -m src.applications.diagnostics` from the repository root.
There are no required command-line parameters. The app is independent of the
machine shell and starts no robot, backend or recorder.

The shared application follows the existing blueprint: `DiagnosticsApplication`,
`DiagnosticsApplicationFactory`, `DiagnosticsModel`, `DiagnosticsView`,
`DiagnosticsController` and the stdlib-only `IDiagnosticsService` boundary.
`DiagnosticsApplicationService` reads retained engine JSONL plus an adjacent legacy
failure register. The model delegates I/O; the controller uses BackgroundWorker;
the view owns semantic filter/selection signals and shared Qt styling. Factory
ownership keeps the controller alive and cleanup stops workers/timers.

The UI provides folder selection, preset/custom local time intervals, minimum
severity, text search, optional live refresh, a chronological table and selected
event JSON/traceback. Raw values remain untranslated; English and Bulgarian chrome
supports initial translation and runtime retranslation. No broker is needed.

**Export incident** reads the selected event's exact operation, including evidence
transport records and clearing display time/search/severity filters. If it has no
operation ID, the current filters are exported. The new exclusive ZIP contains raw
events, a readable UTC timeline, reconstructed inline evidence and a completeness
manifest. Transport parts are hidden in the table. Limits, partial capture, missing
expected evidence and unavailable receipts remain explicit. The same controller
worker handles reading/exporting and preserves the displayed timeline on export
failure. Source logs/settings remain unchanged; external artifact files are not copied.

Readers coalesce filter changes while work is active and discard obsolete query
results. Scans cap files, bytes, processing time and returned rows. Parse errors,
incomplete writes, missing files and limits are visible. The newest 500 matching
events are displayed, without claiming complete capture or consistent live exports.
Local filesystem reads can still block. This UI does not inspect images/bundles,
change settings, manage retention or repair corrupt evidence.

The standalone runner injects the real service and localization. The source
`example_usage.py` injects `StubDiagnosticsService` for development. Tests cover
reader filtering/limits/corruption, controller coalescing, off-thread factory reads,
read-only behavior and initial/runtime language changes.

See [engine diagnostics](../../engine/diagnostics/README.md) for machine paths,
captured action coverage and recorder reliability limits.
