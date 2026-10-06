# `src/engine/` — Engine Overview

The `engine` package is the core of the robot system platform. It provides the foundational infrastructure that all robot applications and applications build on: messaging, robot control, hardware I/O, and settings persistence. The intended boundary is reusable infrastructure. Current exceptions include glue-specific weight configuration imports and Qt-dependent localization/demo utilities; see [code issues](../CODE_ISSUES.md).

The [remote support controller](remote_support/README.md) is a standalone
engine component installed as a restricted systemd socket service on Ubuntu
robots. It is used by the shared Network Settings application.

---

## Package Structure

```
src/engine/
├── common_service_ids.py  ← CommonServiceID (robot, navigation, work_areas, vision, tools)
├── common_settings_ids.py ← CommonSettingsID (shared SettingsSpec keys)
├── core/                       ← Pub/sub messaging + cross-cutting interfaces
│   ├── i_messaging_service.py
│   ├── message_broker.py
│   ├── messaging_service.py
│   ├── i_health_checkable.py
│   ├── i_coordinate_transformer.py
│   └── dependency_container.py  ← empty placeholder (0 bytes, not imported)
├── cad/                        ← empty reserved directory; no implemented CAD service
├── geometry/                   ← planar.py: rotate/unwrap/normalize/axis-equivalent angles
├── hardware/                   ← Hardware I/O drivers
│   ├── communication/          ← IRegisterTransport, transport registry, live transport
│   │   └── modbus/             ← Modbus RTU, FC16, Xinje MA, slave config, serial bus
│   ├── xinje/                  ← XinjeMA8X8YR address map + device wrapper
│   ├── peripherals/            ← PeripheralBinding/Config + device adapters + factories
│   ├── motor/                  ← Motor controller service (IMotorService)
│   ├── generator/              ← Relay-switched generator controller + run timer
│   ├── fan/                    ← IFanControl, ModbusFanControl
│   ├── dryer/                  ← DryerService, ModbusDryerController, register model
│   ├── laser/                  ← ILaserControl, ModbusLaserControl
│   ├── vacuum_pump/            ← IVacuumPumpController, VacuumPumpController
│   ├── vacuum_sensor/          ← IVacuumSensorService, VacuumSensorService
│   ├── physical_control_buttons/ ← IPhysicalControlButtons, Modbus impl
│   └── weight/                 ← Weight cell service + HTTP transport
│       ├── interfaces/
│       └── http/
├── process/                    ← Process lifecycle state machine
│   ├── i_process.py            ← IProcess ABC
│   ├── base_process.py         ← Thread-safe BaseProcess with template hooks
│   ├── executable_state_machine.py ← Standalone FSM used by process executors
│   ├── process_requirements.py ← Service pre-condition declarations
│   ├── process_sequence.py     ← Auto-advancing ordered process chain
│   └── service_health_registry.py ← Service name → health callable for BaseProcess
│   (ProcessState, ProcessStateEvent, ProcessTopics → src/shared_contracts/events/process_events.py)
├── localization/               ← Runtime language service over Qt translators
│   ├── i_localization_service.py
│   ├── dict_translator.py
│   └── localization_service.py
├── auth/                       ← Authentication, authorization, and session
│   ├── i_authenticated_user.py
│   ├── i_auth_user_repository.py
│   ├── i_authentication_service.py
│   ├── i_authorization_service.py
│   ├── i_permissions_admin_service.py
│   ├── i_session_service.py
│   ├── authentication_service.py
│   ├── authorization_service.py
│   ├── user_session.py
│   ├── json_permissions_repository.py
│   └── permissions_migrator.py
├── system/                     ← Single-process exclusivity lock
│   ├── i_system_manager.py     ← ISystemManager ABC
│   ├── system_manager.py       ← Thread-safe SystemManager
│   └── system_state.py         ← SystemBusyState, SystemStateEvent, SystemTopics
├── repositories/               ← JSON-backed settings persistence
│   ├── interfaces/
│   └── json/
├── updates/                    ← Signed release download, verify, migrate, rollback
│   ├── config.py  updater.py  releases.py  migrations.py
│   ├── factory_defaults.py  files.py  environment.py  paths.py
├── robot/                      ← Robot control stack (see robot/README.md)
│   ├── interfaces/             ← IRobot, IMotionService, IRobotService, …
│   ├── configuration/          ← RobotSettings, RobotCalibrationSettings
│   ├── enums/                  ← RobotAxis, Direction, ImageToRobotMapping
│   ├── safety/                 ← SafetyChecker + MotionCorridor / MotionCorridorRegistry
│   ├── features/               ← NavigationService, RobotToolService
│   ├── targeting/              ← VisionTargetResolver, JogFramePoseResolver, PointRegistry
│   ├── calibration/            ← calibration services + builders + TCP/Z-shift/intrinsic capture
│   ├── height_measuring/       ← Laser height sensor services + correction interpolation
│   ├── path_interpolation/     ← ContourPathPipeline (active) + legacy deprecated/
│   ├── path_preparation/       ← Workpiece pixels → WorkpieceExecutionPlan
│   ├── procedures/             ← ServoUntilConditionProcedure + pickup conditions
│   ├── services/               ← MotionService, RobotStateManager, RobotService
│   └── drivers/
│       ├── ros2_robot.py       ← Ros2Robot (production driver)
│       ├── client_adapters/    ← HTTP/WebSocket + fake transports
│       └── fairino/            ← FairinoRobot, TestRobotWrapper
├── work_areas/                 ← IWorkAreaService, WorkAreaService, normalised polygon storage
├── vision/                     ← IVisionService interface + VisionSystem implementation
│   ├── i_vision_service.py     ← IVisionService ABC
│   ├── camera_settings_serializer.py
│   └── implementation/
│       └── VisionSystem/       ← Full camera + contour + calibration system
└── remote_support/             ← Restricted systemd socket service for the Network app
```

