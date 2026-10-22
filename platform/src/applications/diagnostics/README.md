# Diagnostics desktop application

Run from the repository root with no parameters:

```bash
.venv/bin/python -m src.applications.diagnostics
```

This read-only MVC application uses a narrow service interface and the shared
ApplicationFactory/BackgroundWorker lifecycle. It starts no robot, backend,
recorder or machine settings service. The engine's existing directory precedence
selects the initial folder. Choose another folder to inspect copied machine logs
or a legacy failure-register directory.

Select a time window (including a custom local interval), minimum severity and
text search. Search includes IDs, sources, user IDs, messages and fields. Refresh
runs on a background worker; optional live refresh polls every three seconds and
never overlaps readers. The table shows the newest 500 matching records in time
order; selecting one shows its captured JSON fields and traceback. English and
Bulgarian UI text supports switching during use. Raw logs/IDs remain untranslated.

Each scan is limited to 32 files, 64 MiB and about two seconds of processing;
directory inventory is limited to 128 entries. Limits and corrupt/incomplete
records are disclosed. Local file reads can still wait on the filesystem. History
may rotate during a scan, and truncated details or records lost before persistence
cannot be reconstructed. Empty results do not establish correct machine behavior.
Export incident writes a new ZIP with events, a readable timeline, reconstructed
inline snapshots and a gap/completeness manifest. Selecting an operation-associated
event exports that exact retained operation with display filters cleared; otherwise
the current filters apply. Evidence transport parts are hidden in the table and
included for export reconstruction. File/byte/time/500-event limits still apply and
are disclosed. Existing destinations are never overwritten. Images/bundle contents
and consistent indexed history/export remain future work.
The app reads existing JSONL and adjacent failure_register.jsonl, without moving
or deleting the RobotSystem's legacy evidence. A zip support archive must first
be extracted into a directory.

The standalone runner offers the real service; example_usage uses a stub for UI
development. The application is not yet registered as a machine-shell folder.
