"""Connection discovery must remain useful when individual tools are missing."""

import json
import subprocess
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from src.applications.login.connection_information_reader import ConnectionInformationReader


class TestConnectionInformationReader(unittest.TestCase):
    def read(self, addresses, rustdesk="123456789"):
        def run(command, **kwargs):
            result = addresses if command[0] == "ip" else rustdesk
            if isinstance(result, Exception):
                raise result
            return subprocess.CompletedProcess(command, 0, result)

        with patch("src.applications.login.connection_information_reader.subprocess.run", side_effect=run), \
             patch("src.applications.login.connection_information_reader.socket.gethostname", return_value="plp"), \
             patch("src.applications.login.connection_information_reader.pwd.getpwuid", return_value=SimpleNamespace(pw_name="pl_user")):
            return ConnectionInformationReader().read()

    def test_lists_lan_vpn_without_loopback_link_local_or_duplicates(self):
        interfaces = [
            {"ifname": "lo", "flags": ["UP", "LOOPBACK"], "addr_info": [
                {"family": "inet", "local": "127.0.0.1"},
                {"family": "inet6", "local": "::1"},
            ]},
            {"ifname": "enp1s0", "addr_info": [
                {"family": "inet", "local": "192.168.222.12"},
                {"family": "inet", "local": "192.168.222.12"},
                {"family": "inet6", "local": "fe80::1234"},
            ]},
            {"ifname": "wg0", "addr_info": [{"family": "inet", "local": "10.20.0.2"}]},
        ]
        information = self.read(json.dumps(interfaces))
        self.assertEqual(information, {
            "hostname": "plp", "username": "pl_user", "rustdesk_id": "123456789",
            "addresses": [
                {"interface": "enp1s0", "address": "192.168.222.12"},
                {"interface": "wg0", "address": "10.20.0.2"},
            ],
        })

    def test_docker_vm_and_veth_noise_is_removed_but_vpn_and_lan_bridge_are_kept(self):
        names = ("wlp2s0", "virbr0", "br-04c74cf5bbeb", "docker0", "vetha03cb23", "wg0", "br0")
        interfaces = [{"ifname": name, "addr_info": [
            {"family": "inet", "local": "192.168.222.112"},
            {"family": "inet6", "local": "fe80::1234"},
        ]} for name in names]
        addresses = self.read(json.dumps(interfaces))["addresses"]
        self.assertEqual({"wlp2s0", "wg0", "br0"}, {item["interface"] for item in addresses})
        self.assertTrue(all(item["address"] == "192.168.222.112" for item in addresses))

    def test_username_unavailable_does_not_discard_network_details(self):
        with patch("src.applications.login.connection_information_reader.pwd.getpwuid", side_effect=KeyError), \
             patch("src.applications.login.connection_information_reader.subprocess.run", return_value=subprocess.CompletedProcess([], 0, "[]")):
            self.assertIsNone(ConnectionInformationReader().read()["username"])

    def test_empty_success_differs_from_unavailable_network_information(self):
        self.assertEqual(self.read("[]")["addresses"], [])
        for failure in (FileNotFoundError(), subprocess.TimeoutExpired("ip", 2),
                        subprocess.CalledProcessError(1, "ip"), "invalid json"):
            with self.subTest(failure=failure):
                information = self.read(failure)
                self.assertIsNone(information["addresses"])
                self.assertEqual(information["hostname"], "plp")
                self.assertEqual(information["rustdesk_id"], "123456789")

    def test_missing_rustdesk_preserves_other_information(self):
        information = self.read("[]", FileNotFoundError())
        self.assertEqual(information["hostname"], "plp")
        self.assertEqual(information["addresses"], [])
        self.assertIsNone(information["rustdesk_id"])

    def test_empty_or_diagnostic_rustdesk_output_is_not_presented_as_an_id(self):
        for output in ("", "warning\n123456789", "x" * 129):
            with self.subTest(output=output):
                self.assertIsNone(self.read("[]", output)["rustdesk_id"])

    def test_commands_are_read_only_and_have_a_timeout(self):
        with patch("src.applications.login.connection_information_reader.subprocess.run") as run:
            run.side_effect = [subprocess.CompletedProcess([], 0, "[]"),
                               subprocess.CompletedProcess([], 0, "123456789")]
            ConnectionInformationReader(timeout=.5).read()
        self.assertEqual([call.args[0] for call in run.call_args_list],
                         [["ip", "-j", "address", "show", "up"], ["rustdesk", "--get-id"]])
        for call in run.call_args_list:
            self.assertEqual(call.kwargs["timeout"], .5)
            self.assertTrue(call.kwargs["check"])


if __name__ == "__main__":
    unittest.main()
