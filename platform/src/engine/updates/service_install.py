"""Install one unprivileged systemd update service per robot installation."""
import os
from pathlib import Path
import subprocess

from .environment import subprocess_environment
from .files import atomic_json


def install_service(root, config_path):
    root = Path(root).resolve()
    config_path = Path(config_path).resolve()
    target = root.name
    if not target or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_' for c in target):
        raise ValueError('Invalid update service target')
    unit = f'robot-update-{target}.service'
    directory = Path.home() / '.config/systemd/user'
    directory.mkdir(parents=True, exist_ok=True)
    def quote(value):
        return '"' + str(value).replace('\\', '\\\\').replace('"', '\\"').replace('%', '%%') + '"'
    source = ('[Unit]\nDescription=Robot system update service\n'
              '[Service]\nType=simple\nExecStart=/usr/bin/python3 ' + quote(root/'tools/manage.py') +
              ' --config ' + quote(config_path) + ' serve\nRestart=on-failure\nRestartSec=3\n'
              'UMask=0077\n'
              '[Install]\nWantedBy=default.target\n')
    (directory/unit).write_text(source)
    environment = subprocess_environment()
    environment.setdefault('XDG_RUNTIME_DIR', f'/run/user/{os.getuid()}')
    environment.setdefault('DBUS_SESSION_BUS_ADDRESS', 'unix:path=' + environment['XDG_RUNTIME_DIR'] + '/bus')
    subprocess.run(['systemctl', '--user', 'daemon-reload'], check=True, env=environment)
    subprocess.run(['systemctl', '--user', 'enable', unit], check=True, env=environment)
    subprocess.run(['systemctl', '--user', 'restart', unit], check=True, env=environment)
    atomic_json(root/'update-state/service.json', {'unit': unit})
