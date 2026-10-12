"""Uniform scale correction from a rectangular reference's known dimensions."""
from dataclasses import dataclass
import math


@dataclass(frozen=True)
class RectangleScaleCalibration:
    """Sizes are ordered short-side first, independent of rectangle rotation."""
    measured_size_mm: tuple[float, float]
    reference_size_mm: tuple[float, float]
    correction: float

    @property
    def corrected_size_mm(self) -> tuple[float, float]:
        return tuple(value * self.correction for value in self.measured_size_mm)

    @property
    def residual_mm(self) -> tuple[float, float]:
        return tuple(actual - expected for actual, expected in
                     zip(self.corrected_size_mm, self.reference_size_mm))

    @property
    def residual_percent(self) -> tuple[float, float]:
        return tuple(100.0 * error / expected for error, expected in
                     zip(self.residual_mm, self.reference_size_mm))


def calibrate_rectangle_scale(measured_size_mm, reference_size_mm) -> RectangleScaleCalibration:
    """Least-squares uniform correction; swapping rectangle axes changes nothing.

    Measure the raw minimum-area rectangle using the nominal mm/pixel scale.
    This corrects a uniform scale error, not perspective or unequal axis scales.
    Inspect residual_mm to assess whether both known sides agree after correction.
    """
    measured = tuple(sorted(float(value) for value in measured_size_mm))
    reference = tuple(sorted(float(value) for value in reference_size_mm))
    if len(measured) != 2 or len(reference) != 2:
        raise ValueError('Measured and reference sizes must each contain two dimensions')
    if any(not math.isfinite(value) or value <= 0 for value in measured + reference):
        raise ValueError('Reference and measured dimensions must be finite and positive')
    try:
        denominator = math.fsum(value * value for value in measured)
        numerator = math.fsum(actual * expected for actual, expected in zip(measured, reference))
        correction = numerator / denominator
    except (OverflowError, ZeroDivisionError) as error:
        raise ValueError('Dimensions are outside the supported numeric range') from error
    if not math.isfinite(correction) or correction <= 0:
        raise ValueError('Scale correction must be finite and positive')
    return RectangleScaleCalibration(measured, reference, correction)
