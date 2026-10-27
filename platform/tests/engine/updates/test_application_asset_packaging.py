import importlib.util
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location("asset_packaging_targets", ROOT / "packaging/platform/targets.py")
targets = importlib.util.module_from_spec(spec)
spec.loader.exec_module(targets)


class TestApplicationAssets(unittest.TestCase):
    def test_selected_profile_includes_base_dashboard_assets_without_other_systems_or_storage(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            paths = (
                "src/robot_systems/paint/applications/dashboard/assets/paint_process.svg",
                "src/robot_systems/glue/applications/dashboard/assets/other.svg",
                "src/robot_systems/paint/storage/workpieces/assets/private.svg",
            )
            for name in paths:
                path = root / name
                path.parent.mkdir(parents=True)
                path.write_text("<svg/>")
            data = targets.application_asset_data({"packages": ["paint", "paint_tray_dry"]}, root)
            self.assertEqual([(str(root / "src/robot_systems/paint/applications/dashboard/assets"),
                               "src/robot_systems/paint/applications/dashboard/assets")], data)

    def test_real_paint_process_svg_is_collected_and_renders(self):
        import os
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtSvg import QSvgRenderer
        from PyQt6.QtGui import QIcon
        app = QApplication.instance() or QApplication([])
        data = targets.application_asset_data(targets.load_target("paint_tray_dry"))
        relative = "src/robot_systems/paint/applications/dashboard/assets"
        source = next(Path(source) for source, destination in data if destination == relative)
        icon = source / "paint_process.svg"
        self.assertTrue(QSvgRenderer(str(icon)).isValid())
        self.assertFalse(QIcon(str(icon)).pixmap(48, 48).isNull())
