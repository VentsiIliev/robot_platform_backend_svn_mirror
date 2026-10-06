> Documentation status: design plan/backlog or historical review. Proposed paths and behaviors may not exist in the current checkout. Use the [source index](../SOURCE_INDEX.md) and current package guides to verify implementation.

# Package dependency audit

Generated with `python scripts/audit_package_dependencies.py`. Regenerate after boundary changes.

Static AST scan of `src/` and `pl_gui/`: includes demos, nested imports, fallback imports and TYPE_CHECKING blocks. Counts are import sites, not runtime dependencies. Dynamic import strings, resources, ROS/native dependencies and dependency versions require manual review. External roots include stdlib and unresolved legacy namespaces; they are not a pip requirements list.

## Python files

| Proposed package | Files |
|---|---:|
| applications | 469 |
| bootstrap | 10 |
| contracts | 21 |
| engine | 508 |
| shell | 70 |
| system-runtime | 5 |
| system:ROBOT_SYSTEM_BLUEPRINT | 34 |
| system:glue | 199 |
| system:paint | 203 |
| system:paint_auto_dry | 3 |
| system:paint_tray_dry | 3 |
| system:twin_robot | 34 |
| system:welding | 37 |

## Dependencies

| Importing package | Imported package | Import sites |
|---|---|---:|
| applications | contracts | 57 |
| applications | engine | 218 |
| applications | shell | 318 |
| applications | system:glue | 8 |
| applications | system:paint | 3 |
| bootstrap | applications | 5 |
| bootstrap | contracts | 4 |
| bootstrap | engine | 9 |
| bootstrap | shell | 12 |
| bootstrap | system-runtime | 3 |
| contracts | engine | 2 |
| engine | contracts | 34 |
| engine | system:glue | 5 |
| system-runtime | contracts | 13 |
| system-runtime | engine | 43 |
| system:ROBOT_SYSTEM_BLUEPRINT | applications | 34 |
| system:ROBOT_SYSTEM_BLUEPRINT | bootstrap | 4 |
| system:ROBOT_SYSTEM_BLUEPRINT | contracts | 16 |
| system:ROBOT_SYSTEM_BLUEPRINT | engine | 51 |
| system:ROBOT_SYSTEM_BLUEPRINT | shell | 6 |
| system:ROBOT_SYSTEM_BLUEPRINT | system-runtime | 7 |
| system:glue | applications | 149 |
| system:glue | contracts | 57 |
| system:glue | engine | 178 |
| system:glue | shell | 37 |
| system:glue | system-runtime | 2 |
| system:paint | applications | 169 |
| system:paint | bootstrap | 2 |
| system:paint | contracts | 32 |
| system:paint | engine | 217 |
| system:paint | shell | 99 |
| system:paint | system-runtime | 4 |
| system:paint_auto_dry | system-runtime | 1 |
| system:paint_auto_dry | system:paint | 3 |
| system:paint_tray_dry | system-runtime | 1 |
| system:paint_tray_dry | system:paint | 3 |
| system:twin_robot | applications | 30 |
| system:twin_robot | contracts | 5 |
| system:twin_robot | engine | 5 |
| system:twin_robot | shell | 11 |
| system:twin_robot | system-runtime | 2 |
| system:welding | applications | 70 |
| system:welding | contracts | 18 |
| system:welding | engine | 73 |
| system:welding | shell | 5 |
| system:welding | system-runtime | 2 |
| system:welding | system:glue | 1 |

## Representative evidence

### applications → contracts

- `src/applications/aruco_z_probe/controller/aruco_z_probe_controller.py:16` → `src.shared_contracts.events.vision_events.VisionTopics`
- `src/applications/base/dashboard_camera_feed_mixin.py:6` → `src.shared_contracts.events.vision_events.VisionTopics`
- `src/applications/base/dashboard_process_state_mixin.py:6` → `src.shared_contracts.events.process_events.ProcessTopics`
- `src/applications/base/jog_controller.py:10` → `src.shared_contracts.events.robot_events.RobotTopics`
- `src/applications/base/notification_presenter.py:18` → `src.shared_contracts.events.notification_events.DismissNotificationEvent`
- 52 additional import sites; use `--json` for the complete list.

### applications → engine

