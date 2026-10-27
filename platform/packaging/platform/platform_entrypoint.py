"""Standalone entry point bound to one robot-system/profile release target."""
import os
import sys
import json
from pathlib import Path

from src.engine.updates.config import UpdateConfig, default_config_path, default_install_root
from src.engine.updates.files import lock


def main():
    if "--set-kiosk-password" in sys.argv:
        from src.bootstrap.kiosk_password import main as set_kiosk_password
        set_kiosk_password(sys.argv[sys.argv.index("--set-kiosk-password") + 1:])
        return
    resource_root = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[2]))
    target = json.loads((resource_root / "config/release-target.json").read_text())
    os.environ["ROBOT_PLATFORM_PRODUCT"] = target["product"]
    if "--self-test" in sys.argv:
        self_test()
        return
    config_path = default_config_path()
    root = (UpdateConfig.load(config_path).install_root if config_path.exists()
            else default_install_root(target["product"]))
    if config_path.exists() and UpdateConfig.load(config_path).product != target["product"]:
        raise RuntimeError("Update configuration belongs to another robot system/profile")
    os.environ.setdefault("ROBOT_PLATFORM_DATA_ROOT", str(root / "data"))
    # Also guard direct executable launches, not just the installed launcher.
    with lock(root / "update-state/runtime.lock", shared=True):
        if (root / "update-state/transaction.json").exists():
            raise RuntimeError("Interrupted update: use the installed launcher to recover first")
        from src.engine.updates.factory_defaults import seed_factory_defaults
        seed_factory_defaults(resource_root, Path(os.environ["ROBOT_PLATFORM_DATA_ROOT"]), target)
        from src.bootstrap.run_main import main as run_platform
        run_platform()


def check_vision_application_widgets(app):
    """Construct lazy vision screens with stubs, without cameras or robot I/O."""
    from src.engine.core.messaging_service import MessagingService
    from src.applications.calibration.calibration_factory import CalibrationFactory
    from src.applications.calibration.service.stub_calibration_service import StubCalibrationService
    from src.applications.camera_settings.camera_settings_factory import CameraSettingsFactory
    from src.applications.camera_settings.service.stub_camera_settings_service import StubCameraSettingsService
    from src.applications.work_area_settings.work_area_settings_factory import WorkAreaSettingsFactory
    from src.applications.work_area_settings.service.stub_work_area_settings_service import StubWorkAreaSettingsService
    from src.shared_contracts.declarations import WorkAreaDefinition
    from pl_gui.settings.settings_view.styles import PRIMARY

    messaging = MessagingService()
    areas = [WorkAreaDefinition(id="magazine", label="Magazine", color=PRIMARY)]
    for factory, service, options in (
        (WorkAreaSettingsFactory(areas), StubWorkAreaSettingsService(), {}),
        (CameraSettingsFactory(), StubCameraSettingsService(), {"show_camera_devices": True}),
        (CalibrationFactory(areas), StubCalibrationService(), {}),
    ):
        view = factory.build(service, messaging=messaging, **options)
        try:
            view.resize(1280, 800)
            view.grab()
            app.processEvents()
        finally:
            view.clean_up()
            view.deleteLater()
    app.processEvents()


