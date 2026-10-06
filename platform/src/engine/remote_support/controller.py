"""Local, socket-activated controller for the system RustDesk unit.

Installed outside the application and run by systemd as root. The request
protocol deliberately has no command, unit-name, or path parameters.
"""

import json
import logging
import os
import socket
import subprocess
import time
import sys
import fcntl
import math
from pathlib import Path


UNIT = "rustdesk.service"
STATE_DIR = Path("/var/lib/plproject/remote-support")
ENABLE_MARKER = STATE_DIR / "enabled"
MAX_REQUEST_BYTES = 1024
ACCESS_DURATIONS = (900, 7200, 18000)
BOOT_ID_PATH = Path("/proc/sys/kernel/random/boot_id")
LOGGER = logging.getLogger("plproject.remote_support")


def _elapsed_time() -> float:
    # Linux boot time is monotonic and includes time spent suspended.
    return time.clock_gettime(time.CLOCK_BOOTTIME)


def _read_window() -> dict | None:
    try:
        window = json.loads(ENABLE_MARKER.read_text())
        if (not isinstance(window, dict) or window.get("boot_id") != BOOT_ID_PATH.read_text().strip()
                or type(window.get("duration_seconds")) is not int
                or window["duration_seconds"] not in ACCESS_DURATIONS
                or type(window.get("deadline_elapsed")) not in (int, float)
                or not math.isfinite(window["deadline_elapsed"])
                or type(window.get("expires_at")) not in (int, float)
                or not math.isfinite(window["expires_at"])):
            return None
        return window
    except (FileNotFoundError, ValueError, TypeError):
        return None


def _access_allowed() -> bool:
    window = _read_window()
    return window is not None and _elapsed_time() < window["deadline_elapsed"]


def _write_json(path: Path, value: dict) -> None:
    temporary = path.with_name("." + path.name + "-new")
    with temporary.open("w", encoding="utf-8") as stream:
        os.fchmod(stream.fileno(), 0o600)
        json.dump(value, stream)
        stream.flush()
        os.fsync(stream.fileno())
    temporary.replace(path)
    _sync_state_directory()


def _expire_if_needed() -> None:
    if (STATE_DIR / "stop_pending").is_file() or (ENABLE_MARKER.is_file() and not _access_allowed()):
        LOGGER.info("Remote support access expired; stopping service")
        _set_enabled(False)


def _sync_state_directory() -> None:
    descriptor = os.open(STATE_DIR, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _systemctl(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["/usr/bin/systemctl", *args, UNIT],
        capture_output=True, text=True, timeout=30, check=False,
    )


def _status() -> dict:
    result = _systemctl("show", "--property=LoadState,ActiveState", "--no-pager")
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "Cannot read RustDesk service state")
    values = dict(
        line.split("=", 1) for line in result.stdout.splitlines() if "=" in line
    )
    if values.get("LoadState") != "loaded":
        raise RuntimeError("RustDesk system service is not installed")
    active_state = values.get("ActiveState", "unknown")
    window = _read_window()
    remaining = max(0, math.ceil(window["deadline_elapsed"] - _elapsed_time())) if window else 0
    return {
        "enabled": ENABLE_MARKER.is_file(),
        "active": active_state == "active",
        "service_state": active_state,
        "timed_access_supported": True,
        "remaining_seconds": remaining,
        "expires_at": window["expires_at"] if window else None,
        "duration_seconds": window["duration_seconds"] if window else 900,
    }


