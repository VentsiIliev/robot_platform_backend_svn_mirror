# `pl_gui/` — Shared Qt shell and widget framework

This vendored package supplies `AppShell`, navigation folders, application descriptors/registry, base application widgets, schema-based settings and dashboards. It receives application widget factories; concrete robot-system selection belongs to bootstrap/composition.

## Integration and ownership

Bootstrap supplies descriptors and a widget factory. The shell creates a folder launcher, opens screens on demand and tracks running widgets. Screens must implement their cleanup/can-close contracts. The application factory retains controllers on the view and wraps `clean_up()` to stop controller/jog subscriptions before view teardown. Do not duplicate that controller ownership in each application.

`AppWidget` is the shell screen base. `settings/app/` supplies settings applications; `settings/settings_view/` supplies shared controls, handlers, groups and styles; `settings/settings_menu/` owns settings navigation. `dashboard/` contains layouts, camera/trajectory views and dashboard application helpers. `utils/` contains shared widget support. `shell/resources/` and `dashboard/resources/` are packaged icons/images; `shell/ui/` contains shell presentation modules.

## Style and touch input

Application views use `pl_gui.settings.settings_view.styles` constants for titles, backgrounds, cards and actions. Numeric application fields use the reusable `KeyboardNumberField` from `src/applications/base/widgets`; text fields use `KeyboardLineEdit`. Schema-driven application forms use shared keyboard handlers/factories. These application keyboard adapters live outside `pl_gui` so the shell package can remain independently installable.

## Packaging and verification

The shell has a real [pyproject.toml](../../pl_gui/pyproject.toml) and [package guide](../../pl_gui/README.md), including the optional vision dependency extra. Core shell/settings require Qt and QtAwesome; dashboard vision functionality has additional dependencies. See `tests/architecture/test_shell_package.py` for package coverage/build checks. Use offscreen Qt for hardware-free UI verification.

Follow the source navigation for every nested package and module. This documentation audit changes documentation only; shell/framework implementation is shared infrastructure.

<!-- source-navigation:start -->
## Source navigation

[Module reference](MODULES.md) — signatures, fields, imports and source links for every Python file in this directory.

[Resource reference](RESOURCES.md) — non-Python files and their formats; values remain in the owning storage/source files.

| Source subdirectory | Guide |
|---|---|
| `dashboard/` | [dashboard](dashboard/README.md) |
| `settings/` | [settings](settings/README.md) |
| `shell/` | [shell](shell/README.md) |
| `utils/` | [utils](utils/README.md) |

[Complete source index](../SOURCE_INDEX.md).
<!-- source-navigation:end -->
