# `pl_gui/shell`

This page follows the source directory. The reference below records its modules and contracts; follow child guides for nested implementations.

[Parent guide](../README.md).

<!-- source-navigation:start -->
## Source navigation

[Module reference](MODULES.md) — signatures, fields, imports and source links for every Python file in this directory.

| Source subdirectory | Guide |
|---|---|
| `base_app_widget/` | [base_app_widget](base_app_widget/README.md) |
| `resources/` | [resources](resources/README.md) |
| `ui/` | [ui](ui/README.md) |

[Complete source index](../../SOURCE_INDEX.md).
<!-- source-navigation:end -->

## Active-operation close veto

Application `can_close()` guards navigation, logout and normal main-window close. A main-window veto ignores the event before cleanup. Forced teardown is separate; controllers must retain workers until they exit.

## Context-sensitive onboarding action

`Header` owns a generic, initially hidden help button and emits
`help_requested`. `AppShell` determines availability from the currently displayed
application widget:

- a callable `start_onboarding_tour()` shows and enables the help button
- applications without that capability keep the button hidden
- returning to the folder page hides the button

The shell never imports application or robot-system tour code. Each application
owns its steps, targets, translations, and cleanup. The shared header tooltip uses
the `Header` context and source string `Take a tour`.