- `src/applications/APPLICATION_BLUEPRINT/my_application.py:4` → `src.engine.core.i_messaging_service.IMessagingService`
- `src/applications/aruco_z_probe/controller/aruco_z_probe_controller.py:15` → `src.engine.core.i_messaging_service.IMessagingService`
- `src/applications/base/application_interface.py:3` → `src.engine.core.i_messaging_service.IMessagingService`
- `src/applications/base/jog_controller.py:9` → `src.engine.core.i_messaging_service.IMessagingService`
- `src/applications/base/notification_presenter.py:17` → `src.engine.core.i_messaging_service.IMessagingService`
- 213 additional import sites; use `--json` for the complete list.

### applications → shell

- `src/applications/APPLICATION_BLUEPRINT/my_application.py:3` → `pl_gui.shell.base_app_widget.AppWidget.AppWidget`
- `src/applications/APPLICATION_BLUEPRINT/view/__init__.py:12` → `pl_gui.shell.base_app_widget.AppWidget.AppWidget`
- `src/applications/aruco_z_probe/view/aruco_z_probe_view.py:20` → `pl_gui.settings.settings_view.styles.ACTION_BTN_STYLE`
- `src/applications/aruco_z_probe/view/aruco_z_probe_view.py:20` → `pl_gui.settings.settings_view.styles.LABEL_STYLE`
- `src/applications/base/app_dialog.py:4` → `pl_gui.settings.settings_view.styles.ACTION_BTN_STYLE`
- 313 additional import sites; use `--json` for the complete list.

### applications → system:glue

- `src/applications/calibration/controller/calibration_controller.py:16` → `src.robot_systems.glue.component_ids.ProcessID`
- `src/applications/pick_and_place_visualizer/controller/pick_and_place_visualizer_controller.py:16` → `src.robot_systems.glue.component_ids.ProcessID`
- `src/applications/pick_and_place_visualizer/service/pick_and_place_visualizer_service.py:4` → `src.robot_systems.glue.domain.matching.i_matching_service.IMatchingService`
- `src/applications/pick_and_place_visualizer/service/pick_and_place_visualizer_service.py:5` → `src.robot_systems.glue.processes.pick_and_place.config.PickAndPlaceConfig`
- `src/applications/pick_and_place_visualizer/service/pick_and_place_visualizer_service.py:6` → `src.robot_systems.glue.processes.pick_and_place.plane.Plane`
- 3 additional import sites; use `--json` for the complete list.

### applications → system:paint

- `src/applications/workpiece_editor/controller/workpiece_editor_controller.py:819` → `src.robot_systems.paint.processes.paint.config.PAINT_PROCESS_CONFIG`
- `src/applications/workpiece_editor/controller/workpiece_editor_controller.py:857` → `src.robot_systems.paint.processes.paint.config.PAINT_PROCESS_CONFIG`
- `src/applications/workpiece_editor/editor_core/adapters/workpiece_adapter.py:5` → `src.robot_systems.paint.domain.paint_workpiece_editor_adapter.PaintWorkpieceEditorAdapter`

### bootstrap → applications

- `src/bootstrap/run_main.py:21` → `src.applications.base.notification_presenter.UserNotificationPresenter`
- `src/bootstrap/run_main.py:22` → `src.applications.base.robot_connection_notifier.RobotConnectionNotifier`
- `src/bootstrap/run_main.py:304` → `src.applications.login.stub_login_application_service._StubUser`
- `src/bootstrap/run_main.py:394` → `src.applications.broker_debug.broker_debug_factory.BrokerDebugFactory`
- `src/bootstrap/run_main.py:395` → `src.applications.broker_debug.service.broker_debug_application_service.BrokerDebugApplicationService`

### bootstrap → contracts

- `src/bootstrap/application_loader.py:7` → `src.shared_contracts.declarations.system_specs.ApplicationSpec`
- `src/bootstrap/run_main.py:216` → `src.shared_contracts.events.shell_events.ApplicationShortcut`
- `src/bootstrap/run_main.py:216` → `src.shared_contracts.events.shell_events.ShellTopics`
- `src/bootstrap/startup_splash_runtime.py:7` → `src.shared_contracts.events.robot_events.RobotTopics`

### bootstrap → engine

- `src/bootstrap/application_loader.py:6` → `src.engine.core.i_messaging_service.IMessagingService`
- `src/bootstrap/build_engine.py:1` → `src.engine.core.i_messaging_service.IMessagingService`
- `src/bootstrap/build_engine.py:2` → `src.engine.core.messaging_service.MessagingService`
- `src/bootstrap/run_main.py:23` → `src.engine.localization.localization_service.LocalizationService`
- `src/bootstrap/run_main.py:24` → `src.engine.auth.user_session.UserSession`
- 4 additional import sites; use `--json` for the complete list.

