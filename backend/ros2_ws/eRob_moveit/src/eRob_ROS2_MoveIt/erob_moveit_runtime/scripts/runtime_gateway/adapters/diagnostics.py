"""Backend process ownership for diagnostics; never exposed to API handlers."""
import os
import subprocess
import threading

from runtime_gateway.errors import GatewayError


class RuntimeDiagnostics:
    def __init__(self, node_getter, collision_channel, rviz_manager=None):
        self._node_getter = node_getter
        self._collision = collision_channel
        self._rviz = rviz_manager
        self._process = None
        self._lock = threading.Lock()

    def rviz_status(self):
        if self._rviz is None:
            raise GatewayError('rviz_unavailable', 'RViz process management is not configured', kind='unsupported')
        return self._rviz.status()

    def set_rviz_enabled(self, enabled):
        if self._rviz is None:
            raise GatewayError('rviz_unavailable', 'RViz process management is not configured', kind='unsupported')
        if enabled and self._node_getter() is None:
            raise GatewayError('runtime_unavailable', 'Robot runtime is still initializing', kind='unavailable', retryable=True)
        return self._rviz.set_enabled(enabled)

    def open_collision_diagnostics(self):
        with self._lock:
            if self._process is not None and self._process.poll() is None:
                return {'success': True, 'already_running': True,
                        'config': self._collision.publish({'diagnostics_enabled': True})}
            from ament_index_python.packages import get_package_prefix, get_package_share_directory
            try:
                executable = os.path.join(get_package_prefix('plotjuggler'), 'lib', 'plotjuggler', 'plotjuggler')
            except LookupError as error:
                raise GatewayError('diagnostics_not_installed', 'PlotJuggler is not installed',
                                   kind='unavailable') from error
            if not os.path.isfile(executable) or not os.access(executable, os.X_OK):
                raise GatewayError('diagnostics_executable_unavailable', 'PlotJuggler executable is unavailable',
                                   kind='unavailable', details={'executable': executable})
            if not os.environ.get('DISPLAY') and not os.environ.get('WAYLAND_DISPLAY'):
                raise GatewayError('display_unavailable', 'The backend has no graphical display for PlotJuggler',
                                   kind='unavailable')
            state = self._collision.publish({'diagnostics_enabled': True})
            layout = os.path.join(get_package_share_directory('zeroerr'), 'config', 'collision_observer_plotjuggler.xml')
            try:
                self._process = subprocess.Popen(
                    [executable, '-l', layout, '--start_streamer', 'DataStreamROS2', '--buffer_size', '30'],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
            except OSError as error:
                raise GatewayError('diagnostics_start_failed', f'Could not start PlotJuggler: {error}',
                                   details={'errno': error.errno}) from error
            return {'success': True, 'already_running': False, 'config': state}

    def close(self):
        if self._rviz is not None:
            self._rviz.close()
        with self._lock:
            if self._process is not None and self._process.poll() is None:
                self._process.terminate()
                try:
                    self._process.wait(timeout=2.0)
                except subprocess.TimeoutExpired:
                    self._process.kill()
                    self._process.wait(timeout=2.0)