---

## Architecture Diagram

```
┌──────────────────────────────────────────────────────────┐
│                     robot_apps / applications            │
│           (GlueRobotSystem, ModbusSettingsApplication, …)│
└────────────┬───────────────────────────┬─────────────────┘
             │ ISettingsService           │ IRobotService / IMessagingService
             ▼                           ▼
┌────────────────────┐     ┌──────────────────────────────┐
│   repositories/    │     │          robot/              │
│                    │     │                              │
│ SettingsService    │     │  RobotService                │
│   └ BaseJson       │     │    ├ MotionService            │
│     Repository     │     │    │   ├ IRobot               │
└────────────────────┘     │    │   └ SafetyChecker        │
                           │    └ RobotStateManager        │
┌────────────────────┐     │        └ RobotStatePublisher  │
│      core/         │◄────┤                              │
│                    │     │  NavigationService            │
│ MessagingService   │     │  RobotToolService             │
│   └ MessageBroker  │     └──────────────────────────────┘
│     (singleton)    │
└────────────────────┘
             ▲
             │  IMessagingService
┌────────────┴───────────────────┐
│         hardware/              │
│                                │
│  WeightCellService             │
│    ├ HttpCellTransport         │
│    └ ICellCalibrator           │
│                                │
│  ModbusActionService           │
│  MotorService                  │
│  GeneratorController           │
└────────────────────────────────┘

┌────────────────────┐     ┌────────────────────┐
│      system/       │     │       auth/         │
│                    │     │                     │
│ SystemManager      │     │ AuthenticationService│
│ ISystemManager     │     │ AuthorizationService │
│ SystemBusyState    │     │ UserSession          │
└────────────────────┘     └────────────────────┘
```

---

## Subsystem Summary

