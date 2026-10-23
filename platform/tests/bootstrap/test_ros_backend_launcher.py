from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from src.bootstrap.ros_backend_launcher import (
    RosBackendLauncher,
    _clean_ros_process_env,
    build_ros_backend_launcher_from_env,
)
from src.bootstrap.startup_config import RosBackendConfig


class TestRosBackendLauncher(unittest.TestCase):
    def test_backend_does_not_inherit_platform_qt_plugins(self) -> None:
        inherited = {
            "QT_PLUGIN_PATH": "/tmp/app/.venv/PyQt6/plugins",
            "QT_QPA_PLATFORM_PLUGIN_PATH": "/tmp/app/.venv/cv2/qt/plugins",
            "QT_QPA_FONTDIR": "/tmp/app/.venv/cv2/qt/fonts",
            "DISPLAY": ":1",
            "XAUTHORITY": "/run/user/1000/gdm/Xauthority",
            "ROS_DOMAIN_ID": "42",
            "LD_LIBRARY_PATH": "/opt/ros/jazzy/lib",
        }
        with patch.dict(os.environ, inherited, clear=True):
            env = _clean_ros_process_env()
            for name in ("QT_PLUGIN_PATH", "QT_QPA_PLATFORM_PLUGIN_PATH", "QT_QPA_FONTDIR"):
                self.assertNotIn(name, env)
                self.assertEqual(os.environ[name], inherited[name])
        for name in ("DISPLAY", "XAUTHORITY", "ROS_DOMAIN_ID", "LD_LIBRARY_PATH"):
            self.assertEqual(env[name], inherited[name])

    def _script(self, directory: Path, name: str) -> Path:
        path = directory / name
        path.write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")
        path.chmod(0o755)
        return path

    def test_start_launches_script_with_delay(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            launch = self._script(root, "launch.sh")
            stop = self._script(root, "stop.sh")
            process = MagicMock()
            process.poll.return_value = None

            with (
                patch("src.bootstrap.ros_backend_launcher.urllib.request.urlopen", side_effect=OSError("down")),
                patch("src.bootstrap.ros_backend_launcher.subprocess.Popen", return_value=process) as popen,
                patch("src.bootstrap.ros_backend_launcher.time.sleep") as sleep,
            ):
                launcher = RosBackendLauncher(launch, stop, startup_delay_s=1.5, log_file=root / "backend.log")
                launcher.start()
                launcher._close_log_handle()

            popen.assert_called_once_with(
                [str(launch)],
                cwd=str(root),
                start_new_session=True,
                env=unittest.mock.ANY,
                stdout=unittest.mock.ANY,
                stderr=subprocess.STDOUT,
            )
            env = popen.call_args.kwargs["env"]
            self.assertNotIn("VIRTUAL_ENV", env)
            self.assertNotIn("PYTHONPATH", env)
            self.assertEqual(Path(popen.call_args.kwargs["stdout"].name), root / "backend.log")
            sleep.assert_called_once_with(1.5)

    def test_stop_runs_stop_script_and_waits_for_launch_wrapper(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            launch = self._script(root, "launch.sh")
            stop = self._script(root, "stop.sh")
            process = MagicMock()
            process.poll.return_value = None

            with (
                patch("src.bootstrap.ros_backend_launcher.urllib.request.urlopen", side_effect=OSError("down")),
                patch("src.bootstrap.ros_backend_launcher.subprocess.Popen", return_value=process),
                patch("src.bootstrap.ros_backend_launcher.subprocess.run") as run,
                patch("src.bootstrap.ros_backend_launcher.time.sleep"),
            ):
                launcher = RosBackendLauncher(launch, stop, startup_delay_s=0, log_file=root / "backend.log")
                launcher.start()
                launcher.stop()

            run.assert_called_once_with(
                [str(stop)],
                cwd=str(root),
                check=False,
                timeout=30,
                env=unittest.mock.ANY,
            )
            process.wait.assert_called_once_with(timeout=10)
            self.assertIsNone(launcher._log_handle)

    def test_start_skips_launch_when_backend_is_already_reachable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            launch = self._script(root, "launch.sh")
            stop = self._script(root, "stop.sh")
            response = MagicMock()
            response.__enter__.return_value = response

            with (
                patch("src.bootstrap.ros_backend_launcher.urllib.request.urlopen", return_value=response),
                patch("src.bootstrap.ros_backend_launcher.subprocess.Popen") as popen,
                patch("src.bootstrap.ros_backend_launcher.subprocess.run") as run,
            ):
                launcher = RosBackendLauncher(launch, stop, startup_delay_s=0, log_file=root / "backend.log")
                launcher.start()
                launcher.stop()

            popen.assert_not_called()
            run.assert_not_called()

    def test_target_reuse_rejects_wrong_or_missing_identity(self):
        import io
        for payload in (b'{}', b'{"robot_release":{"target":"glue","profile":"paint"}}'):
            with self.subTest(payload=payload), patch(
                "src.bootstrap.ros_backend_launcher.urllib.request.urlopen",
                return_value=io.BytesIO(payload),
            ), patch("src.bootstrap.ros_backend_launcher.subprocess.Popen") as popen:
                launcher = RosBackendLauncher(robot_target="paint_tray_dry", backend_profile="paint_short_links")
                with self.assertRaises(RuntimeError):
                    launcher.start()
                popen.assert_not_called()

    def test_target_reuse_accepts_matching_identity(self):
        import io
        response = io.BytesIO(b'{"robot_release":{"target":"paint_tray_dry","profile":"paint_short_links"}}')
        with patch("src.bootstrap.ros_backend_launcher.urllib.request.urlopen", return_value=response):
            launcher = RosBackendLauncher(robot_target="paint_tray_dry", backend_profile="paint_short_links")
            self.assertTrue(launcher._backend_is_reachable())
            self.assertEqual(launcher._launch_env()["ZEROERR_ACTIVE_PROFILE"], "paint_short_links")

    def test_unmapped_target_cannot_autostart(self):
        with self.assertRaisesRegex(RuntimeError, "Missing configuration: robot_systems"):
            build_ros_backend_launcher_from_env(RosBackendConfig(), "glue")

    def test_target_cannot_use_another_workspace(self):
        with self.assertRaisesRegex(RuntimeError, "must reference"):
            build_ros_backend_launcher_from_env(RosBackendConfig(launch_script="/tmp/wrong.sh"), "paint_tray_dry")

    def test_clean_env_removes_python_virtualenv_contamination(self) -> None:
        with patch.dict(
            os.environ,
            {
                "VIRTUAL_ENV": "/tmp/app/.venv",
                "PYTHONPATH": "/tmp/app/src",
                "PYTHONHOME": "/tmp/python",
                "PATH": "/tmp/app/.venv/bin:/usr/bin:/bin",
            },
            clear=False,
        ):
            env = _clean_ros_process_env()

        self.assertNotIn("VIRTUAL_ENV", env)
        self.assertNotIn("PYTHONPATH", env)
        self.assertNotIn("PYTHONHOME", env)
        self.assertNotIn("/tmp/app/.venv/bin", env["PATH"].split(os.pathsep))
        self.assertIn("/usr/bin", env["PATH"].split(os.pathsep))
        self.assertIn("/bin", env["PATH"].split(os.pathsep))

    def test_start_can_be_disabled_by_env(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            launch = self._script(root, "launch.sh")
            stop = self._script(root, "stop.sh")

            with (
                patch.dict(os.environ, {"ROBOT_APP_BACKEND_AUTOSTART": "0"}),
                patch("src.bootstrap.ros_backend_launcher.subprocess.Popen") as popen,
            ):
                RosBackendLauncher(launch, stop).start()

            popen.assert_not_called()

    def test_start_can_be_disabled_by_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            launch = self._script(root, "launch.sh")
            stop = self._script(root, "stop.sh")

            with patch("src.bootstrap.ros_backend_launcher.subprocess.Popen") as popen:
                RosBackendLauncher(launch, stop, auto_launch=False).start()

            popen.assert_not_called()

    def test_stop_can_be_disabled_by_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            launch = self._script(root, "launch.sh")
            stop = self._script(root, "stop.sh")
            process = MagicMock()
            process.poll.return_value = None

            with (
                patch("src.bootstrap.ros_backend_launcher.urllib.request.urlopen", side_effect=OSError("down")),
                patch("src.bootstrap.ros_backend_launcher.subprocess.Popen", return_value=process),
                patch("src.bootstrap.ros_backend_launcher.subprocess.run") as run,
                patch("src.bootstrap.ros_backend_launcher.time.sleep"),
            ):
                launcher = RosBackendLauncher(launch, stop, startup_delay_s=0, log_file=root / "backend.log", auto_stop=False)
                launcher.start()
                launcher.stop()
                launcher._close_log_handle()

            run.assert_not_called()
            process.wait.assert_not_called()

    def test_builder_uses_config_defaults(self) -> None:
        launcher = build_ros_backend_launcher_from_env(
            RosBackendConfig(
                auto_launch=False,
                auto_stop=False,
                launch_script="~/custom_ws/launch.sh",
                stop_script="~/custom_ws/stop.sh",
                startup_delay_s=2.5,
                log_file="~/backend.log",
                status_timeout_s=0.7,
            )
        )

        self.assertFalse(launcher._auto_launch)
        self.assertFalse(launcher._auto_stop)
        self.assertEqual(launcher._launch_script, Path.home() / "custom_ws" / "launch.sh")
        self.assertEqual(launcher._stop_script, Path.home() / "custom_ws" / "stop.sh")
        self.assertEqual(launcher._startup_delay_s, 2.5)
        self.assertEqual(launcher._log_file, Path.home() / "backend.log")
        self.assertEqual(launcher._status_urls, ("http://127.0.0.1:5000/startup/status", "http://127.0.0.1:5000/health"))
        self.assertEqual(launcher._status_timeout_s, 0.7)

    def test_builder_defaults_to_current_users_ros_workspace(self) -> None:
        with (
            patch.dict(os.environ, {}, clear=True),
            patch("src.bootstrap.ros_backend_launcher.Path.home", return_value=Path("/home/plp")),
        ):
            launcher = build_ros_backend_launcher_from_env(RosBackendConfig())

        self.assertEqual(launcher._launch_script, Path("/home/plp/ros2_ws/launch_zeroerr.sh"))
        self.assertEqual(launcher._stop_script, Path("/home/plp/ros2_ws/stop_zeroerr.sh"))

    def test_env_overrides_config_paths(self) -> None:
        with patch.dict(
            os.environ,
            {
                "ROBOT_APP_BACKEND_LAUNCH_SCRIPT": "/tmp/env_launch.sh",
                "ROBOT_APP_BACKEND_STOP_SCRIPT": "/tmp/env_stop.sh",
            },
            clear=False,
        ):
            launcher = build_ros_backend_launcher_from_env(
                RosBackendConfig(
                    launch_script="/tmp/config_launch.sh",
                    stop_script="/tmp/config_stop.sh",
                )
            )

        self.assertEqual(launcher._launch_script, Path("/tmp/env_launch.sh"))
        self.assertEqual(launcher._stop_script, Path("/tmp/env_stop.sh"))


if __name__ == "__main__":
    unittest.main()