def _set_enabled(enabled: bool, duration_seconds: int = 900) -> dict:
    if type(duration_seconds) is not int or duration_seconds not in ACCESS_DURATIONS:
        raise ValueError("Unsupported remote support duration")
    STATE_DIR.mkdir(mode=0o700, parents=True, exist_ok=True)
    if enabled:
        _status()  # Do not persist ON for a missing or masked unit.
        # The marker gates service startup through ConditionPathExists.
        if ENABLE_MARKER.is_file() and _access_allowed():
            # Retrying ON must not silently restart or extend the window.
            return _status()
        _write_json(ENABLE_MARKER, {
            "boot_id": BOOT_ID_PATH.read_text().strip(),
            "duration_seconds": duration_seconds,
            "deadline_elapsed": _elapsed_time() + duration_seconds,
            "expires_at": time.time() + duration_seconds,
        })
        # Enable at boot as well as starting now. OFF remains gated by the
        # systemd condition even when the unit is enabled.
        try:
            result = _systemctl("enable", "--now")
            status = _status()
            if result.returncode or not status["active"]:
                raise RuntimeError(result.stderr.strip() or "RustDesk service did not start")
            # Type=simple reports started before RustDesk has initialized.
            # Catch immediate shutdowns such as its own stop-service setting.
            time.sleep(1)
            status = _status()
            if not status["active"]:
                raise RuntimeError("RustDesk stopped during startup; check its service settings and logs")
            return status
        except (OSError, subprocess.SubprocessError, RuntimeError):
            (STATE_DIR / "stop_pending").touch(mode=0o600)
            ENABLE_MARKER.unlink(missing_ok=True)
            _sync_state_directory()
            try:
                _systemctl("stop")
            except (OSError, subprocess.SubprocessError):
                pass
            raise
    else:
        # Remove the startup permission before stopping a running session.
        (STATE_DIR / "stop_pending").touch(mode=0o600)
        ENABLE_MARKER.unlink(missing_ok=True)
        _sync_state_directory()
        result = _systemctl("stop")
    status = _status()
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "Could not change RustDesk service")
    if status["active"] != enabled:
        raise RuntimeError("RustDesk service did not reach the requested state")
    (STATE_DIR / "stop_pending").unlink(missing_ok=True)
    _sync_state_directory()
    return status


def handle_request(request: dict) -> dict:
    if not isinstance(request, dict):
        raise ValueError("Invalid remote support request")
    operation = request.get("operation")
    allowed_keys = {"operation", "duration_seconds"} if operation == "enable" else {"operation"}
    if set(request) not in ({"operation"}, allowed_keys):
        raise ValueError("Invalid remote support request")
    if operation == "status":
        return _status()
    if operation == "enable":
        LOGGER.info("Remote support enable requested")
        status = _set_enabled(True, request.get("duration_seconds", 900))
        LOGGER.info("Remote support enable completed: %s", status)
        return status
    if operation == "disable":
        LOGGER.info("Remote support disable requested")
        status = _set_enabled(False)
        LOGGER.info("Remote support disable completed: %s", status)
        return status
    raise ValueError("Unknown remote support operation")


def _serve_connection(connection: socket.socket) -> None:
    # A stalled local client must not block every subsequent status request.
    connection.settimeout(5)
    try:
        request_bytes = bytearray()
        while len(request_bytes) <= MAX_REQUEST_BYTES:
            chunk = connection.recv(1)
            if not chunk or chunk == b"\n":
                break
            request_bytes.extend(chunk)
        if not request_bytes or len(request_bytes) > MAX_REQUEST_BYTES:
            raise ValueError("Invalid remote support request size")
        STATE_DIR.mkdir(mode=0o700, parents=True, exist_ok=True)
        with (STATE_DIR / "controller.lock").open("a") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            _expire_if_needed()
            result = {"ok": True, "status": handle_request(json.loads(request_bytes))}
    except (ValueError, OSError, subprocess.SubprocessError, RuntimeError) as exc:
        LOGGER.error("Remote support request failed: %s", exc)
        result = {"ok": False, "error": str(exc)}
    try:
        connection.sendall(json.dumps(result).encode("utf-8") + b"\n")
    except OSError:
        # A disconnected client must not terminate the root controller.
        pass


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(name)s: %(levelname)s: %(message)s")
    if sys.argv[1:] == ["--check-access"]:
        raise SystemExit(0 if _access_allowed() else 1)
    if sys.argv[1:] == ["--expire"] and os.geteuid() == 0:
        STATE_DIR.mkdir(mode=0o700, parents=True, exist_ok=True)
        with (STATE_DIR / "controller.lock").open("a") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            _expire_if_needed()
        return
    if sys.argv[1:] or os.geteuid() != 0 or os.environ.get("LISTEN_PID") != str(os.getpid()) or os.environ.get("LISTEN_FDS") != "1":
        raise SystemExit("Run via plproject-remote-support.socket as root")
    with socket.socket(fileno=3) as listener:
        listener.settimeout(1)
        while True:
            try:
                with (STATE_DIR / "controller.lock").open("a") as lock:
                    fcntl.flock(lock, fcntl.LOCK_EX)
                    _expire_if_needed()
                connection, _ = listener.accept()
            except socket.timeout:
                continue
            except (OSError, subprocess.SubprocessError, RuntimeError):
                LOGGER.error("Remote support expiry check failed; will retry")
                time.sleep(1)
                continue
            with connection:
                _serve_connection(connection)


if __name__ == "__main__":
    main()