| Subsystem | Key Entry Point | Docs |
|-----------|----------------|------|
| Messaging | `MessagingService` | [core/](core/README.md) |
| Health checks | `IHealthCheckable`, `ServiceHealthRegistry` | [core/](core/README.md), [process/](process/README.md) |
| Shared service ids | `CommonServiceID`, `CommonSettingsID` | `src/engine/common_service_ids.py`, `src/engine/common_settings_ids.py` |
| Planar geometry | `nearest_axis_equivalent_degrees`, `unwrap_degrees` | [geometry/](geometry/README.md) |
| Modbus / transports | `ModbusActionService`, `IRegisterTransport` | [hardware/communication/modbus/](hardware/communication/modbus/README.md), [hardware/communication/](hardware/communication/README.md) |
| Xinje MA I/O | `XinjeMA8X8YR`, `XinjeMA8X8YRTransport` | [hardware/xinje/](hardware/xinje/README.md) |
| Peripheral registry | `PeripheralConfig`, `build_device_control_adapters()` | [hardware/peripherals/](hardware/peripherals/README.md) |
| Motors | `IMotorService` | [hardware/motor/](hardware/motor/README.md) |
| Generator | `IGeneratorController` | [hardware/generator/](hardware/generator/README.md) |
| Fans | `IFanControl`, `ModbusFanControl` | [hardware/fan/](hardware/fan/README.md) |
| Dryer | `DryerService`, `ModbusDryerController` | [hardware/dryer/](hardware/dryer/README.md) |
| Weight cells | `WeightCellService` | [hardware/weight/](hardware/weight/README.md) |
| Laser | `ILaserControl`, `ModbusLaserControl` | [hardware/laser/](hardware/laser/README.md) |
| Vacuum pump | `IVacuumPumpController`, `VacuumPumpController` | [hardware/vacuum_pump/](hardware/vacuum_pump/README.md) |
| Vacuum sensor | `IVacuumSensorService`, `VacuumSensorService` | [hardware/vacuum_sensor/](hardware/vacuum_sensor/README.md) |
| Physical buttons | `IPhysicalControlButtons` | [hardware/physical_control_buttons/](hardware/physical_control_buttons/README.md) |
| Process lifecycle | `BaseProcess` / `IProcess` | [process/](process/README.md) |
| Localization | `LocalizationService` | [localization/](localization/README.md) |
| Auth | `AuthenticationService` / `AuthorizationService` / `UserSession` | [auth/](auth/README.md) |
| System manager | `SystemManager` / `ISystemManager` | [system/](system/README.md) |
| Settings | `SettingsService` | [repositories/](repositories/README.md) |
| Updates | `PlatformUpdater` | [updates/](updates/README.md) |
| Robot control | `RobotService` | [robot/](robot/README.md) |
| Motion safety | `SafetyChecker`, `MotionCorridor` | [robot/safety/](robot/safety/README.md) |
| Targeting | `VisionTargetResolver`, `JogFramePoseResolver` | [robot/targeting/](robot/targeting/README.md) |
| Robot calibration | `RobotCalibrationService`, `CameraTcpOffsetCalibrationService`, `ToolTcpCalibrationService` | [robot/calibration/](robot/calibration/README.md) |
| Robot drivers | `Ros2Robot`, `build_robot_client` | [robot/drivers/](robot/drivers/README.md) |
| Height measuring | `IHeightMeasuringService`, `HeightCorrectionService` | [robot/height_measuring/](robot/height_measuring/README.md) |
| Path interpolation | `ContourPathPipeline`, `smooth_points` | [robot/path_interpolation/](robot/path_interpolation/README.md) |
| Path preparation | `DefaultWorkpiecePathPreparationService`, `WorkpieceExecutionPlan` | [robot/path_preparation/](robot/path_preparation/README.md) |
| Motion procedures | `ServoUntilConditionProcedure` | [robot/procedures/](robot/procedures/README.md) |
| Work areas | `IWorkAreaService`, `WorkAreaService` | [work_areas/](work_areas/README.md) |
| Vision | `VisionSystem` / `IVisionService` | [vision/](vision/README.md) |
| Remote support | `remote_support` controller | [remote_support/](remote_support/README.md) |

---

## Startup Integration

The engine is wired together during platform startup
(`../../src/bootstrap/run_main.py`). The active robot system is selected by a
`BootstrapProvider` resolved from the startup config:

