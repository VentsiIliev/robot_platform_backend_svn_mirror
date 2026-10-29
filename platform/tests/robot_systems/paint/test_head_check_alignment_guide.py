"""A schematic guide preserves correction direction and hides detector geometry."""

import unittest
from dataclasses import fields, replace
from math import nan, sqrt

from PyQt6.QtCore import QEvent, QRectF, Qt
from PyQt6.QtWidgets import QApplication

from pl_gui.settings.settings_view.styles import STATUS_OK, PRIMARY, ERROR_COLOR
from src.robot_systems.paint.applications.dashboard.head_alignment_presentation import (
    GuidePoint,
    GuideAvailability,
    GuideRotation,
    HeadAlignmentGuideData,
    build_head_alignment_guide,
    unavailable_head_alignment_guide,
)
from src.robot_systems.paint.applications.dashboard.ui.head_alignment_guide import (
    PaintHeadAlignmentGuide,
    PaintHeadGuideAssetError,
)
from src.robot_systems.paint.contracts.paint_head_check.guidance import (
    HeadCorrectionDirection,
    HeadRotationCorrection,
    PaintHeadCorrection,
)


def correction() -> PaintHeadCorrection:
    return PaintHeadCorrection(
        image_width=1000,
        image_height=1000,
        translation_direction=HeadCorrectionDirection(-0.6, 0.8),
        rotation_direction=HeadRotationCorrection.CLOCKWISE,
        translation_extent=1.0,
        rotation_extent=1.0,
    )


class HeadAlignmentPresentationTests(unittest.TestCase):
    def test_correction_directions_survive_the_presentation_boundary(self) -> None:
        guide = build_head_alignment_guide(correction())
        self.assertEqual(GuidePoint(-0.6, 0.8), guide.translation_direction)
        self.assertIs(GuideRotation.CLOCKWISE, guide.rotation_direction)
        self.assertFalse(guide.aligned)
        reverse = build_head_alignment_guide(
            replace(
                correction(),
                rotation_direction=HeadRotationCorrection.COUNTERCLOCKWISE,
            )
        )
        self.assertIs(GuideRotation.COUNTERCLOCKWISE, reverse.rotation_direction)

    def test_aligned_feedback_requires_confirmed_presence_and_no_corrections(self) -> None:
        within_tolerance = replace(
            correction(), translation_direction=None, rotation_direction=HeadRotationCorrection.NONE
        )
        self.assertFalse(build_head_alignment_guide(within_tolerance).aligned)
        self.assertTrue(
            build_head_alignment_guide(within_tolerance, confirmed_present=True).aligned
        )
        self.assertFalse(build_head_alignment_guide(correction(), confirmed_present=True).aligned)

    def test_contract_exposes_only_frame_compatibility_and_correction_directions(self) -> None:
        self.assertEqual(
            {
                "image_width",
                "image_height",
                "translation_direction",
                "rotation_direction",
                "translation_extent",
                "rotation_extent",
            },
            {field.name for field in fields(PaintHeadCorrection)},
        )
        self.assertEqual(
            {
                "translation_direction",
                "rotation_direction",
                "aligned",
                "availability",
                "show_head_reference",
                "translation_extent",
                "rotation_extent",
            },
            {field.name for field in fields(HeadAlignmentGuideData)},
        )

    def test_invalid_direction_never_produces_a_correction_arrow(self) -> None:
        for invalid in (
            replace(correction(), image_width=0),
            replace(correction(), translation_extent=nan),
            replace(correction(), rotation_extent=1.1),
            replace(correction(), translation_direction=HeadCorrectionDirection(nan, 1)),
            replace(correction(), translation_direction=HeadCorrectionDirection(0, 0)),
        ):
            with self.subTest(invalid=invalid):
                self.assertIsNone(build_head_alignment_guide(invalid))

    def test_image_aspect_is_resolved_before_the_camera_independent_card(self) -> None:
        guide = build_head_alignment_guide(replace(
            correction(), image_width=2000, image_height=1000,
            translation_direction=HeadCorrectionDirection(-1 / sqrt(2), 1 / sqrt(2)),
        ))
        self.assertAlmostEqual(-2 / sqrt(5), guide.translation_direction.x)
        self.assertAlmostEqual(1 / sqrt(5), guide.translation_direction.y)


class PaintHeadAlignmentGuideTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication([])

    def guide(self) -> PaintHeadAlignmentGuide:
        widget = PaintHeadAlignmentGuide()
        widget.resize(320, 440)
        widget.show()
        self.addCleanup(widget.close)
        return widget

    def test_illustrated_card_resizes_without_using_camera_coordinates(self) -> None:
        widget = self.guide()
        widget.set_guide(build_head_alignment_guide(correction()))
        widget.resize(320, 500)
        self.app.processEvents()
        self.assertEqual(QRectF(0, 30, 320, 440), widget.card_rectangle())
        self.assertFalse(widget.testAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents))
        widget.resize(260, 400)
        self.app.processEvents()
        self.assertEqual(QRectF(0, 21.25, 260, 357.5), widget.card_rectangle())
        widget.set_guide(None)
        self.assertTrue(widget.isHidden())

    def test_missing_reference_artwork_fails_with_a_typed_error(self) -> None:
        from pathlib import Path
        from unittest.mock import patch

        with patch(
            "src.robot_systems.paint.applications.dashboard.ui.head_alignment_guide._ARTWORK_PATH",
            Path("/tmp/nonexistent-paint-guide-artwork.png"),
        ):
            with self.assertRaises(PaintHeadGuideAssetError):
                self.guide()

    def test_reference_head_is_visible_below_the_target_and_stays_fixed_during_adjustment(
        self,
    ) -> None:
        widget = self.guide()
        active = build_head_alignment_guide(correction())
        widget.set_guide(active)
        self.app.processEvents()
        before = widget.grab().toImage()
        # The upper part of the static illustration is independent of live marker updates.
        head_top = before.copy(65, 145, 40, 30)
        self.assertTrue(
            any(
                head_top.pixelColor(x, y).lightness() < 60
                for y in range(head_top.height())
                for x in range(head_top.width())
            )
        )
        widget.set_guide(
            replace(
                active, translation_extent=0.1, rotation_direction=GuideRotation.COUNTERCLOCKWISE
            )
        )
        self.app.processEvents()
        self.assertEqual(head_top, widget.grab().toImage().copy(65, 145, 40, 30))

    def test_confirmed_aligned_result_has_a_green_centred_marker(self) -> None:
        widget = self.guide()
        aligned = replace(
            correction(), translation_direction=None, rotation_direction=HeadRotationCorrection.NONE
        )
        widget.set_guide(build_head_alignment_guide(aligned, confirmed_present=True))
        self.app.processEvents()
        marker = widget.grab().toImage().pixelColor(104, 318)
        self.assertGreater(marker.green(), marker.red() + 30)

    def test_unavailable_feedback_retains_only_a_grey_historical_marker(self) -> None:
        active = build_head_alignment_guide(correction())
        disabled = unavailable_head_alignment_guide(active)
        self.assertIs(GuideAvailability.UNAVAILABLE, disabled.availability)
        self.assertFalse(disabled.aligned)
        self.assertEqual(active.translation_direction, disabled.translation_direction)
        self.assertEqual(active.translation_extent, disabled.translation_extent)
        widget = self.guide()
        widget.set_guide(disabled)
        self.app.processEvents()
        image = widget.grab().toImage()
        actionable = {STATUS_OK.lower(), PRIMARY.lower(), ERROR_COLOR.lower()}
        for y in range(min(440, image.height())):
            for x in range(image.width()):
                self.assertNotIn(image.pixelColor(x, y).name(), actionable)
        self.assertFalse(widget.isHidden())

    def test_unavailable_feedback_cannot_retain_a_green_aligned_state(self) -> None:
        active = build_head_alignment_guide(
            replace(
                correction(),
                translation_direction=None,
                rotation_direction=HeadRotationCorrection.NONE,
            ),
            confirmed_present=True,
        )
        self.assertTrue(active.aligned)
        disabled = unavailable_head_alignment_guide(active)
        self.assertFalse(disabled.aligned)
        self.assertIs(GuideAvailability.UNAVAILABLE, disabled.availability)
        neutral = unavailable_head_alignment_guide(None)
        self.assertIsNone(neutral.translation_direction)
        self.assertFalse(neutral.aligned)

    def test_missing_hides_the_reference_image_while_keeping_the_card_disabled(self) -> None:
        widget = self.guide()
        unknown = unavailable_head_alignment_guide(None)
        widget.set_guide(unknown)
        self.app.processEvents()
        with_head = widget.grab().toImage()
        missing = unavailable_head_alignment_guide(None, show_head_reference=False)
        widget.set_guide(missing)
        self.app.processEvents()
        no_head = widget.grab().toImage()
        self.assertFalse(missing.show_head_reference)
        self.assertIs(GuideAvailability.UNAVAILABLE, missing.availability)
        self.assertFalse(widget.isHidden())
        # No target/marker in this upper artwork region: only the illustration changes.
        self.assertGreater(
            no_head.pixelColor(102, 170).lightness(),
            with_head.pixelColor(102, 170).lightness() + 20,
        )

    def test_card_translates_initial_bulgarian_and_runtime_language_without_new_feedback(
        self,
    ) -> None:
        from tests.robot_systems.paint.test_head_check_settings_ui import CatalogTranslator

        translator = CatalogTranslator("bg")
        self.app.installTranslator(translator)
        widget = self.guide()
        widget.set_guide(unavailable_head_alignment_guide(None))
        self.app.processEvents()
        initial_bulgarian = widget.grab().toImage()
        try:
            self.app.removeTranslator(translator)
            QApplication.sendEvent(widget, QEvent(QEvent.Type.LanguageChange))
            self.app.processEvents()
            english = widget.grab().toImage()
            self.assertNotEqual(initial_bulgarian, english)
            self.app.installTranslator(translator)
            QApplication.sendEvent(widget, QEvent(QEvent.Type.LanguageChange))
            self.app.processEvents()
            self.assertEqual(initial_bulgarian, widget.grab().toImage())
        finally:
            self.app.removeTranslator(translator)


if __name__ == "__main__":
    unittest.main()
