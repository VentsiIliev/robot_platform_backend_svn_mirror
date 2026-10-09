#!/usr/bin/env bash
set -euo pipefail
[[ $EUID == 0 && $# == 1 ]] || { echo 'Run as root with the desktop user'; exit 2; }
ui_user=$1
[[ $ui_user =~ ^[a-z_][a-z0-9_-]*$ && $ui_user != root ]] && id "$ui_user" >/dev/null
source_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
source "$source_dir/release.conf"
install -d -o root -g root -m 0755 /usr/local/libexec
install -o root -g root -m 0755 "$source_dir/update_package.py" /usr/local/libexec/robot-remote-support-update
/usr/bin/python3 - "$DOWNLOAD_BASE_URL" <<'PY'
import json, os, sys
from pathlib import Path
path = Path('/etc/robot-remote-support.json')
path.write_text(json.dumps({'download_base_url': sys.argv[1]}))
os.chmod(path, 0o644)
PY
policy=$(mktemp)
trap 'rm -f "$policy"' EXIT
printf '%s ALL=(root) NOPASSWD: /usr/local/libexec/robot-remote-support-update upgrade *\n' "$ui_user" > "$policy"
visudo -cf "$policy"
install -o root -g root -m 0440 "$policy" "/etc/sudoers.d/robot-remote-support-$ui_user"