```
1. load_startup_config() → load_bootstrap_provider(startup_config)
       └─ selects the BootstrapProvider (system_class, robot, dev flags)

2. EngineContext.build()
       └─ creates the MessagingService singleton

3. SystemBuilder()
       .with_robot(build_configured_robot(startup_config))
       .with_messaging_service(ctx.messaging_service)
       .with_development_mode(dev_skip_login)
       .build(bootstrap_provider.system_class)
       ├─ build_from_specs(settings_specs, …) → SettingsService
       ├─ constructs the robot transport / driver
       └─ robot_system.on_start() composes runtime services

4. ShellConfigurator.configure(bootstrap_provider.system_class)
       └─ registers folder metadata from the system's ShellSetup

5. QApplication + localization service init
       └─ Qt must exist before any widget is created

6. AppShell (created before application loading, empty placeholder)
       └─ login gate when dev_skip_login is False

7. _load_apps_into_shell(…) — ApplicationLoader iterates visible
   ApplicationSpecs filtered by user role, calls spec.factory(robot_app),
   then rebuilds the shell's folder page
```

Runtime services are assembled by factories and system composition. Module-level constants and optional/demo code exist; inspect module imports before assuming import-time execution is side-effect free.

Robot-system-specific startup composition does not belong in `engine/` and must
not be hardcoded in `../../src/bootstrap/run_main.py`. Concrete robot driver
selection, login/auth wiring, and authorization/permissions filtering live in the
active robot system's bootstrap provider (`src/bootstrap/startup_config.py`).

---

## Design Principles

- **GUI separation** — production services generally avoid widget dependencies. Localization uses Qt core; interpolation and vacuum-sensor demo runners also import Qt widgets. Hardware/vision dependencies still need their environment even when no `QApplication` is required.
- **Interface-first** — all cross-module calls go through abstract base classes (`IRobotService`, `ISettingsService`, `IMessagingService`). Concrete classes are an implementation detail.
- **Dependency injection** — factories wire dependencies explicitly; no global state except the `MessageBroker` singleton.
- **Daemon threads** — background polling loops (`RobotStateManager`, `WeightCellService`) use daemon threads so they don't block process exit.

Note: `engine/localization/` intentionally touches Qt core translation APIs (`QCoreApplication`, `QTranslator`). It still remains GUI-agnostic: it does not import views, widgets, or application-specific code. It also persists the selected language in a small JSON state file so the shell selector and installed translator stay in sync across restarts, and it now supports layered shared-plus-robot-system catalog loading.

Platform release configuration, signed updates, external data paths and explicit
JSON schema migrations and product/profile compatibility checks live in `src/engine/updates/`. See
[installer and updater instructions](../../packaging/platform/README.md).

Factory configuration seeding in `src/engine/updates/factory_defaults.py` creates
missing files atomically from product/profile templates and preserves existing
files, including empty ones. Activation seeds its staged data copy; standalone
startup seeds before runtime settings are loaded.

<!-- source-navigation:start -->
## Source navigation

[Module reference](MODULES.md) — signatures, fields, imports and source links for every Python file in this directory.

| Source subdirectory | Guide |
|---|---|
| `auth/` | [auth](auth/README.md) |
| `cad/` | [cad](cad/README.md) |
| `core/` | [core](core/README.md) |
| `geometry/` | [geometry](geometry/README.md) |
| `hardware/` | [hardware](hardware/README.md) |
| `localization/` | [localization](localization/README.md) |
| `process/` | [process](process/README.md) |
| `remote_support/` | [remote_support](remote_support/README.md) |
| `repositories/` | [repositories](repositories/README.md) |
| `robot/` | [robot](robot/README.md) |
| `system/` | [system](system/README.md) |
| `updates/` | [updates](updates/README.md) |
| `vision/` | [vision](vision/README.md) |
| `work_areas/` | [work_areas](work_areas/README.md) |

[Complete source index](../SOURCE_INDEX.md).
<!-- source-navigation:end -->
