#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 && $# -ne 3 ]]; then
    echo "Usage: sudo $0 ROBOT_UI_USER [--vendor-installer PATH]" >&2
    exit 2
fi
vendor_installer=""
if [[ $# -eq 3 ]]; then
    if [[ $2 != --vendor-installer || ! -f $3 ]]; then
        echo "Provide --vendor-installer followed by a trusted installer file" >&2
        exit 2
    fi
    vendor_installer=$(realpath -- "$3")
fi
if [[ ${EUID} -ne 0 ]]; then
    echo "Run this installer as root" >&2
    exit 2
fi

ui_user=$1
source_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
if [[ ! $ui_user =~ ^[a-z_][a-z0-9_-]*$ ]] || [[ $ui_user == root ]] || ! id -u "$ui_user" >/dev/null 2>&1; then
    echo "ROBOT_UI_USER must be an existing local user" >&2
    exit 2
fi

bash "$source_dir/install_openssh.sh"
if [[ -n "$vendor_installer" ]]; then
    bash "$source_dir/install_rustdesk.sh" "$ui_user" --vendor-installer "$vendor_installer"
else
    bash "$source_dir/install_rustdesk.sh" "$ui_user"
fi
bash "$source_dir/install_auto_login.sh" "$ui_user"
bash "$source_dir/install_update_helper.sh" "$ui_user"
echo "SSH and PL PROJECT remote support installed and enabled at boot."
