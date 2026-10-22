"""Validated endpoint configuration shared with the backend through one JSON file."""
from dataclasses import dataclass
from ipaddress import ip_address
import json
import os
from pathlib import Path


CONFIG_ENV = "ROBOT_BACKEND_NETWORK_CONFIG"


def network_config_path() -> Path:
    explicit = os.environ.get(CONFIG_ENV)
    if explicit is not None:
        path = Path(explicit)
        if not explicit or not path.is_absolute():
            raise ValueError(f"{CONFIG_ENV} must be an absolute file path")
        return path
    # Source checkout: use the platform-owned file, never a second set of values.
    for parent in Path(__file__).resolve().parents:
        candidate = parent / "platform/config/backend_network.json"
        if candidate.is_file():
            return candidate
    raise ValueError(f"Set {CONFIG_ENV} to the shared backend_network.json absolute path")


@dataclass(frozen=True)
class BackendNetwork:
    bind_host: str
    client_host: str
    http_port: int
    state_ws_port: int
    execution_ws_port: int
    sensor_ws_port: int

    @property
    def http_url(self) -> str:
        host = f"[{self.client_host}]" if ':' in self.client_host else self.client_host
        return f"http://{host}:{self.http_port}"


def load_backend_network(path: Path | None = None) -> BackendNetwork:
    path = path or network_config_path()
    payload = json.loads(path.read_text(encoding="utf-8"))
    required = set(BackendNetwork.__dataclass_fields__)
    if not isinstance(payload, dict) or set(payload) != required:
        raise ValueError(f"{path}: expected exactly {sorted(required)}")
    for key in ("bind_host", "client_host"):
        value = payload[key]
        if not isinstance(value, str) or value != value.strip():
            raise ValueError(f"{path}: {key} must be an IP address")
        address = ip_address(value)
        if key == "client_host" and address.is_unspecified:
            raise ValueError(f"{path}: client_host cannot be a wildcard address")
        if address.is_multicast:
            raise ValueError(f"{path}: {key} cannot be multicast")
    ports = [payload[key] for key in required if key.endswith('_port')]
    if any(type(port) is not int or not 1 <= port <= 65535 for port in ports):
        raise ValueError(f"{path}: ports must be integers in 1..65535")
    if len(set(ports)) != len(ports):
        raise ValueError(f"{path}: each endpoint needs a distinct port")
    return BackendNetwork(**payload)
