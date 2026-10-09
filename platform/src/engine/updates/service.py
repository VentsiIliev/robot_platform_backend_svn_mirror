"""Per-user update daemon; the GUI and launcher only submit requests."""
import json
import os
from pathlib import Path
import socket
import socketserver
import threading
import time

from .config import UpdateConfig
from .files import lock
from .updater import PlatformUpdater


def request(config_path, operation, timeout=1800):
    config = UpdateConfig.load(Path(config_path))
    with socket.socket(socket.AF_UNIX) as connection:
        connection.settimeout(timeout)
        connection.connect(str(config.install_root / 'update-state/service.sock'))
        connection.sendall(json.dumps({'operation': operation}).encode() + b'\n')
        with connection.makefile('rb') as stream:
            response = json.loads(stream.readline(1024 * 1024))
    if not response['ok']:
        raise RuntimeError(response['error'])
    return response.get('result')


class UpdateService:
    def __init__(self, config_path):
        self.config_path = Path(config_path)
        self.guard = threading.Lock()

    def updater(self):
        return PlatformUpdater(UpdateConfig.load(self.config_path))

    def dispatch(self, operation):
        with self.guard:
            updater = self.updater()
            if operation == 'check':
                return updater.check()
            if operation == 'download':
                return updater.stage_latest()
            if operation == 'queue':
                updater.queue()
                return None
            if operation == 'status':
                installed = updater.installed() or {}
                def read(name):
                    path = updater.state / name
                    return json.loads(path.read_text()) if path.exists() else {}
                return dict(installed=installed.get('version', ''), staged=read('staged.json').get('version', ''),
                            configuration=str(self.config_path), enabled=updater.config.enabled,
                            result=read('result.json'), release_kind=installed.get('component', 'platform'))
            raise ValueError('Unknown update-service operation')

    def apply_when_offline(self):
        with self.guard:
            updater = self.updater()
            def stop_backend():
                if not (updater.state / 'pending.json').exists() and not (updater.state / 'transaction.json').exists():
                    return
                current = updater.installed()
                if current and current.get('component') == 'robot':
                    import subprocess
                    from .environment import subprocess_environment
                    subprocess.run([str(updater.root / 'current/backend/stop.sh')],
                                   check=True, timeout=60, env=subprocess_environment())
            return updater.apply_pending(before_activation=stop_backend)



def serve(config_path):
    service = UpdateService(config_path)
    updater = service.updater()
    updater.state.mkdir(parents=True, exist_ok=True)
    endpoint = updater.state / 'service.sock'

    class Handler(socketserver.StreamRequestHandler):
        def handle(self):
            self.connection.settimeout(30)
            try:
                raw = json.loads(self.rfile.readline(4096))
                result = service.dispatch(raw['operation'])
                response = dict(ok=True, result=result)
            except Exception as error:
                response = dict(ok=False, error=str(error))
            self.wfile.write(json.dumps(response).encode() + b'\n')

    with lock(updater.state / 'service.lock'):
        endpoint.unlink(missing_ok=True)
        with socketserver.ThreadingUnixStreamServer(str(endpoint), Handler) as server:
            os.chmod(endpoint, 0o600)
            server.daemon_threads = True
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                while True:
                    try:
                        if service.apply_when_offline():
                            # Reload release-owned service code after activating the new tools.
                            import sys
                            helper = updater.root / 'tools/manage.py'
                            if helper.is_file():
                                os.execv('/usr/bin/python3', ['/usr/bin/python3', str(helper),
                                                           '--config', str(service.config_path), 'serve'])
                    except RuntimeError as error:
                        if str(error) != 'Platform is running or another update is in progress':
                            print(f'Update service: {error}', flush=True)
                    except Exception as error:
                        print(f'Update service: {error}', flush=True)
                    time.sleep(1)
            finally:
                server.shutdown()
                endpoint.unlink(missing_ok=True)