### bootstrap → shell

- `src/bootstrap/application_loader.py:4` → `pl_gui.shell.app_registry.build_app_registry`
- `src/bootstrap/application_loader.py:5` → `pl_gui.shell.app_descriptor.AppDescriptor`
- `src/bootstrap/application_loader.py:58` → `pl_gui.shell.base_app_widget.AppWidget.AppWidget`
- `src/bootstrap/run_main.py:30` → `pl_gui.shell.AppShell.AppShell`
- `src/bootstrap/run_main.py:31` → `pl_gui.shell.startup_splash_view.StartupSplashView`
- 7 additional import sites; use `--json` for the complete list.

### bootstrap → system-runtime

- `src/bootstrap/run_main.py:25` → `src.robot_systems.system_builder.SystemBuilder`
- `src/bootstrap/shell_configurator.py:5` → `src.robot_systems.base_robot_system.BaseRobotSystem`
- `src/bootstrap/startup_config.py:9` → `src.robot_systems.robot_system_bootstrap_provider.RobotSystemBootstrapProvider`

### contracts → engine

- `src/shared_contracts/declarations/movement.py:6` → `src.engine.robot.configuration.MovementGroup`
- `src/shared_contracts/declarations/system_specs.py:7` → `src.engine.repositories.interfaces.ISettingsSerializer`

### engine → contracts

- `src/engine/hardware/weight/__init__.py:1` → `src.shared_contracts.events.weight_events.CellState`
- `src/engine/hardware/weight/__init__.py:1` → `src.shared_contracts.events.weight_events.WeightReading`
- `src/engine/hardware/weight/interfaces/i_weight_cell_service.py:5` → `src.shared_contracts.events.weight_events.CellState`
- `src/engine/hardware/weight/interfaces/i_weight_cell_service.py:5` → `src.shared_contracts.events.weight_events.WeightReading`
- `src/engine/hardware/weight/weight_cell_service.py:7` → `src.shared_contracts.events.weight_events.CellState`
- 29 additional import sites; use `--json` for the complete list.

### engine → system:glue

- `src/engine/hardware/weight/http/http_weight_cell_factory.py:6` → `src.robot_systems.glue.settings.cells.CellConfig`
- `src/engine/hardware/weight/http/http_weight_cell_factory.py:6` → `src.robot_systems.glue.settings.cells.GlueCellsConfig`
- `src/engine/hardware/weight/interfaces/i_cell_calibrator.py:3` → `src.robot_systems.glue.settings.cells.CalibrationConfig`
- `src/engine/hardware/weight/interfaces/i_weight_cell_service.py:6` → `src.robot_systems.glue.settings.cells.CalibrationConfig`
- `src/engine/robot/path_interpolation/new_interpolation/simple_interpolation_pyqt6.py:59` → `src.robot_systems.glue.glue_robot_system.GlueRobotSystem`

### system-runtime → contracts

- `src/robot_systems/base_robot_system.py:20` → `src.shared_contracts.declarations.DispenseChannelDefinition`
- `src/robot_systems/base_robot_system.py:20` → `src.shared_contracts.declarations.MovementGroupDefinition`
- `src/robot_systems/base_robot_system.py:20` → `src.shared_contracts.declarations.RemoteTcpDefinition`
- `src/robot_systems/base_robot_system.py:20` → `src.shared_contracts.declarations.RolePolicy`
- `src/robot_systems/base_robot_system.py:20` → `src.shared_contracts.declarations.ServiceSpec`
- 8 additional import sites; use `--json` for the complete list.

### system-runtime → engine

- `src/robot_systems/base_robot_system.py:9` → `src.engine.repositories.interfaces.ISettingsRepository`
- `src/robot_systems/base_robot_system.py:9` → `src.engine.repositories.interfaces.ISettingsService`
- `src/robot_systems/base_robot_system.py:10` → `src.engine.robot.targeting.jog_frame_pose_resolver.JogFramePoseResolver`
- `src/robot_systems/base_robot_system.py:11` → `src.engine.robot.targeting.point_registry.PointRegistry`
- `src/robot_systems/base_robot_system.py:12` → `src.engine.robot.targeting.end_effector_point.EndEffectorPoint`
- 38 additional import sites; use `--json` for the complete list.

