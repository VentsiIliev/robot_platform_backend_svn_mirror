#!/usr/bin/python3
"""Root-owned, narrowly scoped remote-support package update helper."""
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import urllib.request

POLICY = Path('/etc/robot-remote-support.json')


def upgrade(base, release, package, version):
    policy = json.loads(POLICY.read_text())
    if base != policy['download_base_url'] or not base.startswith('https://'):
        raise ValueError('Remote-support download source requires administrator approval')
    for value in (release, package, version):
        if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._+~:-]*', value) or '..' in value:
            raise ValueError('Invalid remote-support package identifier')
    if not package.endswith('.deb'):
        raise ValueError('Remote-support package must be a Debian archive')
    with tempfile.TemporaryDirectory(prefix='robot-remote-support-') as directory:
        archive = Path(directory) / package
        with urllib.request.urlopen(base.rstrip('/') + '/' + release + '/' + package,
                                    timeout=120) as response:
            if not response.url.startswith('https://'):
                raise ValueError('Remote-support download must remain HTTPS')
            with archive.open('wb') as output:
                import shutil
                shutil.copyfileobj(response, output)
        metadata = subprocess.check_output(
            ['dpkg-deb', '-f', str(archive), 'Package', 'Version', 'Architecture', 'Maintainer'],
            text=True,
        )
        fields = dict(line.split(': ', 1) for line in metadata.splitlines())
        architecture = subprocess.check_output(['dpkg', '--print-architecture'], text=True).strip()
        if fields != {'Package': 'rustdesk', 'Version': version,
                      'Architecture': architecture, 'Maintainer': 'PL PROJECT'}:
            raise ValueError('Remote-support package metadata does not match the release')
        subprocess.run(['apt-get', '-o', 'DPkg::Lock::Timeout=600', 'install', '-y', str(archive)], check=True)
        subprocess.run(['systemctl', 'enable', '--now', 'rustdesk.service'], check=True)
        subprocess.run(['systemctl', 'is-active', '--quiet', 'rustdesk.service'], check=True)
        actual = subprocess.check_output(['dpkg-query', '-W', '-f=${Status}|${Version}', 'rustdesk'], text=True)
        if actual.strip() != 'install ok installed|' + version:
            raise RuntimeError('Remote-support package verification failed')


if __name__ == '__main__':
    if os.geteuid() != 0 or len(sys.argv) != 6 or sys.argv[1] != 'upgrade':
        sys.exit('Usage (root): robot-remote-support-update upgrade BASE RELEASE PACKAGE VERSION')
    upgrade(*sys.argv[2:])
