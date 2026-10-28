"""Host-root authority for the trusted, installed maintenance command."""
import os
import pwd
from uuid import uuid4

from src.engine.auth.i_maintenance_authority import IMaintenanceAuthority
from src.shared_contracts.accounts.maintenance import OperatingSystemActor
from src.shared_contracts.authorization.errors import ErrorCode, ServiceError, ServiceUnavailableError
from src.shared_contracts.authorization.results import Failure, Success


class UnixMaintenanceAuthority(IMaintenanceAuthority):
    def current_actor(self):
        uid = os.geteuid()
        if uid != 0:
            return Failure(ServiceError(ErrorCode.ACCESS_DENIED, "maintenance.os_authority_required", uuid4().hex))
        try:
            effective = pwd.getpwuid(uid).pw_name
        except (KeyError, OSError) as exc:
            raise ServiceUnavailableError() from exc
        sudo_uid, sudo_username = None, None
        # These describe the root process's environment, not an independent
        # identity proof. Host sudo/journal records remain the authoritative trail.
        candidate = os.environ.get("SUDO_UID", "")
        if candidate.isdecimal():
            try:
                candidate_uid = int(candidate)
                candidate_name = pwd.getpwuid(candidate_uid).pw_name
                if candidate_name == os.environ.get("SUDO_USER"):
                    sudo_uid, sudo_username = candidate_uid, candidate_name
            except (KeyError, ValueError, OverflowError, OSError):
                pass
        return Success(OperatingSystemActor(uid, effective, sudo_uid, sudo_username))
