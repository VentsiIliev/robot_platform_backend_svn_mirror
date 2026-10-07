"""Actionable tray failures shared by production and dashboard boundaries."""

from dataclasses import dataclass
from enum import StrEnum


class TrayErrorCode(StrEnum):
    CONFIRMATION_REQUIRED = "tray_confirmation_required"
    BUSY = "tray_busy"
    LAYOUT_CHANGED = "tray_layout_changed"
    UNAVAILABLE = "tray_unavailable"


@dataclass(frozen=True)
class TrayFailure:
    code: TrayErrorCode
    message: str


class TrayError(RuntimeError):
    code: TrayErrorCode

    def as_failure(self) -> TrayFailure:
        return TrayFailure(self.code, str(self))


class TrayConfirmationRequiredError(TrayError):
    code = TrayErrorCode.CONFIRMATION_REQUIRED

    def __init__(self) -> None:
        super().__init__("Confirm that the tray is physically empty before starting.")


class TrayBusyError(TrayError):
    code = TrayErrorCode.BUSY

    def __init__(self) -> None:
        super().__init__("Wait for the paint process to stop before confirming an empty tray.")


class TrayLayoutChangedError(TrayError):
    code = TrayErrorCode.LAYOUT_CHANGED

    def __init__(self) -> None:
        super().__init__("Tray layout settings changed. Empty the physical tray and confirm a new tray before starting.")


class TrayUnavailableError(TrayError):
    code = TrayErrorCode.UNAVAILABLE

    def __init__(self) -> None:
        super().__init__("Tray layout is not available.")
