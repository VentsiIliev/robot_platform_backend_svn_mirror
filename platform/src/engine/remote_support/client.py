"""Unprivileged client for the local PL PROJECT remote support controller."""

import json
import socket
import time


SOCKET_PATH = "/run/plproject/remote-support.sock"
MAX_RESPONSE_BYTES = 4096


class RemoteSupportClient:
    def __init__(self, socket_path: str = SOCKET_PATH, timeout: float = 100) -> None:
        self._socket_path = socket_path
        self._timeout = timeout

    def status(self) -> dict:
        return self._request("status")

    def set_enabled(self, enabled: bool, duration_seconds: int | None = None) -> dict:
        fields = {"duration_seconds": duration_seconds} if enabled and duration_seconds is not None else {}
        return self._request("enable" if enabled else "disable", **fields)

    def _request(self, operation: str, **fields) -> dict:
        deadline = time.monotonic() + self._timeout
        try:
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as connection:
                connection.settimeout(self._timeout)
                connection.connect(self._socket_path)
                connection.sendall(json.dumps({"operation": operation, **fields}).encode("utf-8") + b"\n")
                response = bytearray()
                while len(response) <= MAX_RESPONSE_BYTES:
                    remaining = deadline - time.monotonic()
                    if remaining <= 0:
                        raise TimeoutError("Remote support request timed out")
                    connection.settimeout(remaining)
                    chunk = connection.recv(1)
                    if not chunk or chunk == b"\n":
                        break
                    response.extend(chunk)
        except FileNotFoundError as exc:
            raise RuntimeError("Remote support controller is not installed") from exc
        except (OSError, TimeoutError) as exc:
            raise RuntimeError(f"Remote support controller is unavailable: {exc}") from exc
        if not response or len(response) > MAX_RESPONSE_BYTES:
            raise RuntimeError("Invalid remote support controller response")
        try:
            result = json.loads(response)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise RuntimeError("Invalid remote support controller response") from exc
        if not isinstance(result, dict) or not isinstance(result.get("ok"), bool):
            raise RuntimeError("Invalid remote support controller response")
        if not result["ok"]:
            raise RuntimeError(str(result.get("error") or "Remote support operation failed"))
        status = result.get("status")
        if not isinstance(status, dict) or not isinstance(status.get("enabled"), bool) or not isinstance(status.get("active"), bool):
            raise RuntimeError("Invalid remote support controller status")
        return status
