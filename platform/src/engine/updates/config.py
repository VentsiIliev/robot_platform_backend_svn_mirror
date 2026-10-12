"""Machine-owned update configuration, never taken from a release archive."""
from dataclasses import dataclass
import json
import os
from pathlib import Path
from urllib.parse import urlparse


def default_config_path(product: str | None = None) -> Path:
    override = os.environ.get("ROBOT_PLATFORM_UPDATE_CONFIG")
    if override:
        return Path(override).expanduser()
    product = product or os.environ.get("ROBOT_PLATFORM_PRODUCT", "paint-robot")
    # Preserve the first paint install's configuration location.
    legacy = Path.home() / ".config/robot-platform/updates.json"
    if product == "paint-robot" and legacy.is_file():
        return legacy
    return Path.home() / ".config/robot-platform" / product / "updates.json"


def default_install_root(product: str) -> Path:
    base = Path.home() / ".local/share/robot-platform"
    if product == "paint-robot" and ((base / "current").exists() or (base / "data").is_dir()):
        return base
    return base / "products" / product


@dataclass(frozen=True)
class UpdateConfig:
    install_root: Path
    repository_url: str
    public_key: Path | None
    product: str = "paint-robot"
    channel: str = "stable"
    enabled: bool = False
    timeout_seconds: int = 30
    max_download_bytes: int = 4 * 1024 ** 3
    max_extracted_bytes: int = 8 * 1024 ** 3
    repository_type: str = 'feed'
    allow_insecure_http: bool = False
    token_file: Path | None = None
    api_url: str | None = None

    @property
    def local_repository(self) -> Path | None:
        return Path(self.repository_url) if self.repository_url.startswith("/") else None

    @classmethod
    def load(cls, path: Path | None = None):
        path = path or default_config_path()
        raw = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            raise ValueError("Update configuration must be an object")
        enabled = raw.get("enabled", False)
        if not isinstance(enabled, bool):
            raise ValueError("enabled must be a boolean")
        root = Path(raw["install_root"]).expanduser()
        if not root.is_absolute():
            raise ValueError("install_root must be absolute")
        repository = raw.get("repository_url", "")
        if not isinstance(repository, str):
            raise ValueError("repository_url must be a string")
        parsed = urlparse(repository)
        local = Path(repository).is_absolute()
        repository_type = raw.get('repository_type', 'feed')
        if repository_type not in ('feed', 'gitea', 'github', 'gitlab', 'svn'):
            raise ValueError('repository_type must be feed, gitea, github, gitlab or svn')
        if repository_type == 'github':
            from .github_source import repository_api
            repository_api(repository)
        api_url = raw.get('api_url')
        if api_url is not None and (not isinstance(api_url, str) or repository_type != 'gitlab'):
            raise ValueError('api_url is an optional GitLab API base URL')
        if repository_type == 'gitlab':
            from .gitlab_source import repository_api
            repository_api(repository, api_url)
        insecure = raw.get('allow_insecure_http', False)
        if not isinstance(insecure, bool):
            raise ValueError('allow_insecure_http must be a boolean')
        allowed_schemes = ('http', 'https') if insecure else ('https',)
        if enabled and not local and (
                parsed.scheme not in allowed_schemes or not parsed.netloc or parsed.username or parsed.password or parsed.query or parsed.fragment):
            raise ValueError(
                "Enabled updates require an absolute local folder or HTTPS repository_url without credentials/query")
        for name in ("product", "channel"):
            value = raw.get(name, "paint-robot" if name == "product" else "stable")
            if not isinstance(value, str) or not value or any(
                    c not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_" for c in value):
                raise ValueError(f"Invalid {name}")
        key_value = raw.get("public_key")
        if key_value is not None and not isinstance(key_value, str):
            raise ValueError("public_key must be a quoted file path or null")
        key = Path(key_value).expanduser() if key_value else None
        if key is not None and not key.is_absolute():
            raise ValueError("public_key must be absolute")
        token_value = raw.get('token_file')
        if token_value is not None and not isinstance(token_value, str):
            raise ValueError('token_file must be a quoted file path or null')
        token_file = Path(token_value).expanduser() if token_value else None
        if token_file is not None and (not token_file.is_absolute() or not token_file.is_file()):
            raise ValueError('token_file must point to an existing absolute file')
        if enabled and ((key is not None and not key.is_file()) or (not local and key is None and not insecure)):
            raise ValueError("Enabled updates require an installed public_key")
        limits = {}
        for name, default in (("timeout_seconds", 30), ("max_download_bytes", 4 * 1024 ** 3),
                              ("max_extracted_bytes", 8 * 1024 ** 3)):
            value = raw.get(name, default)
            if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
                raise ValueError(f"{name} must be a positive integer")
            limits[name] = value
        return cls(root.resolve(), repository.rstrip("/") + "/" if repository else "", key,
                   raw.get("product", "paint-robot"), raw.get("channel", "stable"), enabled,
                   repository_type=repository_type, allow_insecure_http=insecure,
                   token_file=token_file, api_url=api_url, **limits)
