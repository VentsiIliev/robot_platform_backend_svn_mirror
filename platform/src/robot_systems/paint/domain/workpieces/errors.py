"""Workpiece persistence failures shared by repository and service boundaries."""


class WorkpieceReadError(OSError):
    """A persisted workpiece could not be read for production matching."""