### system:ROBOT_SYSTEM_BLUEPRINT → applications

- `src/robot_systems/ROBOT_SYSTEM_BLUEPRINT/application_wiring.py:3` → `src.applications.base.widget_application.WidgetApplication`
- `src/robot_systems/ROBOT_SYSTEM_BLUEPRINT/application_wiring.py:23` → `src.applications.user_management.domain.csv_user_repository.CsvUserRepository`
- `src/robot_systems/ROBOT_SYSTEM_BLUEPRINT/application_wiring.py:24` → `src.applications.user_management.service.user_management_application_service.UserManagementApplicationService`
- `src/robot_systems/ROBOT_SYSTEM_BLUEPRINT/application_wiring.py:27` → `src.applications.user_management.user_management_factory.UserManagementFactory`
- `src/robot_systems/ROBOT_SYSTEM_BLUEPRINT/application_wiring.py:61` → `src.applications.base.robot_jog_service_builder.build_robot_system_jog_service`
- 29 additional import sites; use `--json` for the complete list.

### system:ROBOT_SYSTEM_BLUEPRINT → bootstrap

- `src/robot_systems/ROBOT_SYSTEM_BLUEPRINT/run_demo.py:11` → `src.bootstrap.application_loader.ApplicationLoader`
- `src/robot_systems/ROBOT_SYSTEM_BLUEPRINT/run_demo.py:12` → `src.bootstrap.build_engine.EngineContext`
- `src/robot_systems/ROBOT_SYSTEM_BLUEPRINT/run_demo.py:13` → `src.bootstrap.logging_config.setup_logging`
- `src/robot_systems/ROBOT_SYSTEM_BLUEPRINT/run_demo.py:14` → `src.bootstrap.shell_configurator.ShellConfigurator`

### system:ROBOT_SYSTEM_BLUEPRINT → contracts

- `src/robot_systems/ROBOT_SYSTEM_BLUEPRINT/applications/dashboard/service/demo_my_dashboard_service.py:3` → `src.shared_contracts.events.process_events.ProcessState`
- `src/robot_systems/ROBOT_SYSTEM_BLUEPRINT/my_robot_system.py:21` → `src.shared_contracts.declarations.ApplicationSpec`
- `src/robot_systems/ROBOT_SYSTEM_BLUEPRINT/my_robot_system.py:21` → `src.shared_contracts.declarations.FolderSpec`
- `src/robot_systems/ROBOT_SYSTEM_BLUEPRINT/my_robot_system.py:21` → `src.shared_contracts.declarations.MovementGroupDefinition`
- `src/robot_systems/ROBOT_SYSTEM_BLUEPRINT/my_robot_system.py:21` → `src.shared_contracts.declarations.MovementGroupType`
- 11 additional import sites; use `--json` for the complete list.

### system:ROBOT_SYSTEM_BLUEPRINT → engine

- `src/robot_systems/ROBOT_SYSTEM_BLUEPRINT/application_wiring.py:4` → `src.engine.common_service_ids.CommonServiceID`
- `src/robot_systems/ROBOT_SYSTEM_BLUEPRINT/application_wiring.py:5` → `src.engine.common_settings_ids.CommonSettingsID`
- `src/robot_systems/ROBOT_SYSTEM_BLUEPRINT/application_wiring.py:28` → `src.engine.auth.authorization_service.AuthorizationService`
- `src/robot_systems/ROBOT_SYSTEM_BLUEPRINT/application_wiring.py:29` → `src.engine.auth.json_permissions_repository.JsonPermissionsRepository`
- `src/robot_systems/ROBOT_SYSTEM_BLUEPRINT/applications/dashboard/controller/my_dashboard_controller.py:7` → `src.engine.core.i_messaging_service.IMessagingService`
- 46 additional import sites; use `--json` for the complete list.

### system:ROBOT_SYSTEM_BLUEPRINT → shell

