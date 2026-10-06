# `tests/` — Verification suite

`tests/run_tests.py` discovers `test_*.py` with `unittest`, enables coverage using `.coveragerc`, sets `QT_QPA_PLATFORM=offscreen` unless already set, and cleans the runner's `tests/MagicMock` artifact. It reports pass/failure/error/skip counts and exits unsuccessfully when a test fails. Run it from the repository environment:

```bash
.venv/bin/python tests/run_tests.py
.venv/bin/python -m unittest tests.bootstrap.test_startup_config -v
```

The tree mirrors production areas: `bootstrap`, `engine`, `applications`, `robot_systems`, and `shared_contracts`. `architecture` checks package boundaries and shell packaging. `integration` covers combined behavior. `scripts` covers migration tools; `container` contains test/container support. The `compact_paint` test directory is a historical test location; there is no current `src/robot_systems/compact_paint` package.

Qt tests require a working Qt runtime even with the offscreen plugin. Hardware interfaces should be replaced with stubs/fakes. Some tests intentionally exercise local sockets, temporary repositories and packaging subprocesses; sandbox restrictions can prevent these operations. Failure logs containing errors from intentionally failing mocks are not equivalent to unittest failures.

The audit ran 3,336 tests: 3,312 passed, 23 skipped, and one Unix-socket bind failed under the sandbox. That one test passed when rerun with socket permission. No assertion failure was reported. This is a snapshot, not a claim of full branch/behavior coverage; see [audit notes](../DOCUMENTATION_AUDIT.md) and [issues](../CODE_ISSUES.md).

Every test module has a source reference beneath its corresponding folder. Review test bodies to understand what is mocked and what each assertion actually proves. Full test execution writes `.coverage`; it does not run or enable the production application.

<!-- source-navigation:start -->
## Source navigation

[Module reference](MODULES.md) — signatures, fields, imports and source links for every Python file in this directory.

[Resource reference](RESOURCES.md) — non-Python files and their formats; values remain in the owning storage/source files.

| Source subdirectory | Guide |
|---|---|
| `applications/` | [applications](applications/README.md) |
| `architecture/` | [architecture](architecture/README.md) |
| `bootstrap/` | [bootstrap](bootstrap/README.md) |
| `container/` | [container](container/README.md) |
| `engine/` | [engine](engine/README.md) |
| `integration/` | [integration](integration/README.md) |
| `robot_systems/` | [robot_systems](robot_systems/README.md) |
| `scripts/` | [scripts](scripts/README.md) |
| `shared_contracts/` | [shared_contracts](shared_contracts/README.md) |

[Complete source index](../SOURCE_INDEX.md).
<!-- source-navigation:end -->
