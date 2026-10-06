# `src/applications/` — Application System

The `applications` package contains all pluggable GUI features of the platform. Each application is a self-contained MVC unit exposed to the shell via `ApplicationSpec` entries on the robot system. Applications are the only place in the codebase where the GUI and platform services meet.

---

## Architecture Overview

```
Bootstrap
  └─ visible ApplicationSpec metadata
       └─ shell descriptors only             ← folders/icons available at login

First app open
  └─ ApplicationSpec.factory(robot_system)
       └─ IApplication
            ├─ register(messaging_service)    ← receive broker reference on first open
            └─ create_widget()                ← builds widget for the shell
                    └─ ApplicationFactory.build(service)
                         ├─ IApplicationModel      ← state + I/O, no Qt
                         ├─ IApplicationView       ← pure Qt, no logic
                         └─ IApplicationController ← wires M ↔ V, broker subscriptions
```

Data flows in one direction only:

```
User action  →  View signal  →  Controller  →  Model  →  Service
Live data    →  Broker sub   →  Bridge      →  View setter
```

---

## Packages

| Package | Description |
|---------|-------------|
| `base/` | Abstract base classes plus shared UI infrastructure such as `KeyboardSettingsView`, `CollapsibleSettingsView`, virtual keyboard widgets, dialogs, and `app_styles.py` |
| `APPLICATION_BLUEPRINT/` | Copy-paste template with full guide in `APPLICATION_GUIDE.MD` |
| `modbus_settings/` | Modbus serial port configuration — port detection + connection test |
| `glue_cell_settings/` | Weight cell configuration + live readings per cell |
| `robot_settings/` | Robot kinematics, safety limits, calibration, and movement group editor |
| `camera_settings/` | Camera resolution, brightness, thresholds, and work area configuration |
| `calibration/` | Robot-to-camera calibration workflow (ArUco marker capture + solve) |
| `broker_debug/` | Live message broker inspector — spy on topics, publish test messages |
| `workpiece_editor/` | Contour-based workpiece path editor with vision overlay |
| `workpiece_library/` | Workpiece catalogue — browse, edit metadata, delete entries |
| `tool_settings/` | Tool changer configuration (grip offsets, tool type selection) |
| `user_management/` | User account management backed by a CSV repository |
| `contour_matching_tester/` | Offline workpiece-to-contour match testing tool |
| `pick_target/` | Manual vision-to-robot target probe for homography, pickup-plane mapping, and TCP-offset debugging |
| `login/` | Modal login dialog — password auth, QR code scanning, and first-run admin setup |
| `device_control/` | Manual on/off control panel for laser, vacuum pump, motors, and generator |
| `height_measuring/` | Laser height sensor calibration, detection tuning, and single-shot verification |
| `aruco_z_probe/` | ArUco marker Z-sweep tool for measuring camera-Z displacement relationships |
| `pick_and_place_visualizer/` | Live placement plane visualizer, step-mode debugger, and log panel for pick-and-place |
| `work_area_settings/` | Shared work-area and detection ROI editor (separate from camera settings) |
| `calibration_settings/` | Shared calibration configuration |
| `ethercat_diagnostics/` | Master/slave diagnostics and optional error reset |
| `hand_eye_calibration/` | Robot/chessboard pose capture and camera-to-flange solve |
| `intrinsic_calibration_capture/` | Automated chessboard/ChArUco calibration acquisition |
| `shaft_alignment/` | Camera/marker reference capture and alignment comparison |
| `network_settings/` | Host network configuration |
| `remote_support/` | Restricted support-service controls |
| `software_update/` | Signed product update UI |

Robot-system-specific dashboards may expose process-owned quick settings while retaining the same MVC boundary. The paint dashboard's unmatched controls use a one/two-pass selector and pass tabs. Pass two defaults to an explicit “Use Pass 1 settings” mode; disabling inheritance enables independent velocity, acceleration, and press-offset fields. The service validates/saves the complete configuration; whether pass settings may change during a run depends on `allow_running_paint_settings_updates`. When enabled, the active workpiece retains its snapshot and the next cycle captures the update.

---

## Lifecycle

```
Bootstrap startup:
  for each visible ApplicationSpec in robot_system.shell.applications:
    application_loader stores shell descriptor metadata
    application_loader stores deferred builder only

User opens folder:
  application = spec.factory(robot_system)            ← first-open only
  application.register(messaging_service)
  application.create_widget()                      ← instantiates view + controller
    └─ ApplicationFactory.build(service)
         ├─ _create_model(service)
         ├─ _create_view()
         ├─ _create_controller(model, view)
         ├─ controller.load()                 ← populate view from model
         └─ view._controller = controller     ← GC ownership fix
```

---

## Wiring a Application

In the robot system, add a module-level factory function and a `ApplicationSpec`:

