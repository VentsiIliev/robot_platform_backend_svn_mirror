"""Installer account commissioning through hardware-free tools and root maintenance.

Only stdlib imports: this module also runs in the isolated installed updater.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess

from .environment import subprocess_environment
from .releases import release_executable


def provision_installation_accounts(root, config_path, *, initialize=False):
    """Require an enabled Manufacturer before deployment setup can complete.

    Initialization is allowed only for a recorded fresh installation. Established
    stores must open successfully; missing/corrupt data never triggers a reset.
    Passwords are collected solely by the root-owned interactive maintenance tool.
    The caller may hold root/runtime.lock, but not update-state/runtime.lock:
    the frozen tools acquire the latter themselves.
    """
    if os.geteuid() == 0:
        raise RuntimeError("Run the installer as the platform desktop user, without sudo; "
                           "administrator authentication is requested separately.")
    root = Path(root).resolve()
    manifest = json.loads((root / 'current/manifest.json').read_text())
    executable = root / 'current/platform' / release_executable(manifest)
    environment = subprocess_environment()
    environment['ROBOT_PLATFORM_DATA_ROOT'] = str(root / 'data')
    environment['ROBOT_PLATFORM_UPDATE_CONFIG'] = str(Path(config_path or root / 'updates.json').resolve())
    # Invoke the executable directly: the stable launcher would reacquire the
    # installer-held root lock. Tool mode exits before Qt, seeding and hardware.
    if initialize:
        subprocess.run([str(executable), '--account-setup'], env=environment, check=True)
    record = subprocess.run([str(executable), '--account-locations'], env=environment,
                            check=True, capture_output=True, text=True)
    locations = json.loads(record.stdout)
    database = Path(locations['database'])
    if (not locations.get('installation_id') or locations.get('platform_uid') != os.getuid()
            or not database.is_absolute() or not database.resolve().is_relative_to(root / 'data')
            or not database.is_file()):
        raise RuntimeError("Account installation is not ready for this platform OS user.")

    # Refuse deployment completion before kiosk can enter a restart loop. This
    # seeds only fresh settings and reads every required repository without ROS/Qt.
    subprocess.run([str(executable), '--check-installation'], env=environment, check=True)

    payload = root / 'current/platform/installation/account-maintenance'
    archive = payload / 'account-maintenance.pyz'
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    trusted = Path('/root/robot-account-maintenance') / digest
    # Root executes the delivered installer only after staging it into a private
    # administrator-owned directory, just like the documented manual procedure.
    subprocess.run(['sudo', 'install', '-d', '-o', 'root', '-g', 'root', '-m', '700',
                    str(trusted)], check=True)
    subprocess.run(['sudo', 'install', '-o', 'root', '-g', 'root', '-m', '644',
                    str(archive), str(payload / 'account-maintenance.pyz.sha256'),
                    str(payload / 'install.py'), str(trusted)], check=True)
    subprocess.run(['sudo', '/usr/bin/python3', '-I', str(trusted / 'install.py')], check=True)
    subprocess.run(['sudo', '/usr/local/sbin/robot-account-maintenance',
                    '--database', str(database), 'ensure-manufacturer'], check=True)