- `src/robot_systems/ROBOT_SYSTEM_BLUEPRINT/applications/dashboard/config.py:5` → `pl_gui.dashboard.config.ActionButtonConfig`
- `src/robot_systems/ROBOT_SYSTEM_BLUEPRINT/applications/dashboard/config.py:5` → `pl_gui.dashboard.config.CardConfig`
- `src/robot_systems/ROBOT_SYSTEM_BLUEPRINT/applications/dashboard/config.py:5` → `pl_gui.dashboard.config.DashboardConfig`
- `src/robot_systems/ROBOT_SYSTEM_BLUEPRINT/applications/dashboard/ui/demo_card_factory.py:3` → `pl_gui.dashboard.config.CardConfig`
- `src/robot_systems/ROBOT_SYSTEM_BLUEPRINT/applications/dashboard/view/my_dashboard_view.py:7` → `pl_gui.dashboard.DashboardWidget.DashboardWidget`
- 1 additional import sites; use `--json` for the complete list.

### system:ROBOT_SYSTEM_BLUEPRINT → system-runtime

- `src/robot_systems/ROBOT_SYSTEM_BLUEPRINT/bootstrap_provider.py:14` → `src.robot_systems.robot_system_bootstrap_provider.RobotSystemBootstrapProvider`
- `src/robot_systems/ROBOT_SYSTEM_BLUEPRINT/my_robot_system.py:20` → `src.robot_systems.base_robot_system.BaseRobotSystem`
- `src/robot_systems/ROBOT_SYSTEM_BLUEPRINT/run_demo.py:20` → `src.robot_systems.system_builder.SystemBuilder`
- `src/robot_systems/ROBOT_SYSTEM_BLUEPRINT/service_builders.py:5` → `src.robot_systems.default_service_builders.build_navigation_service`
- `src/robot_systems/ROBOT_SYSTEM_BLUEPRINT/service_builders.py:5` → `src.robot_systems.default_service_builders.build_robot_service`
- 2 additional import sites; use `--json` for the complete list.

### system:glue → applications

- `src/robot_systems/glue/application_wiring.py:4` → `src.applications.workpiece_editor.editor_core.config.SegmentEditorConfig`
- `src/robot_systems/glue/application_wiring.py:25` → `src.applications.base.widget_application.WidgetApplication`
- `src/robot_systems/glue/application_wiring.py:26` → `src.applications.base.robot_jog_service_builder.build_robot_system_jog_service`
- `src/robot_systems/glue/application_wiring.py:27` → `src.applications.pick_and_place_visualizer.PickAndPlaceVisualizerFactory`
- `src/robot_systems/glue/application_wiring.py:28` → `src.applications.pick_and_place_visualizer.service.pick_and_place_visualizer_service.PickAndPlaceVisualizerService`
- 144 additional import sites; use `--json` for the complete list.

### system:glue → contracts

- `src/robot_systems/glue/application_wiring.py:199` → `src.shared_contracts.events.workpiece_events.WorkpieceTopics`
- `src/robot_systems/glue/applications/dashboard/config.py:4` → `src.shared_contracts.events.process_events.ProcessState`
- `src/robot_systems/glue/applications/dashboard/controller/glue_dashboard_controller.py:14` → `src.shared_contracts.events.notification_events.NotificationSeverity`
- `src/robot_systems/glue/applications/dashboard/controller/glue_dashboard_controller.py:14` → `src.shared_contracts.events.notification_events.NotificationTopics`
- `src/robot_systems/glue/applications/dashboard/controller/glue_dashboard_controller.py:14` → `src.shared_contracts.events.notification_events.UserNotificationEvent`
- 52 additional import sites; use `--json` for the complete list.

### system:glue → engine

- `src/robot_systems/glue/application_wiring.py:3` → `src.engine.common_service_ids.CommonServiceID`
- `src/robot_systems/glue/application_wiring.py:5` → `src.engine.common_settings_ids.CommonSettingsID`
- `src/robot_systems/glue/application_wiring.py:6` → `src.engine.robot.configuration.robot_settings.SafetyLimits`
- `src/robot_systems/glue/application_wiring.py:16` → `src.engine.vision.capture_snapshot_service.CaptureSnapshotService`
- `src/robot_systems/glue/application_wiring.py:148` → `src.engine.robot.calibration.ros_tool_registry_client.RosToolRegistryClient`
- 173 additional import sites; use `--json` for the complete list.

### system:glue → shell