```python
def _build_my_application(robot_system):
    from src.applications.base.widget_application import WidgetApplication
    from src.applications.my_application.my_application_factory import MyApplicationFactory
    from src.applications.my_application.service.my_application_service import MyApplicationService

    service = MyApplicationService(settings_service=robot_system._settings_service)
    factory = MyApplicationFactory()
    return WidgetApplication(widget_factory=lambda _ms: factory.build(service))
    # If the application needs live broker data:
    # return WidgetApplication(widget_factory=lambda ms: factory.build(service, ms))


class YourRobotApp(BaseRobotSystem):
    shell = ShellSetup(
        applications=[
            ApplicationSpec(name="MyApplication", folder_id=2, icon="fa5s.cog", factory=_build_my_application),
        ],
    )
```

---

## Design Notes

- **Lazy application creation**: visible apps contribute only shell metadata at startup. `spec.factory(robot_system)`, `register(...)`, and `create_widget()` all happen on first open.
- **Shell stays UI-only**: the shell receives descriptors plus a `widget_factory(app_name)` callback; it does not know about `robot_system`, `ApplicationSpec`, or application lifecycle.
- **GC safety**: `ApplicationFactory.build()` assigns `view._controller = controller`, keeping the controller alive as long as the view exists. Never write this line yourself.
- **Layer separation**: Each layer has strict import rules — see `APPLICATION_BLUEPRINT/APPLICATION_GUIDE.MD`.
- **Cross-thread safety**: When broker callbacks arrive from background threads (e.g., weight readings), controllers use a `_Bridge(QObject)` with `pyqtSignal` attributes to marshal data back to the Qt main thread safely. See `glue_cell_settings/controller/`.
- **Blocking service calls**: When a service call may block the GUI (e.g., serial port detection), controllers dispatch a `QThread + _Worker` pair and track them in `_active: List[Tuple[QThread, _Worker]]`. See `modbus_settings/controller/`.
- **Localization**: Views should prefer `self.tr(...)` for static strings and implement `retranslateUi()` when they own localizable widget text. `IApplicationView` now handles `LanguageChange` by default and emits `language_changed` for controllers that need to refresh dynamic text via `QCoreApplication.translate(...)`.
- **Shared view styling**: Use `pl_gui.settings.settings_view.styles` for titles, backgrounds, cards and action buttons. `src/applications/base/app_styles.py` provides additional shared application styling; avoid duplicating common patterns locally.
- **Virtual keyboard**: Direct numeric fields use `KeyboardNumberField`, text fields use `KeyboardLineEdit`; schema tabs use keyboard settings handlers, and existing factory seams use `VirtualKeyboardWidgetFactory()`. Spin-box subclasses are reserved for contracts requiring an actual Qt spin box. The startup flag controls the shared keyboard; dialogs must restore spacing on hide.

<!-- source-navigation:start -->
## Source navigation

[Module reference](MODULES.md) — signatures, fields, imports and source links for every Python file in this directory.

[Resource reference](RESOURCES.md) — non-Python files and their formats; values remain in the owning storage/source files.

| Source subdirectory | Guide |
|---|---|
| `APPLICATION_BLUEPRINT/` | [APPLICATION_BLUEPRINT](APPLICATION_BLUEPRINT/README.md) |
| `aruco_z_probe/` | [aruco_z_probe](aruco_z_probe/README.md) |
| `base/` | [base](base/README.md) |
| `broker_debug/` | [broker_debug](broker_debug/README.md) |
| `calibration/` | [calibration](calibration/README.md) |
| `calibration_settings/` | [calibration_settings](calibration_settings/README.md) |
| `camera_settings/` | [camera_settings](camera_settings/README.md) |
| `contour_matching_tester/` | [contour_matching_tester](contour_matching_tester/README.md) |
| `device_control/` | [device_control](device_control/README.md) |
| `ethercat_diagnostics/` | [ethercat_diagnostics](ethercat_diagnostics/README.md) |
| `glue_cell_settings/` | [glue_cell_settings](glue_cell_settings/README.md) |
| `hand_eye_calibration/` | [hand_eye_calibration](hand_eye_calibration/README.md) |
| `height_measuring/` | [height_measuring](height_measuring/README.md) |
| `intrinsic_calibration_capture/` | [intrinsic_calibration_capture](intrinsic_calibration_capture/README.md) |
| `localization/` | [localization](localization/README.md) |
| `login/` | [login](login/README.md) |
| `modbus_settings/` | [modbus_settings](modbus_settings/README.md) |
| `network_settings/` | [network_settings](network_settings/README.md) |
| `pick_and_place_visualizer/` | [pick_and_place_visualizer](pick_and_place_visualizer/README.md) |
| `pick_target/` | [pick_target](pick_target/README.md) |
| `remote_support/` | [remote_support](remote_support/README.md) |
| `robot_settings/` | [robot_settings](robot_settings/README.md) |
| `shaft_alignment/` | [shaft_alignment](shaft_alignment/README.md) |
| `software_update/` | [software_update](software_update/README.md) |
| `tool_settings/` | [tool_settings](tool_settings/README.md) |
| `user_management/` | [user_management](user_management/README.md) |
| `work_area_settings/` | [work_area_settings](work_area_settings/README.md) |
| `workpiece_editor/` | [workpiece_editor](workpiece_editor/README.md) |
| `workpiece_library/` | [workpiece_library](workpiece_library/README.md) |

[Complete source index](../SOURCE_INDEX.md).
<!-- source-navigation:end -->
