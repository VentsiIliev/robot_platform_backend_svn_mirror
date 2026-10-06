# Documentation audit — 2026-10-06

## Scope and organization

The audit compares checked-out files with `docs/`, corrects current guides, and provides source-backed coverage for every Python module. Production code is unchanged; findings are recorded in [CODE_ISSUES.md](CODE_ISSUES.md).

`src/<area>/…` maps to `docs/<area>/…`. Other roots keep their names. Files directly under `src/` use `docs/source/`; root utilities use `docs/utilities/`; the empty root `bootstrap/` uses `docs/environment_bootstrap/` to distinguish it from runtime `src/bootstrap/`.

The inventory covers 2,016 Python files across `src`, `pl_gui`, `tests`, `scripts`, `packaging` and root utilities. There are 525 directly populated Python directory references. Including parent/resource/empty directories, the source index covers 688 directories. The resource inventory covers 565 non-Python files in 152 directories. These counts describe this checkout, including vendored libraries, templates, examples and test modules; they are not a count of production features.

The [source index](SOURCE_INDEX.md) and [resource index](RESOURCE_INDEX.md) enumerate the coverage. `MODULES.md` records directly declared classes, decorators, bases, constructors/public methods, top-level functions, fields/default expressions, package import/export surfaces, imports and source docstrings. `RESOURCES.md` records filenames/formats without copying machine settings, accounts, captures or binary/model content. README navigation follows the directory tree.

## Corrections and additions

- Added a root guide and guides for bootstrap, GUI framework, config, packaging, tests, scripts and source utilities.
- Added missing application coverage for EtherCAT diagnostics, hand-eye calibration, intrinsic calibration capture and shaft alignment, plus all nested MVC/support modules.
- Added welding, twin-robot, paint automatic-dryer/tray-dryer and robot-system blueprint coverage, including owned application/provider/domain/storage folders.
- Added missing shared declarations and CAD-directory documentation. CAD and the root environment-bootstrap directory are empty/reserved, not implemented services.
- Added nested references throughout robot/hardware/vision/process code, application editor infrastructure, robot-system processes, vendor libraries, tests and maintenance tooling.
- Moved vision core/features/services/PLVision guides under `engine/vision/implementation/…` and glue dashboard/settings guides under `robot_systems/glue/applications/…`. Older guide locations remain redirects for bookmarks.
- Converted old-checkout absolute links to portable relative links. Removed links to two historical test-review artifacts absent from the checkout and identified their absence explicitly.
- Corrected startup selection: current startup reads `config/platform.json`, loads a provider dynamically and builds the configured ROS bridge. Lazy factories run on first application open.
- Corrected engine isolation claims: Qt localization/demo utilities and glue-dependent weight contracts are current exceptions. Glue domain services also import injected engine contracts.
- Corrected robot motion completion defaults to 5 mm, 1.2°, three consecutive samples and fresh-driver reads, and polling interval to nominal 0.02 seconds. Removed the obsolete claim that state monitoring constructs its own Fairino connection. Preserved intentional `move_ptp()` → driver `move_linear()` behavior.
- Corrected shared contract documentation: vision/camera topics are implemented, robot config/targeting changes are separate events, and shared topic imports do not provide compile-time validation of topic values/payloads.
- Replaced paint guides describing removed DXF/alignment/pivot-projection modules and unconditional fixed execution order. Current guides describe matcher adaptation, preparation, contact planning, execution collaborators and the business machine. Previous detailed geometry descriptions are preserved with explicit superseded status in `archive/`.
- Corrected paint movement-group/work-area declarations, application folders, camera-layout switch and tray-edit/settings-update distinctions. Individual placement removal can occur during production; New Tray has a process-state gate. Active workpieces retain configuration snapshots.
- Identified plans/backlogs/older reports as proposals or historical snapshots rather than current implementation guarantees.

## Verification

The repository test runner completed in approximately 51 seconds and discovered 3,336 tests: 3,312 passed, 23 skipped, no assertion failures and one Unix-socket bind error caused by sandbox permission. That one test passed on rerun outside the socket restriction:

```bash
.venv/bin/python -m unittest tests.engine.remote_support.test_controller.RemoteSupportControllerTests.test_client_and_controller_exchange_status_over_unix_socket -v
```

Seven defects were independently reproduced with local fakes/objects by `docs/_tools/reproduce_code_issues.py`. They include register-write recursion, repeated-start exclusivity release, a manager callback deadlock, sequence stop/advance cancellation, non-finite startup values incomplete orientation acceptance and missing jog responses normalized to success. The report separates these from architecture and unfinished-integration observations.

All Python source/reference input files parse without importing production code. The generator's check mode verifies complete file/directory coverage and freshness. The documentation checker validates local target existence, Markdown anchors, portable paths and JSON syntax. `serve_docs.py:474` produces one `SyntaxWarning` for an invalid escape sequence while being parsed; the reference generator does not modify that source.

Run from the repository root:

```bash
python3 docs/_tools/build_source_reference.py --check
python3 docs/_tools/check_docs.py
.venv/bin/python docs/_tools/reproduce_code_issues.py
```

The full test log for this audit was written to `/tmp/platform-doc-audit-tests.log`; this is a temporary session artifact, not a committed test report. The test runner writes its ordinary `.coverage` output. No production launch, live robot motion, serial operation, camera calibration, deployment or release was performed as part of documentation generation/reproductions.

## Coverage limits and maintenance

Structural/API coverage is comprehensive for the inventoried checkout. It does not establish that every algorithm/docstring is behaviorally correct or that every hardware combination works. Module docstrings are identified as source descriptions rather than independently verified guarantees. Private method bodies, shell-script behavior and binary manuals/models remain at their linked source locations. Guides explain integration/ownership; generated references prevent missing-module gaps.

Plans, historical reports, hardware manuals, Bulgarian calibration material and external reference files are preserved. Their proposed paths, numerical examples and device specifications are not silently rewritten into current implementation claims. The local documentation server supports only a Markdown subset and does not serve source/assets; editor/repository links are the verification path for those files.

For future changes, update the owning narrative guide, regenerate references, run both documentation checks, and review removed/renamed paths. The generator preserves guide prose and updates only its references/indexes/marked navigation. It does not automatically delete documentation for removed source paths; stale directories need deliberate review. External URLs are not fetched by the checker, and JSON syntax validation is not semantic machine-config validation.
