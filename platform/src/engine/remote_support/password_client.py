"""RustDesk password management without plaintext files or process arguments."""

from .session_client import RustDeskSessionClient


class RustDeskPasswordClient(RustDeskSessionClient):
    def _request(self, request: dict) -> dict:
        try:
            response = self._exchange(request)
        except (OSError, ValueError):
            raise RuntimeError("RustDesk password management is unavailable") from None
        if not isinstance(response, dict) or response.get("t") != request["t"]:
            raise RuntimeError("Unexpected RustDesk password-management response")
        return response

    def _config(self, name: str, value=None):
        response = self._request({"t": "Config", "c": [name, value]})
        content = response.get("c")
        if not isinstance(content, list) or len(content) != 2 or content[0] != name:
            raise RuntimeError("Invalid RustDesk password-management response")
        return content[1]

    def get_password_status(self) -> dict:
        configured = self._config("permanent-password-set")
        if configured not in ("Y", "N"):
            raise RuntimeError("RustDesk does not report permanent-password status")
        options = self._request({"t": "Options", "c": None}).get("c")
        if not isinstance(options, dict):
            raise RuntimeError("Invalid RustDesk authentication options")
        return {
            "configured": configured == "Y",
            "unattended_enabled": configured == "Y" and options.get("approve-mode", "password") == "password"
                and options.get("verification-method") != "use-temporary-password",
        }

    def _set_approval(self, unattended: bool) -> None:
        options = self._request({"t": "Options", "c": None}).get("c")
        if not isinstance(options, dict):
            raise RuntimeError("Invalid RustDesk authentication options")
        options.update({
            "approve-mode": "password" if unattended else "click",
            "verification-method": "use-permanent-password" if unattended else "use-temporary-password",
        })
        response = self._request({"t": "Options", "c": options})
        if response.get("c") is not None:
            raise RuntimeError("RustDesk did not confirm authentication options")
        confirmed = self._request({"t": "Options", "c": None}).get("c")
        if not isinstance(confirmed, dict) or any(confirmed.get(key) != options[key] for key in ("approve-mode", "verification-method")):
            raise RuntimeError("RustDesk authentication options did not take effect")

    def set_password(self, password: str) -> None:
        if self._config("permanent-password", password) != "Y":
            raise RuntimeError("RustDesk rejected the password change")
        self._set_approval(True)
        if not self.get_password_status()["unattended_enabled"]:
            raise RuntimeError("RustDesk did not confirm unattended access")

    def remove_password(self) -> None:
        # Switch to local approval first. A branded preset password can survive
        # clearing the local value; it must no longer grant unattended access.
        self._set_approval(False)
        if self._config("permanent-password", "") != "Y":
            raise RuntimeError("RustDesk rejected password removal")
        if self.get_password_status()["unattended_enabled"]:
            raise RuntimeError("RustDesk did not disable unattended access")
