"""Own the RViz launch session independently of the robot/MoveIt processes."""

import os
from pathlib import Path
import shutil
import signal
import subprocess
import tempfile
import threading


def build_rviz_command():
    try:
        from ament_index_python.packages import get_package_prefix, get_package_share_directory
        executable = Path(get_package_prefix('rviz2')) / 'lib' / 'rviz2' / 'rviz2'
        launch_file = Path(get_package_share_directory('zeroerr')) / 'launch' / 'moveit_rviz.launch.py'
    except (ImportError, LookupError) as exc:
        raise RuntimeError('RViz or its ZeroErr launch configuration is not installed') from exc
    ros2 = shutil.which('ros2')
    if not ros2 or not executable.is_file() or not os.access(executable, os.X_OK) or not launch_file.is_file():
        raise RuntimeError('RViz or its ZeroErr launch configuration is not installed')
    cores = os.environ.get('ZEROERR_LOW_PRIORITY_CORES') or os.environ.get('ZEROERR_NON_RT_CORES', '0')
    return ['taskset', '-c', cores, 'nice', '-n', '19', ros2, 'launch', 'zeroerr', 'moveit_rviz.launch.py']


class RvizProcessManager:
    def __init__(self, on_state_changed=None, command_builder=build_rviz_command):
        self._lock = threading.RLock()
        self._process = None
        self._log = None
        self._error = None
        self._on_state_changed = on_state_changed
        self._command_builder = command_builder

    def _state(self):
        running = self._process is not None and self._process.poll() is None
        if self._process is not None and not running and self._process.returncode and not self._error:
            self._error = self._read_error()
        if self._on_state_changed is not None:
            self._on_state_changed(running)
        result = {'success': True, 'running': running}
        if self._error:
            result['error'] = self._error
        return result

    def _read_error(self):
        detail = ''
        if self._log is not None:
            self._log.seek(0, os.SEEK_END)
            self._log.seek(max(0, self._log.tell() - 2048))
            detail = self._log.read().decode('utf-8', errors='replace').strip()
        return f'RViz exited with code {self._process.returncode}' + (f': {detail}' if detail else '')

    def status(self):
        with self._lock:
            return self._state()

    def set_enabled(self, enabled):
        if not isinstance(enabled, bool):
            return {'success': False, 'error': 'enabled must be a boolean'}
        with self._lock:
            try:
                if enabled:
                    if self._state()['running']:
                        return self._state()
                    if not os.environ.get('DISPLAY') and not os.environ.get('WAYLAND_DISPLAY'):
                        raise RuntimeError('The backend has no graphical display available for RViz')
                    command = self._command_builder()
                    if self._log is not None:
                        self._log.close()
                    self._log = tempfile.TemporaryFile()
                    self._error = None
                    self._process = subprocess.Popen(
                        command, stdout=self._log, stderr=subprocess.STDOUT,
                        start_new_session=True,
                    )
                    try:
                        self._process.wait(timeout=0.2)
                    except subprocess.TimeoutExpired:
                        pass
                    result = self._state()
                    if not result['running']:
                        result.update(success=False, error=self._read_error())
                    return result
                self._stop()
                return self._state()
            except (OSError, RuntimeError, subprocess.TimeoutExpired) as exc:
                message = str(exc)
                result = self._state()
                self._error = message
                result.update(success=False, error=message)
                return result

    def _stop(self):
        process = self._process
        if process is not None and process.poll() is None:
            # Only signal the new session we created; never use global pkill.
            for sig, timeout in ((signal.SIGINT, 3), (signal.SIGTERM, 1), (signal.SIGKILL, 1)):
                try:
                    os.killpg(process.pid, sig)
                except ProcessLookupError:
                    break
                try:
                    process.wait(timeout=timeout)
                    break
                except subprocess.TimeoutExpired:
                    if sig == signal.SIGKILL:
                        raise
        self._process = None
        self._error = None
        if self._log is not None:
            self._log.close()
            self._log = None

    def close(self):
        return self.set_enabled(False)