- `src/robot_systems/glue/applications/dashboard/config.py:3` → `pl_gui.dashboard.config.DashboardConfig`
- `src/robot_systems/glue/applications/dashboard/config.py:3` → `pl_gui.dashboard.config.ActionButtonConfig`
- `src/robot_systems/glue/applications/dashboard/config.py:3` → `pl_gui.dashboard.config.CardConfig`
- `src/robot_systems/glue/applications/dashboard/glue_dashboard.py:6` → `pl_gui.dashboard.config.CardConfig`
- `src/robot_systems/glue/applications/dashboard/ui/dashboard_preview_widget.py:18` → `pl_gui.dashboard.widgets.RobotTrajectoryWidget.TrajectoryManager`
- 32 additional import sites; use `--json` for the complete list.

### system:glue → system-runtime

- `src/robot_systems/glue/bootstrap_provider.py:14` → `src.robot_systems.robot_system_bootstrap_provider.RobotSystemBootstrapProvider`
- `src/robot_systems/glue/glue_robot_system.py:29` → `src.robot_systems.base_robot_system.BaseRobotSystem`

### system:paint → applications

- `src/robot_systems/paint/application_wiring.py:4` → `src.applications.workpiece_editor.editor_core.config.SegmentEditorConfig`
- `src/robot_systems/paint/application_wiring.py:249` → `src.applications.base.robot_jog_service_builder.build_robot_system_jog_service`
- `src/robot_systems/paint/application_wiring.py:250` → `src.applications.base.widget_application.WidgetApplication`
- `src/robot_systems/paint/application_wiring.py:274` → `src.applications.base.widget_application.WidgetApplication`
- `src/robot_systems/paint/application_wiring.py:305` → `src.applications.base.robot_jog_service_builder.build_robot_system_jog_service`
- 164 additional import sites; use `--json` for the complete list.

### system:paint → bootstrap

- `src/robot_systems/paint/run_servo_pickup_test.py:16` → `src.bootstrap.build_engine.EngineContext`
- `src/robot_systems/paint/run_servo_pickup_test.py:17` → `src.bootstrap.logging_config.setup_logging`

### system:paint → contracts

- `src/robot_systems/paint/application_wiring.py:1583` → `src.shared_contracts.events.process_events.ProcessState`
- `src/robot_systems/paint/applications/dashboard/controller/paint_dashboard_controller.py:24` → `src.shared_contracts.events.robot_events.RobotTopics`
- `src/robot_systems/paint/applications/dashboard/controller/paint_dashboard_controller.py:25` → `src.shared_contracts.events.shell_events.ShellTopics`
- `src/robot_systems/paint/applications/dashboard/controller/paint_dashboard_controller.py:26` → `src.shared_contracts.events.vision_events.CameraTopics`
- `src/robot_systems/paint/applications/dashboard/example_usage.py:20` → `src.shared_contracts.events.process_events.ProcessState`
- 27 additional import sites; use `--json` for the complete list.

### system:paint → engine

- `src/robot_systems/paint/application_wiring.py:5` → `src.engine.common_service_ids.CommonServiceID`
- `src/robot_systems/paint/application_wiring.py:6` → `src.engine.common_settings_ids.CommonSettingsID`
- `src/robot_systems/paint/application_wiring.py:284` → `src.engine.vision.capture_snapshot_service.CaptureSnapshotService`
- `src/robot_systems/paint/application_wiring.py:440` → `src.engine.robot.path_preparation.DefaultWorkpiecePathPreparationService`
- `src/robot_systems/paint/application_wiring.py:902` → `src.engine.auth.json_permissions_repository.JsonPermissionsRepository`
- 212 additional import sites; use `--json` for the complete list.

### system:paint → shell

- `src/robot_systems/paint/applications/dashboard/config.py:5` → `pl_gui.dashboard.config.ActionButtonConfig`
- `src/robot_systems/paint/applications/dashboard/config.py:5` → `pl_gui.dashboard.config.CardConfig`
- `src/robot_systems/paint/applications/dashboard/config.py:5` → `pl_gui.dashboard.config.DashboardConfig`
- `src/robot_systems/paint/applications/dashboard/ui/paint_card_factory.py:5` → `pl_gui.dashboard.config.CardConfig`
- `src/robot_systems/paint/applications/dashboard/ui/paint_controls_drawer.py:21` → `pl_gui.shell.ui.icon_loader.load_icon`
- 94 additional import sites; use `--json` for the complete list.

### system:paint → system-runtime

- `src/robot_systems/paint/bootstrap_provider.py:14` → `src.robot_systems.robot_system_bootstrap_provider.RobotSystemBootstrapProvider`
- `src/robot_systems/paint/paint_robot_system.py:31` → `src.robot_systems.base_robot_system.BaseRobotSystem`
- `src/robot_systems/paint/run_servo_pickup_test.py:28` → `src.robot_systems.system_builder.SystemBuilder`
- `src/robot_systems/paint/service_builders.py:15` → `src.robot_systems.default_service_builders.build_vision_service`

