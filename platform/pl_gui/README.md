# Robot shell package pilot

`zeroerr-robot-shell` installs the existing `pl_gui` Python namespace. Copy this
directory, including `pyproject.toml`, into a standalone repository to build it.
It does not need the engine, robot systems or parent repository to build/run the
core shell. No application import migration is required.

From the platform repository, use your chosen development environment:

```bash
python -m pip install -e ./pl_gui
# Existing dashboards also require the vision extra:
python -m pip install -e './pl_gui[vision]'
python -m pip wheel --no-deps ./pl_gui --wheel-dir /tmp/robot-shell-wheels
```

Normal pip installs resolve the declared dependencies. These commands are opt-in;
the platform's existing `.venv`, `requirements.txt` and launcher remain usable.
The core shell/settings/widgets require PyQt6 and QtAwesome. Dashboard trajectory
widgets and the camera demo additionally require the `vision` extra. Native Qt
runtime requirements remain operating-system dependencies.

Public integration points include `pl_gui.shell.AppShell.AppShell`,
`pl_gui.shell.app_descriptor.AppDescriptor`, `pl_gui.shell.shell_config.ShellConfig`,
and the shared settings schema/widgets. Applications are supplied through widget
factories; the shell does not discover or import concrete robot systems.

The distribution includes dashboard and shell image/icon assets. Applications
still supply localization catalogs and system-specific images/configuration;
this pilot does not relocate those resources. Older dashboard modules contain
optional legacy icon/style fallbacks; those paths are not package dependencies.

Package names are explicitly listed because the existing directory is both the
package and the standalone project root. Add new subpackages to the list in
`pyproject.toml`; the packaging test checks coverage. Once extracted, a conventional
`src/pl_gui/` layout can replace this mapping without changing imports.

Verify independent source-distribution/wheel packaging and offscreen shell startup:

```bash
.venv/bin/python -m unittest tests.architecture.test_shell_package -v
```

See [the migration plan](../docs/plans/package_migration.md) for the other package
boundaries. That link refers to this monorepository; copy the plan separately when
extracting the shell repository.
