#!/usr/bin/env bash
# Toggle Ubuntu GDM automatic login without interrupting an active session.
set -euo pipefail
if [[ $# -lt 1 || $# -gt 2 || ( $1 != on && $1 != off ) ]]; then
    echo "Usage: sudo auto_login.sh on [USER] | off" >&2
    exit 2
fi
[[ $EUID -eq 0 ]] || { echo "Run with sudo." >&2; exit 1; }
[[ -f /etc/gdm3/custom.conf ]] || { echo "GDM3 configuration not found." >&2; exit 1; }
python3 - "$1" "${2:-}" <<'PY'
import configparser
import os
from pathlib import Path
import pwd
import re
import shutil
import sys
import tempfile

mode, requested_user = sys.argv[1:]
path = Path('/etc/gdm3/custom.conf')
text = path.read_text()
parser = configparser.ConfigParser(interpolation=None)
parser.read_string(text)
values = {'AutomaticLoginEnable': 'True' if mode == 'on' else 'False',
          'TimedLoginEnable': 'False'}
if mode == 'on':
    # An explicit user takes precedence. Otherwise retain the configured kiosk
    # account, falling back to the account invoking sudo on a fresh machine.
    user = requested_user
    user = user or parser.get('daemon', 'AutomaticLogin', fallback='')
    user = user or os.environ.get('SUDO_USER', '')
    try:
        account = pwd.getpwnam(user)
    except KeyError:
        raise SystemExit('Specify an existing account: sudo auto_login.sh on USER')
    if account.pw_uid == 0:
        raise SystemExit('Automatic login requires a non-root account')
    values['AutomaticLogin'] = user

# Preserve comments and unrelated configuration, changing only daemon keys.
section = re.search(r'^\[daemon\][ \t]*\r?\n', text, re.M)
if section:
    next_section = re.search(r'^\[', text[section.end():], re.M)
    end = section.end() + next_section.start() if next_section else len(text)
    body = text[section.end():end]
    for key in values:
        body = re.sub(r'^\s*' + key + r'\s*=.*\n?', '', body, flags=re.M | re.I)
    updated = text[:section.end()] + body.rstrip('\n') + '\n' + ''.join(
        f'{key}={value}\n' for key, value in values.items()) + '\n' + text[end:]
else:
    updated = text.rstrip('\n') + '\n\n[daemon]\n' + ''.join(
        f'{key}={value}\n' for key, value in values.items())
backup = path.with_name('custom.conf.before-auto-login')
if not backup.exists():
    shutil.copy2(path, backup)
metadata = path.stat()
fd, temporary = tempfile.mkstemp(dir=path.parent, prefix='.auto-login-')
try:
    with os.fdopen(fd, 'w') as stream:
        os.fchown(stream.fileno(), metadata.st_uid, metadata.st_gid)
        os.fchmod(stream.fileno(), metadata.st_mode & 0o777)
        stream.write(updated)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)
finally:
    Path(temporary).unlink(missing_ok=True)
print(f'Automatic login: {mode}. Reboot when ready; the current session is unchanged.')
PY
