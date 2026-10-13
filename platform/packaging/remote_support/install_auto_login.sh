#!/usr/bin/env bash
set -euo pipefail

if [[ ${EUID} -ne 0 || $# -ne 1 ]]; then
    echo "Usage: sudo $0 ROBOT_UI_USER" >&2
    exit 2
fi
ui_user=$1
if [[ ! $ui_user =~ ^[a-z_][a-z0-9_-]*$ ]] || [[ $ui_user == root ]] || ! id -u "$ui_user" >/dev/null 2>&1; then
    echo "ROBOT_UI_USER must be an existing local user" >&2
    exit 2
fi

source_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
auto_login="$source_dir/auto_login.sh"
if [[ ! -f "$auto_login" ]]; then
    auto_login="$source_dir/../kiosk/auto_login.sh"
fi
[[ -f "$auto_login" ]] || { echo "Automatic-login helper is missing" >&2; exit 1; }
install -o root -g root -m 0755 "$auto_login" /usr/local/bin/auto_login.sh
echo "Automatic-login helper installed."
