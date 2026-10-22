# `src/bootstrap/` — Runtime startup

Bootstrap assembles platform services, a selected robot system and the Qt shell. It owns startup configuration and presentation/session coordination; machine process implementations remain under `robot_systems`.

## Selection and configuration

[startup_config.py](../../src/bootstrap/startup_config.py) reads `config/platform.json`. `robot_system` must be a lowercase identifier present in the nonempty, duplicate-free `supported_robot_systems` list. The selected `robot_systems.<name>` object must explicitly declare `robot_driver`, `backend`, `backend_profile`, and three `major.minor.patch` version strings. Drivers/backends are limited to `zeroerr` and `fairino` and must match. Other system entries need not be supplied until selected.

`load_bootstrap_provider()` imports `src.robot_systems.<name>.bootstrap_provider`, calls `create_bootstrap_provider()`, and validates the returned provider. There is no `_BOOTSTRAP_PROVIDER` selector in the current startup entry point. `build_configured_robot()` validates system config and constructs `Ros2Robot(server_url="http://localhost:5000")` for both supported backend types; it does not call the provider's `build_robot()` in this startup flow.

UI dataclass defaults are authentication enabled, splash enabled, fullscreen, 1280×1024 dimensions, custom keyboard enabled, and account/power buttons hidden. Checked-in JSON overrides these defaults. ROS backend defaults enable auto-launch and auto-stop; paths, delay, log/status URLs and timeout may be supplied. See [module reference](MODULES.md) for all fields and validation helpers.

## Startup order

1. Configure console logging; parse config and start the optional engine diagnostics service. `diagnostics.enabled` in `config/platform.json` (or `ROBOT_PLATFORM_DIAGNOSTICS_ENABLED=0/1`) controls capture on the next launch. Bootstrap reports disabled/unavailable capture; storage failure does not gate machine startup. Resolve the provider.
2. Build `EngineContext` with the diagnostics service and start the configured ROS backend launcher. An omitted service uses the no-op implementation.
3. Build the system with the configured robot, messaging and development-mode flag. If system construction raises, stop the ROS backend and re-raise.
4. Register shell folder metadata through `ShellConfigurator`.
5. Create `QApplication`, terminal signal handlers, and the layered `LocalizationService`.
6. Create `AppShell` with empty descriptors; connect language selection, window/header controls and optional support monitor/splash/notifiers.
7. Start `ShellSessionController`. Show the provider-built login screen or establish the development stub session.
8. Filter application specs by authorization, register deferred builders and rebuild the folder page. Each application is instantiated only when opened.
9. Enter the Qt event loop. The `finally` block stops support/splash/notifiers, the robot system and backend.

The shutdown `finally` starts around `qt_app.exec()`; exceptions during earlier shell/login/localization setup are not covered by it. This limitation is recorded in [code issues](../CODE_ISSUES.md).

The diagnostics service has a separate outer `finally`, so its drain also runs on
startup exceptions. Console configuration has no recorder side effects. See the
[diagnostics guide](../engine/diagnostics/README.md) for capture policy, no-op
behavior and measured resource limits. Policy changes currently require restart.

## Lazy application lifecycle

`ApplicationLoader` stores descriptors and builders by application name. `_ApplicationManager` creates and caches the `IApplication` at first request. `_WidgetFactory` registers it with messaging once and invokes `create_widget()`; failed construction or an unavailable application returns an `AppWidget` fallback and logs the failure. Returning to an already running screen is owned by the shell. Application factories own controllers and cleanup.

`ShellSessionController` handles login/logout and guards closure of running applications. `StartupSplashCoordinator` tracks readiness through messaging. `ShellRemoteSupportController` polls support/session state for the header. `RosBackendLauncher` owns backend process startup/stop policy and readiness probes. `startup_error.py` provides the startup-error presentation entry points. These helpers are documented separately in [MODULES.md](MODULES.md).

## Localization and verification

Catalog loading order is shared application chrome, each shared app's `localization/`, then the selected system's `metadata.translations_root` as overrides. The language state file is `localization.json` under the resolved settings root. Qt must exist before translators/widgets are used. Runtime language selection updates the installed translator and shell selector.

Use `tests/bootstrap/` for startup config, lazy loading, sessions, splash and backend-launcher tests. Full application startup can launch the backend and enable robot services; it is not a hardware-free documentation check.

<!-- source-navigation:start -->
## Source navigation

[Module reference](MODULES.md) — signatures, fields, imports and source links for every Python file in this directory.

[Complete source index](../SOURCE_INDEX.md).
<!-- source-navigation:end -->

A vetoed header power-off resets the shutdown-request latch and re-enables the power button, allowing the operator to stop the operation and retry.

## Backend endpoint configuration

Backend HTTP/WebSocket hosts and ports are defined in
[`config/backend_network.json`](../../config/backend_network.json).
The launcher derives startup probes from it and passes its absolute path as
`ROBOT_BACKEND_NETWORK_CONFIG` to the backend. Legacy status URL overrides are
rejected. See [deployment and migration details](../engine/robot/backend_network.md).
