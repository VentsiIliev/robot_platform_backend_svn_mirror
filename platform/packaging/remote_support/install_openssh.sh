#!/usr/bin/env bash
set -euo pipefail

if [[ ${EUID} -ne 0 || $# -ne 0 ]]; then
    echo "Usage: sudo $0" >&2
    exit 2
fi

apt-get update
apt-get -o DPkg::Lock::Timeout=600 install -y openssh-server
# /run is temporary; a fresh installation may not have started ssh.service yet.
install -d -o root -g root -m 0755 /run/sshd
/usr/sbin/sshd -t
systemctl enable --now ssh.service
systemctl is-active --quiet ssh.service
echo "OpenSSH installed and enabled at boot."
