"""Read-only status for the boot-managed RustDesk service."""

import subprocess


class RustDeskServiceStatusClient:
    def __init__(self, timeout: float = 2) -> None:
        self._timeout = timeout

    def status(self) -> dict:
        try:
            result = subprocess.run(
                ["systemctl", "show", "rustdesk.service", "--property=LoadState",
                 "--property=ActiveState", "--property=UnitFileState"],
                capture_output=True, text=True, timeout=self._timeout, check=True,
            )
        except (OSError, subprocess.SubprocessError) as error:
            raise RuntimeError("Remote support service status is unavailable") from error
        fields = dict(line.split("=", 1) for line in result.stdout.splitlines() if "=" in line)
        if fields.get("LoadState") != "loaded":
            raise RuntimeError("Remote support service is not installed")
        return {"enabled": fields.get("UnitFileState") in ("enabled", "enabled-runtime"),
                "active": fields.get("ActiveState") == "active",
                "service_state": fields.get("ActiveState", "unknown")}