def self_test():
    """Verify frozen imports, startup resources and Qt without touching hardware."""
    from PyQt6.QtWidgets import QApplication
    from src.bootstrap.startup_config import load_startup_config, load_bootstrap_provider
    from src.applications.software_update.software_update_factory import SoftwareUpdateFactory
    from src.applications.software_update.service.stub_software_update_service import StubSoftwareUpdateService
    from src.applications.base.widgets.fluid_progress import create_fluid_progress
    from src.engine.localization.localization_service import LocalizationService

    from src.bootstrap.run_main import main as _run_platform
    config = load_startup_config()
    load_bootstrap_provider(config)
    from src.engine.updates.factory_defaults import load_factory_defaults
    resource_root = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[2]))
    target = json.loads((resource_root / "config/release-target.json").read_text())
    load_factory_defaults(resource_root, target)
    app = QApplication([])
    check_vision_application_widgets(app)
    if "paint" in target["packages"]:
        from src.robot_systems.paint.applications.dashboard.ui.paint_card_factory import _PAINT_ICON_PATH
        from PyQt6.QtSvg import QSvgRenderer
        from PyQt6.QtGui import QIcon
        if not QSvgRenderer(_PAINT_ICON_PATH).isValid() or QIcon(_PAINT_ICON_PATH).pixmap(48, 48).isNull():
            raise RuntimeError(f"Bundled paint process status icon could not be loaded: {_PAINT_ICON_PATH}")
    # Exercise all selectable progress variants so packaging cannot silently
    # omit a style that is not currently selected by the update view.
    for style in ("ink", "plume", "vessel"):
        progress = create_fluid_progress(style)
        progress.resize(360, progress.height())
        progress.set_waiting(True)
        progress.set_running(True)
        progress.grab()
        progress.deleteLater()
    from PyQt6.QtGui import QPixmap
    from src.applications.login.view.login_view import _LOGO_PATH, _MACHINE_IMAGE_PATH
    for asset in (_LOGO_PATH, _MACHINE_IMAGE_PATH):
        if QPixmap(asset).isNull():
            raise RuntimeError(f"Bundled login image could not be loaded: {asset}")
    fluid_assets = resource_root / "src/applications/login/view/fluid_assets"
    for asset in (fluid_assets / "index.html", fluid_assets / "fluid.js"):
        if not asset.is_file() or asset.stat().st_size == 0:
            raise RuntimeError(f"Bundled login fluid asset is missing: {asset}")
    import tempfile
    temporary = tempfile.TemporaryDirectory()
    resource_root = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[2]))
    catalog = resource_root / "src/applications/software_update/localization"
    localization = LocalizationService(str(catalog), state_file=str(Path(temporary.name) / "language.json"))
    localization.set_language("bg")
    view = SoftwareUpdateFactory().build(StubSoftwareUpdateService())
    if type(view._progress).__name__ != "PlumeLine":
        raise RuntimeError("Bundled update progress widget selection is incorrect")
    if view._title.text() != "Актуализация на софтуера":
        raise RuntimeError("Bundled Bulgarian update catalog missing")
    localization.set_language("en")
    app.processEvents()
    if view._title.text() != "Software Update":
        raise RuntimeError("Bundled update retranslation failed")
    # Exercise the frozen button, background worker and GUI result callback.
    # Capture the result instead of opening a modal dialog during build checks.
    import time
    check_results = []
    def record_check_result(error=False):
        check_results.append((error, view._status.text()))
    view.show_check_result = record_check_result
    view._check.click()
    deadline = time.monotonic() + 5
    while view._controller._busy and time.monotonic() < deadline:
        app.processEvents()
        time.sleep(0.005)
    if check_results != [(False, "Version 1.1.0 is available")]:
        raise RuntimeError("Frozen update check did not deliver its GUI result")
    view.clean_up()
    # Complete queued worker/widget deletion before destroying QApplication.
    # A hardware-free check exits much faster than the normal GUI event loop.
    from PyQt6.QtCore import QCoreApplication, QEvent
    view.deleteLater()
    app.processEvents()
    QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    app.removeTranslator(localization._current_translator)
    temporary.cleanup()
    print("Platform self-test passed (no hardware/backend started)")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        # Keep hardware-free build checks noninteractive.
        if "--self-test" in sys.argv:
            raise
        from src.bootstrap.startup_error import report_startup_error
        root = default_install_root(os.environ.get("ROBOT_PLATFORM_PRODUCT", "paint-robot"))
        try:
            config_path = default_config_path()
            if config_path.exists():
                root = UpdateConfig.load(config_path).install_root
        except Exception:
            pass
        report_startup_error(error, root / "update-state")
        sys.exit(1)
