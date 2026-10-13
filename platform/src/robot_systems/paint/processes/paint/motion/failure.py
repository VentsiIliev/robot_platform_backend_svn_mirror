"""Backend motion failure details shared by operations and workflow."""

def motion_failure_message(robot_service, fallback: str) -> str:
    """Return the latest backend command error without hiding it behind a result code."""
    getter = getattr(robot_service, "get_last_trajectory_command_info", None)
    if callable(getter):
        try:
            info = getter() or {}
        except Exception:
            info = {}
        raw = info.get("raw") if isinstance(info, dict) else None
        if isinstance(raw, dict):
            detail = raw.get("error") or raw.get("message")
            if detail:
                return str(detail)

    details_getter = getattr(robot_service, "get_connection_details", None)
    if callable(details_getter):
        try:
            details = details_getter() or {}
        except Exception:
            details = {}
        if isinstance(details, dict):
            detail = details.get("last_command_error") or details.get("last_error")
            if detail:
                return str(detail)

    return str(fallback)
