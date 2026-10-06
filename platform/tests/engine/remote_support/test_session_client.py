import json
import unittest
from unittest.mock import patch

from src.engine.remote_support.session_client import RustDeskSessionClient


class _Socket:
    def __init__(self, response):
        self.response = bytearray(response)
        self.sent = None

    def __enter__(self):
        return self

    def __exit__(self, *_):
        pass

    def settimeout(self, _):
        pass

    def connect(self, path):
        self.path = path

    def sendall(self, data):
        self.sent = data

    def recv(self, length):
        # Split every read to exercise partial socket delivery.
        data = bytes(self.response[:min(length, 1)])
        del self.response[:len(data)]
        return data


class RustDeskSessionClientTests(unittest.TestCase):
    def query(self, response, width=1):
        payload = json.dumps(response).encode()
        header = ((len(payload) << 2) | (width - 1)).to_bytes(width, "little")
        connection = _Socket(header + payload)
        with patch("src.engine.remote_support.session_client.socket.socket", return_value=connection):
            count = RustDeskSessionClient("/test/ipc").get_session_count()
        self.assertEqual(json.loads(connection.sent[1:]), {"t": "VideoConnCount", "c": None})
        return count

    def test_authenticated_counts_and_partial_frames(self):
        for count in (0, 1, 3):
            for width in (1, 2, 3, 4):
                with self.subTest(count=count, width=width):
                    self.assertEqual(self.query({"t": "VideoConnCount", "c": count}, width), count)

    def test_invalid_responses_never_become_zero(self):
        for response in ([], {"t": "OnlineStatus", "c": 0},
                         {"t": "VideoConnCount", "c": None},
                         {"t": "VideoConnCount", "c": True},
                         {"t": "VideoConnCount", "c": -1}):
            with self.subTest(response=response), self.assertRaises(ValueError):
                self.query(response)

    def test_truncated_and_oversized_frames_are_rejected(self):
        for response in (b"", b"\x04", ((5000 << 2) | 1).to_bytes(2, "little")):
            with patch("src.engine.remote_support.session_client.socket.socket", return_value=_Socket(response)):
                with self.assertRaises(ValueError):
                    RustDeskSessionClient().get_session_count()

    def test_password_request_uses_multibyte_frame_header(self):
        response = b'{"t":"Config","c":["permanent-password","Y"]}'
        connection = _Socket(bytes([len(response) << 2]) + response)
        request = {"t":"Config","c":["permanent-password", "test-value-"*6]}
        with patch("src.engine.remote_support.session_client.socket.socket", return_value=connection):
            self.assertEqual(RustDeskSessionClient('/test/ipc')._exchange(request), json.loads(response))
        width = (connection.sent[0] & 3) + 1
        self.assertGreater(width, 1)
        self.assertEqual(int.from_bytes(connection.sent[:width], 'little') >> 2, len(connection.sent[width:]))
        self.assertEqual(json.loads(connection.sent[width:]), request)
