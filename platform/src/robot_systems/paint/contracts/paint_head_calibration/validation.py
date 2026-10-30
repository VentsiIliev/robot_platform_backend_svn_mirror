"""Small value-invariant checks shared by immutable contract values."""

from math import isfinite

from .errors import CalibrationValidationError


def finite_number(value: object, label: str, *, minimum: float = 0.0) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise CalibrationValidationError(f"{label} must be numeric")
    try:
        valid = isfinite(value) and value >= minimum
    except OverflowError:
        valid = False
    if not valid:
        raise CalibrationValidationError(f"{label} must be finite and at least {minimum}")


def integer(value: object, label: str, *, minimum: int = 0) -> None:
    if type(value) is not int or value < minimum:
        raise CalibrationValidationError(f"{label} must be an integer at least {minimum}")


def text(value: object, label: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise CalibrationValidationError(f"{label} must be nonempty text")
