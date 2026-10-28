from dataclasses import dataclass


@dataclass(frozen=True)
class ApplicationGrant:
    app_id: str
    roles: tuple[str, ...]
    editable_roles: tuple[str, ...] = ()


@dataclass(frozen=True)
class PermissionSnapshot:
    revision: int
    grants: tuple[ApplicationGrant, ...]


@dataclass(frozen=True)
class UpdateAppPermissions:
    app_id: str
    roles: tuple[str, ...]
    expected_revision: int
