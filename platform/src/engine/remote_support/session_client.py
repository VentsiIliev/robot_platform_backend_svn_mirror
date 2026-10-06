"""Read-only RustDesk 1.4.9 desktop-session query over its user IPC socket.

VideoConnCount counts authenticated incoming desktop connections (not relay
connections, pending authorization, or file transfers). The IPC API is internal;
an incompatible RustDesk build must be reported as unknown, never as zero.
"""

import json
import os
import socket
import time


class RustDeskSessionClient:
    def __init__(self, socket_path: str | None = None, timeout: float = 1) -> None:
        self._socket_path = socket_path or f"/tmp/RustDesk-{os.getuid()}/ipc"
        self._timeout = timeout

    def get_session_count(self) -> int:
        response = self._exchange({"t": "VideoConnCount", "c": None})
        if not isinstance(response, dict) or response.get("t") != "VideoConnCount":
            raise ValueError("Unexpected RustDesk IPC response")
        count = response.get("c")
        if type(count) is not int or count < 0:
            raise ValueError("Invalid RustDesk session count")
        return count

    def _exchange(self, request: dict) -> dict:
        payload = json.dumps(request, separators=(",", ":")).encode("utf-8")
        width = next(size for size in range(1, 5) if len(payload) < (1 << (8 * size - 2)))
        header = ((len(payload) << 2) | (width - 1)).to_bytes(width, "little")
        # RustDesk BytesCodec: low two bits encode header width minus one;
        # the remaining bits encode the payload length, little endian.
        deadline = time.monotonic() + self._timeout
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as connection:
            connection.settimeout(self._timeout)
            connection.connect(self._socket_path)
            connection.sendall(header + payload)
            first = self._read_exact(connection, 1, deadline)
            width = (first[0] & 3) + 1
            header = first + self._read_exact(connection, width - 1, deadline)
            length = int.from_bytes(header, "little") >> 2
            if not 0 < length <= 4096:
                raise ValueError("Invalid RustDesk IPC frame length")
            response = json.loads(self._read_exact(connection, length, deadline))
        return response

    @staticmethod
    def _read_exact(connection: socket.socket, length: int, deadline: float) -> bytes:
        result = bytearray()
        while len(result) < length:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError("RustDesk session query timed out")
            connection.settimeout(remaining)
            chunk = connection.recv(length - len(result))
            if not chunk:
                raise ValueError("Incomplete RustDesk IPC response")
            result.extend(chunk)
        return bytes(result)
