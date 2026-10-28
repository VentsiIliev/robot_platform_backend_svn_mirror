from dataclasses import dataclass


@dataclass(frozen=True)
class ApplicationAccess:
    app_id: str
    default_roles: frozenset[str] = frozenset({"Admin"})
    protected_roles: frozenset[str] = frozenset()
    denied_roles: frozenset[str] = frozenset()

    def __post_init__(self):
        for name in ("default_roles", "protected_roles", "denied_roles"):
            object.__setattr__(self, name, frozenset(getattr(self, name)))
        if not self.app_id or self.protected_roles & self.denied_roles:
            raise ValueError("Application access requires an ID and consistent role restrictions")
