# Robot platform documentation

This documentation follows the checked-out project structure. `src/engine/…` maps to `docs/engine/…`, `src/applications/…` to `docs/applications/…`, and `src/robot_systems/…` to `docs/robot_systems/…`. Other project roots retain their names. The `source/` page covers files directly under `src/`; `utilities/` covers root Python utilities.

Start with the guides for behavior and integration. Each Python directory has a **Module reference** with source links, directly declared signatures, fields/defaults, imports and docstrings. The [complete source index](SOURCE_INDEX.md) enumerates every Python directory, including nested services, models, controllers, views, vendor implementation, examples and tests. Generated references are structural coverage; they do not certify that source docstrings or implementations are correct.

| Project area | Guide | Responsibility |
|---|---|---|
| `src/bootstrap/` | [Bootstrap](bootstrap/README.md) | Configuration, backend startup, shell, login and lazy application loading |
| `src/engine/` | [Engine](engine/README.md) | Shared motion, messaging, hardware, persistence, auth, vision and updates |
| `src/applications/` | [Applications](applications/README.md) | Shared MVC screens and reusable application infrastructure |
| `src/robot_systems/` | [Robot systems](robot_systems/README.md) | Machine declarations, providers, runtime composition and domain processes |
| `src/shared_contracts/` | [Shared contracts](shared_contracts/README.md) | Event payloads, topics, declarations and common values |
| `pl_gui/` | [GUI framework](pl_gui/README.md) | Shell, settings framework and dashboard widgets |
| `tests/` | [Tests](tests/README.md) | Unit, integration, architecture and packaging checks |
| `scripts/` | [Scripts](scripts/README.md) | Calibration, migration, diagnostics and hardware proving tools |
| `config/` | [Configuration](config/README.md) | Startup configuration, products, factory defaults and update sources |
| `packaging/` | [Packaging](packaging/README.md) | Product releases, installation and remote-support deployment |
| `bootstrap/` | [Environment bootstrap](environment_bootstrap/README.md) | Environment preparation outside application startup |
| Root utilities | [Utilities](utilities/README.md) | Documentation viewer and coverage runner |

## Development and verification

Run from the repository root using its existing environment:

```bash
.venv/bin/python src/bootstrap/run_main.py
.venv/bin/python tests/run_tests.py
.venv/bin/python -m unittest tests.bootstrap.test_startup_config -v
python3 docs/_tools/build_source_reference.py --check
python3 docs/_tools/check_docs.py
```

The repository has a root [requirements.txt](../requirements.txt), packaging manifests, and the shell's own [pyproject.toml](../pl_gui/pyproject.toml). Use [packaging instructions](../packaging/README.md) for deployment; a virtual environment does not itself describe the complete ROS/backend/OS installation. Application example runners vary: some use stubs, others start real camera/robot composition. Read each runner before executing it.

The checked-in startup selection is `paint_tray_dry` in [config/platform.json](../config/platform.json). Its UI currently bypasses login and the splash, disables the custom keyboard, and uses a fixed-size window. These are checkout values, not defaults or deployment recommendations. Configuration dataclass defaults are documented in [bootstrap](bootstrap/README.md).

`python3 serve_docs.py --no-open` serves the local Markdown viewer at port 7000. Its renderer supports a subset of Markdown and does not serve linked Python, JSON, PDF or image files; use an editor/repository browser for those source and asset links.

## Audit and maintenance

[Code issues](CODE_ISSUES.md) records reproduced defects and separately identified architecture/implementation limitations. [Audit notes](DOCUMENTATION_AUDIT.md) record scope, corrections and validation. Production Python code was left unchanged during this documentation audit.

After a code change, update the owning guide and run the reference generator, then both checks above. The generator preserves hand-written guide text and owns `MODULES.md`, `SOURCE_INDEX.md` and marked navigation blocks. It reads syntax without importing modules or contacting hardware. It does not automatically remove pages for deleted modules: review deletions against the source index.

Plans in `plans/`, fixes/backlogs in `fixes/`, and dated review reports describe proposals or earlier snapshots. They are not proof that a feature is implemented. Superseded technical guides are retained in [archive](archive/README.md). Hardware manuals, Bulgarian calibration documents, spreadsheets and external references remain supporting artifacts with their existing filenames; current Python contracts live in the source-aligned guides.
