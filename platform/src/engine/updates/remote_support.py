"""Reconcile the release's native remote-support dependency before activation."""
from pathlib import Path
import shlex
import subprocess

from .environment import subprocess_environment


def release_settings(release):
    path = Path(release) / 'platform/installation/remote-support/release.conf'
    if not path.is_file():
        return None  # Releases predating dependency reconciliation.
    values = {}
    for line in path.read_text().splitlines():
        tokens = shlex.split(line, comments=True)
        if not tokens:
            continue
        if len(tokens) != 1 or '=' not in tokens[0]:
            raise ValueError('Invalid remote-support release configuration')
        key, value = tokens[0].split('=', 1)
        values[key] = value
    for key in ('DOWNLOAD_BASE_URL', 'RELEASE', 'PACKAGE', 'EXPECTED_VERSION'):
        if not values.get(key):
            raise ValueError('Missing remote-support setting: ' + key)
    return values


def reconcile(release):
    settings = release_settings(release)
    if settings is None:
        return
    environment = subprocess_environment()
    installed = subprocess.run(
        ['dpkg-query', '-W', '-f=${Status}|${Version}', 'rustdesk'],
        capture_output=True, text=True, env=environment,
    )
    if installed.returncode == 0 and installed.stdout.strip() == (
            'install ok installed|' + settings['EXPECTED_VERSION']):
        return
    command = ['sudo', '-n', '/usr/local/libexec/robot-remote-support-update',
               'upgrade', settings['DOWNLOAD_BASE_URL'], settings['RELEASE'],
               settings['PACKAGE'], settings['EXPECTED_VERSION']]
    try:
        subprocess.run(command, check=True, env=environment, timeout=1800)
    except (OSError, subprocess.SubprocessError) as error:
        raise RuntimeError('Required remote-support upgrade failed. Run the trusted installer '
                           'to provision the privileged update helper; inspect the service journal.') from error
