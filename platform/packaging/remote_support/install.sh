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
auto_login="$source_dir/auto_login.sh"
if [[ ! -f "$auto_login" ]]; then
    auto_login="$source_dir/../kiosk/auto_login.sh"
fi
[[ -f "$auto_login" ]] || { echo "Automatic-login helper is missing" >&2; exit 1; }
if [[ ! $ui_user =~ ^[a-z_][a-z0-9_-]*$ ]] || [[ $ui_user == root ]] || ! id -u "$ui_user" >/dev/null 2>&1; then
    echo "ROBOT_UI_USER must be an existing local user" >&2
    exit 2
fi
if [[ -z "$vendor_installer" && $(systemctl show --property=LoadState --value rustdesk.service) != loaded ]]; then
    echo "Install the system rustdesk.service unit first" >&2
    exit 1
fi

# Retire the old timed-access controller before enabling permanent boot startup.
# Stop its socket first so it cannot reactivate the controller during migration.
for unit in plproject-remote-support.socket plproject-remote-support-expiry.timer \
            plproject-remote-support-expiry.service plproject-remote-support.service; do
    if [[ $(systemctl show --property=LoadState --value "$unit") == loaded ]]; then
        systemctl disable --now "$unit"
    fi
done
rm -f /etc/systemd/system/rustdesk.service.d/plproject-remote-support.conf
systemctl daemon-reload

apt-get update
# The frozen platform still loads these native libraries from the operating system.
apt-get -o DPkg::Lock::Timeout=600 install -y openssh-server libzbar0 libxcb-cursor0
# /run is temporary; a fresh installation may not have started ssh.service yet.
install -d -o root -g root -m 0755 /run/sshd
/usr/sbin/sshd -t
systemctl enable --now ssh.service

if [[ -n "$vendor_installer" ]]; then
    USER="$ui_user" bash "$vendor_installer" --provision-only
    systemctl daemon-reload
fi
if [[ $(systemctl show --property=LoadState --value rustdesk.service) != loaded ]]; then
    echo "Vendor installer did not install rustdesk.service" >&2
    exit 1
fi
systemctl enable --now rustdesk.service
systemctl is-active --quiet rustdesk.service
systemctl is-active --quiet ssh.service
install -o root -g root -m 0755 "$auto_login" /usr/local/bin/auto_login.sh
echo "SSH and PL PROJECT remote support installed and enabled at boot."
