import json
import sys
import types
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from src.bootstrap.startup_config import (
    RosBackendConfig,
    StartupConfig,
    UiStartupConfig,
    load_bootstrap_provider,
    load_startup_config,
    load_robot_system_config,
    build_configured_robot,
)
from src.robot_systems.robot_system_bootstrap_provider import (
    RobotSystemBootstrapProvider,
)


class _TestProvider(RobotSystemBootstrapProvider):
    @property
    def system_class(self):
        return object

    def build_robot(self):
        return object()

    def build_login_view(self, robot_system, messaging_service):
        return object()

    def build_authorization_service(self, robot_system):
        return object()


class TestStartupConfig(unittest.TestCase):
    @staticmethod
    def system_config():
        return dict(robot_driver="zeroerr", backend="zeroerr", backend_profile="paint_short_links",
                    release_version="1.0.0", platform_version="1.0.0", backend_version="1.0.0")

    def test_robot_driver_mismatch_fails(self):
        selected = {**self.system_config(), "robot_driver": "fairino"}
        with self.assertRaisesRegex(RuntimeError, "robot_driver must match backend"):
            load_robot_system_config({"robot_systems": {"paint": selected}}, "paint")

    def test_configured_robot_uses_bridge_without_provider_fallback(self):
        config = StartupConfig(robot_system="paint", supported_robot_systems=("paint",), system_config=self.system_config())
        with patch("src.engine.robot.drivers.ros2_robot.Ros2Robot") as robot:
            result = build_configured_robot(config)
        robot.assert_called_once_with(server_url="http://localhost:5000")
        self.assertIs(result, robot.return_value)

    def test_missing_selected_system_fails(self):
        for systems in (None, {}, {"glue": self.system_config()}):
            with self.subTest(systems=systems), TemporaryDirectory() as directory:
                path = Path(directory) / "platform.json"
                path.write_text(json.dumps(dict(robot_system="paint", supported_robot_systems=["paint"], robot_systems=systems)))
                with self.assertRaisesRegex(RuntimeError, "Missing configuration: robot_systems.paint"):
                    load_startup_config(path)

    def test_incomplete_selected_system_fails(self):
        for key in self.system_config():
            selected = self.system_config()
            del selected[key]
            with self.subTest(key=key), self.assertRaisesRegex(RuntimeError, key):
                load_robot_system_config({"robot_systems": {"paint": selected}}, "paint")

    def test_loads_selected_robot_system(self):
        with TemporaryDirectory() as tmp_dir:
            config_path = Path(tmp_dir) / "platform.json"
            config_path.write_text(
                json.dumps(
                    {
                        "robot_system": "paint",
                        "supported_robot_systems": ["glue", "paint", "welding"],
                        "robot_systems": {"paint": self.system_config()},
                    }
                ),
                encoding="utf-8",
            )

            config = load_startup_config(config_path)

        self.assertEqual(
            config,
            StartupConfig(
                robot_system="paint",
                supported_robot_systems=("glue", "paint", "welding"),
                system_config=self.system_config(),
            ),
        )

    def test_loads_ros_backend_config(self):
        with TemporaryDirectory() as tmp_dir:
            config_path = Path(tmp_dir) / "platform.json"
            config_path.write_text(
                json.dumps(
                    {
                        "robot_system": "paint",
                        "supported_robot_systems": ["paint"],
                        "robot_systems": {"paint": self.system_config()},
                        "ros_backend": {
                            "auto_launch": False,
                            "auto_stop": False,
                            "launch_script": "~/ros2_ws/launch_zeroerr.sh",
                            "stop_script": "~/ros2_ws/stop_zeroerr.sh",
                            "startup_delay_s": 0,
                            "log_file": "/tmp/backend.log",
                            "status_urls": ["http://localhost:5000/health"],
                            "status_timeout_s": 0.5,
                        },
                    }
                ),
                encoding="utf-8",
            )

            config = load_startup_config(config_path)

        self.assertEqual(
            config.ros_backend,
            RosBackendConfig(
                auto_launch=False,
                auto_stop=False,
                launch_script="~/ros2_ws/launch_zeroerr.sh",
                stop_script="~/ros2_ws/stop_zeroerr.sh",
                startup_delay_s=0.0,
                log_file="/tmp/backend.log",
                status_urls=("http://localhost:5000/health",),
                status_timeout_s=0.5,
            ),
        )

    def test_loads_ui_startup_config(self):
        with TemporaryDirectory() as tmp_dir:
            config_path = Path(tmp_dir) / "platform.json"
            config_path.write_text(
                json.dumps(
                    {
                        "robot_system": "paint",
                        "supported_robot_systems": ["paint"],
                        "robot_systems": {"paint": self.system_config()},
                        "ui": {
                            "dev_skip_login": True,
                            "skip_splash": True,
                            "show_account_button_when_dev_skip_login": True,
                            "show_power_off_button": True,
                            "fullscreen": False,
                            "window_width": 1024,
                            "window_height": 768,
                        },
                    }
                ),
                encoding="utf-8",
            )

            config = load_startup_config(config_path)

        self.assertEqual(
            config.ui,
            UiStartupConfig(
                dev_skip_login=True,
                skip_splash=True,
                show_account_button_when_dev_skip_login=True,
                show_power_off_button=True,
                fullscreen=False,
                window_width=1024,
                window_height=768,
            ),
        )

    def test_rejects_invalid_ui_window_size(self):
        with TemporaryDirectory() as tmp_dir:
            config_path = Path(tmp_dir) / "platform.json"
            config_path.write_text(
                json.dumps(
                    {
                        "robot_system": "paint",
                        "supported_robot_systems": ["paint"],
                        "robot_systems": {"paint": self.system_config()},
                        "ui": {"window_width": 0},
                    }
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(RuntimeError, "ui.window_width"):
                load_startup_config(config_path)

    def test_rejects_invalid_ui_bool(self):
        with TemporaryDirectory() as tmp_dir:
            config_path = Path(tmp_dir) / "platform.json"
            config_path.write_text(
                json.dumps(
                    {
                        "robot_system": "paint",
                        "supported_robot_systems": ["paint"],
                        "robot_systems": {"paint": self.system_config()},
                        "ui": {"dev_skip_login": "false"},
                    }
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(RuntimeError, "ui.dev_skip_login"):
                load_startup_config(config_path)

    def test_rejects_invalid_ros_backend_bool(self):
        with TemporaryDirectory() as tmp_dir:
            config_path = Path(tmp_dir) / "platform.json"
            config_path.write_text(
                json.dumps(
                    {
                        "robot_system": "paint",
                        "supported_robot_systems": ["paint"],
                        "robot_systems": {"paint": self.system_config()},
                        "ros_backend": {"auto_launch": "false"},
                    }
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(RuntimeError, "ros_backend.auto_launch"):
                load_startup_config(config_path)

    def test_rejects_invalid_ros_backend_path(self):
        with TemporaryDirectory() as tmp_dir:
            config_path = Path(tmp_dir) / "platform.json"
            config_path.write_text(
                json.dumps(
                    {
                        "robot_system": "paint",
                        "supported_robot_systems": ["paint"],
                        "robot_systems": {"paint": self.system_config()},
                        "ros_backend": {"launch_script": ""},
                    }
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(RuntimeError, "ros_backend.launch_script"):
                load_startup_config(config_path)

    def test_rejects_dotted_module_path(self):
        with TemporaryDirectory() as tmp_dir:
            config_path = Path(tmp_dir) / "platform.json"
            config_path.write_text(
                json.dumps(
                    {
                        "robot_system": "src.robot_systems.paint",
                        "supported_robot_systems": ["paint"],
                        "robot_systems": {"paint": self.system_config()},
                    }
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(RuntimeError, "lowercase identifier"):
                load_startup_config(config_path)

    def test_loads_provider_factory_by_convention(self):
        module_name = "src.robot_systems.example.bootstrap_provider"
        module = types.ModuleType(module_name)
        module.create_bootstrap_provider = _TestProvider

        with patch.dict(sys.modules, {module_name: module}):
            provider = load_bootstrap_provider(
                StartupConfig(
                    robot_system="example",
                    supported_robot_systems=("example",),
                )
            )

        self.assertIsInstance(provider, _TestProvider)

    def test_loads_paint_auto_dry_as_a_robot_system(self):
        provider = load_bootstrap_provider(
            StartupConfig(
                robot_system="paint_auto_dry",
                supported_robot_systems=("paint_auto_dry", "paint_tray_dry"),
            )
        )

        self.assertEqual(provider.system_class.__name__, "AutomaticDryerPaintRobotSystem")


    def test_reports_missing_robot_system(self):
        with self.assertRaisesRegex(RuntimeError, "is not installed"):
            load_bootstrap_provider(
                StartupConfig(
                    robot_system="system_that_does_not_exist",
                    supported_robot_systems=("system_that_does_not_exist",),
                )
            )

    def test_rejects_selected_system_not_in_supported_list(self):
        with TemporaryDirectory() as tmp_dir:
            config_path = Path(tmp_dir) / "platform.json"
            config_path.write_text(
                json.dumps(
                    {
                        "robot_system": "paint",
                        "supported_robot_systems": ["glue", "welding"],
                    }
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(RuntimeError, "is not listed"):
                load_startup_config(config_path)


if __name__ == "__main__":
    unittest.main()