### system:paint_auto_dry → system-runtime

- `src/robot_systems/paint_auto_dry/bootstrap_provider.py:4` → `src.robot_systems.robot_system_bootstrap_provider.RobotSystemBootstrapProvider`

### system:paint_auto_dry → system:paint

- `src/robot_systems/paint_auto_dry/bootstrap_provider.py:2` → `src.robot_systems.paint.bootstrap_provider.PaintBootstrapProvider`
- `src/robot_systems/paint_auto_dry/bootstrap_provider.py:3` → `src.robot_systems.paint.paint_robot_system.AutomaticDryerPaintRobotSystem`
- `src/robot_systems/paint_auto_dry/bootstrap_provider.py:3` → `src.robot_systems.paint.paint_robot_system.with_paint_system_overrides`

### system:paint_tray_dry → system-runtime

- `src/robot_systems/paint_tray_dry/bootstrap_provider.py:4` → `src.robot_systems.robot_system_bootstrap_provider.RobotSystemBootstrapProvider`

### system:paint_tray_dry → system:paint

- `src/robot_systems/paint_tray_dry/bootstrap_provider.py:2` → `src.robot_systems.paint.bootstrap_provider.PaintBootstrapProvider`
- `src/robot_systems/paint_tray_dry/bootstrap_provider.py:3` → `src.robot_systems.paint.paint_robot_system.TrayDryerPaintRobotSystem`
- `src/robot_systems/paint_tray_dry/bootstrap_provider.py:3` → `src.robot_systems.paint.paint_robot_system.with_paint_system_overrides`

### system:twin_robot → applications

- `src/robot_systems/twin_robot/application_wiring.py:5` → `src.applications.base.widget_application.WidgetApplication`
- `src/robot_systems/twin_robot/application_wiring.py:17` → `src.applications.base.widget_application.WidgetApplication`
- `src/robot_systems/twin_robot/application_wiring.py:27` → `src.applications.network_settings.build_application.build_network_settings_application`
- `src/robot_systems/twin_robot/application_wiring.py:32` → `src.applications.software_update.build_application.build_software_update_application`
- `src/robot_systems/twin_robot/applications/choreography_setup/choreography_setup_factory.py:3` → `src.applications.base.application_factory.ApplicationFactory`
- 25 additional import sites; use `--json` for the complete list.

### system:twin_robot → contracts

- `src/robot_systems/twin_robot/twin_robot_system.py:14` → `src.shared_contracts.declarations.ApplicationSpec`
- `src/robot_systems/twin_robot/twin_robot_system.py:14` → `src.shared_contracts.declarations.FolderSpec`
- `src/robot_systems/twin_robot/twin_robot_system.py:14` → `src.shared_contracts.declarations.RolePolicy`
- `src/robot_systems/twin_robot/twin_robot_system.py:14` → `src.shared_contracts.declarations.ShellSetup`
- `src/robot_systems/twin_robot/twin_robot_system.py:14` → `src.shared_contracts.declarations.SystemMetadata`

### system:twin_robot → engine

- `src/robot_systems/twin_robot/bootstrap_provider.py:7` → `src.engine.auth.authentication_service.AuthenticationService`
- `src/robot_systems/twin_robot/bootstrap_provider.py:8` → `src.engine.auth.authorization_service.AuthorizationService`
- `src/robot_systems/twin_robot/bootstrap_provider.py:9` → `src.engine.auth.json_permissions_repository.JsonPermissionsRepository`
- `src/robot_systems/twin_robot/bootstrap_provider.py:10` → `src.engine.common_service_ids.CommonServiceID`
- `src/robot_systems/twin_robot/bootstrap_provider.py:11` → `src.engine.robot.drivers.ros2_robot.Ros2Robot`

### system:twin_robot → shell

