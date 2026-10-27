"""Read local connection details without changing network or support settings."""

import ipaddress
import json
import os
import pwd
import socket
import subprocess


class ConnectionInformationReader:
    """Collect a bounded, best-effort snapshot for the pre-login support panel."""

    def __init__(self, timeout: float = 2) -> None:
        self._timeout = timeout

    def read(self) -> dict:
        """Return hostname, interface/address pairs and RustDesk ID independently.

        A missing value is None; an empty address list means the query succeeded
        but no non-loopback addresses were assigned to interfaces that are up.
        """
        try:
            hostname = socket.gethostname()
        except OSError:
            hostname = None
        try:
            username = pwd.getpwuid(os.getuid()).pw_name
        except (OSError, KeyError):
            username = None
        return {
            "hostname": hostname,
            "username": username,
            "addresses": self._read_addresses(),
            "rustdesk_id": self._read_rustdesk_id(),
        }

    def _run(self, command: list[str]) -> str:
        result = subprocess.run(
            command, capture_output=True, text=True, timeout=self._timeout,
            check=True,
        )
        return result.stdout.strip()

    def _read_addresses(self) -> list[dict] | None:
        try:
            interfaces = json.loads(self._run(["ip", "-j", "address", "show", "up"]))
            addresses = []
            for interface in interfaces:
                name = interface["ifname"]
                if ("LOOPBACK" in interface.get("flags", []) or
                        name.startswith(("docker", "virbr", "veth", "br-"))):
                    continue
                for entry in interface.get("addr_info", []):
                    if entry.get("family") not in ("inet", "inet6"):
                        continue
                    if {"tentative", "dadfailed"}.intersection(entry.get("flags", [])):
                        continue
                    address = ipaddress.ip_address(entry["local"])
                    if (address.is_loopback or address.is_unspecified or
                            address.is_multicast or address.is_link_local):
                        continue
                    value = str(address)
                    item = {"interface": name, "address": value}
                    if item not in addresses:
                        addresses.append(item)
            return sorted(addresses, key=lambda item: (ipaddress.ip_address(item["address"]).version,
                                                       item["interface"], item["address"]))
        except (OSError, subprocess.SubprocessError, ValueError, KeyError, TypeError):
            return None

    def _read_rustdesk_id(self) -> str | None:
        try:
            value = self._run(["rustdesk", "--get-id"])
            return value if value and len(value) <= 128 and len(value.splitlines()) == 1 else None
        except (OSError, subprocess.SubprocessError):
            return None