- `src/robot_systems/twin_robot/applications/choreography_setup/view/choreography_setup_view.py:19` → `pl_gui.settings.settings_view.styles.ACTION_BTN_STYLE`
- `src/robot_systems/twin_robot/applications/choreography_setup/view/choreography_setup_view.py:19` → `pl_gui.settings.settings_view.styles.BG_COLOR`
- `src/robot_systems/twin_robot/applications/choreography_setup/view/choreography_setup_view.py:19` → `pl_gui.settings.settings_view.styles.GHOST_BTN_STYLE`
- `src/robot_systems/twin_robot/applications/choreography_setup/view/choreography_setup_view.py:19` → `pl_gui.settings.settings_view.styles.GROUP_STYLE`
- `src/robot_systems/twin_robot/applications/choreography_setup/view/choreography_setup_view.py:19` → `pl_gui.settings.settings_view.styles.LABEL_STYLE`
- 6 additional import sites; use `--json` for the complete list.

### system:twin_robot → system-runtime

- `src/robot_systems/twin_robot/bootstrap_provider.py:14` → `src.robot_systems.robot_system_bootstrap_provider.RobotSystemBootstrapProvider`
- `src/robot_systems/twin_robot/twin_robot_system.py:5` → `src.robot_systems.base_robot_system.BaseRobotSystem`

### system:welding → applications

- `src/robot_systems/welding/application_wiring.py:7` → `src.applications.workpiece_editor.editor_core.config.SegmentEditorConfig`
- `src/robot_systems/welding/application_wiring.py:14` → `src.applications.base.widget_application.WidgetApplication`
- `src/robot_systems/welding/application_wiring.py:35` → `src.applications.base.widget_application.WidgetApplication`
- `src/robot_systems/welding/application_wiring.py:36` → `src.applications.base.robot_jog_service_builder.build_robot_system_jog_service`
- `src/robot_systems/welding/application_wiring.py:38` → `src.applications.workpiece_editor.service.workpiece_editor_service.WorkpieceEditorServices`
- 65 additional import sites; use `--json` for the complete list.

### system:welding → contracts

- `src/robot_systems/welding/application_wiring.py:505` → `src.shared_contracts.events.process_events.ProcessState`
- `src/robot_systems/welding/applications/dashboard/service/welding_dashboard_service.py:3` → `src.shared_contracts.events.process_events.ProcessState`
- `src/robot_systems/welding/calibration/coordinator.py:9` → `src.shared_contracts.events.process_events.ProcessBusyEvent`
- `src/robot_systems/welding/calibration/coordinator.py:9` → `src.shared_contracts.events.process_events.ProcessState`
- `src/robot_systems/welding/calibration/coordinator.py:9` → `src.shared_contracts.events.process_events.ProcessTopics`
- 13 additional import sites; use `--json` for the complete list.

### system:welding → engine

- `src/robot_systems/welding/application_wiring.py:5` → `src.engine.common_service_ids.CommonServiceID`
- `src/robot_systems/welding/application_wiring.py:6` → `src.engine.common_settings_ids.CommonSettingsID`
- `src/robot_systems/welding/application_wiring.py:26` → `src.engine.vision.capture_snapshot_service.CaptureSnapshotService`
- `src/robot_systems/welding/application_wiring.py:37` → `src.engine.robot.path_preparation.DefaultWorkpiecePathPreparationService`
- `src/robot_systems/welding/application_wiring.py:144` → `src.engine.auth.json_permissions_repository.JsonPermissionsRepository`
- 68 additional import sites; use `--json` for the complete list.

### system:welding → shell

- `src/robot_systems/welding/applications/dashboard/config.py:5` → `pl_gui.dashboard.config.ActionButtonConfig`
- `src/robot_systems/welding/applications/dashboard/config.py:5` → `pl_gui.dashboard.config.CardConfig`
- `src/robot_systems/welding/applications/dashboard/config.py:5` → `pl_gui.dashboard.config.DashboardConfig`
- `src/robot_systems/welding/applications/dashboard/ui/welding_card_factory.py:3` → `pl_gui.dashboard.config.CardConfig`
- `src/robot_systems/welding/applications/dashboard/view/welding_dashboard_view.py:7` → `pl_gui.dashboard.DashboardWidget.DashboardWidget`

### system:welding → system-runtime

- `src/robot_systems/welding/bootstrap_provider.py:14` → `src.robot_systems.robot_system_bootstrap_provider.RobotSystemBootstrapProvider`
- `src/robot_systems/welding/welding_robot_system.py:24` → `src.robot_systems.base_robot_system.BaseRobotSystem`

### system:welding → system:glue

- `src/robot_systems/welding/processes/robot_calibration_process.py:5` → `src.robot_systems.glue.component_ids.ProcessID`
