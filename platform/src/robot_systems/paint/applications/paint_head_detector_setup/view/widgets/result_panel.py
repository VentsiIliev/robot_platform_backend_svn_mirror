"""Reusable detector-result presentation for testing and inline draft tuning."""

from html import escape

from PyQt6.QtCore import QEvent, Qt
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QHeaderView,
    QLabel,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from pl_gui.settings.settings_view.styles import BG_COLOR, ERROR_COLOR, STATUS_OK, TEXT_COLOR
from src.robot_systems.paint.contracts.paint_head_calibration.models import CalibrationEvaluation
from src.robot_systems.paint.contracts.paint_head_check.models import (
    PaintHeadObservationReason,
    PaintHeadState,
)

from ..styles import CARD_STYLE, SECTION_TITLE_STYLE
from .forms import translate

_STATES = {
    PaintHeadState.PRESENT: "Head present",
    PaintHeadState.MISSING: "Head missing",
    PaintHeadState.MISALIGNED: "Head misaligned",
    PaintHeadState.UNKNOWN: "Unknown",
}
_REASONS = {
    PaintHeadObservationReason.ALIGNED: "Aligned",
    PaintHeadObservationReason.MISALIGNED: "Misaligned",
    PaintHeadObservationReason.EMPTY_MOUNT: "Empty mount",
    PaintHeadObservationReason.INSUFFICIENT_EVIDENCE: "Insufficient evidence",
    PaintHeadObservationReason.CONFLICTING_EVIDENCE: "Conflicting evidence",
    PaintHeadObservationReason.POSE_UNDETERMINED: "Pose undetermined",
    PaintHeadObservationReason.TOO_DARK: "Too dark",
    PaintHeadObservationReason.OVEREXPOSED: "Overexposed",
    PaintHeadObservationReason.LOW_CONTRAST: "Low contrast",
    PaintHeadObservationReason.CONFIRMING_STATUS: "Confirming status",
    PaintHeadObservationReason.RECHECKING_POSITION: "Rechecking position",
}


def state_text(state: PaintHeadState) -> str:
    return translate(_STATES[state])


def result_color(report: CalibrationEvaluation) -> str:
    return (
        STATUS_OK if report.state is PaintHeadState.PRESENT and report.image_usable else ERROR_COLOR
    )


class CalibrationResultPanel(QFrame):
    def __init__(self, *, compact: bool = False) -> None:
        super().__init__()
        self._compact = compact
        self._evaluation: CalibrationEvaluation | None = None
        self._unavailable: tuple[str, str] | None = None
        self.setObjectName("settingsCard")
        self.setStyleSheet(CARD_STYLE)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(6 if compact else 10)
        self._heading = QLabel()
        self._heading.setStyleSheet(SECTION_TITLE_STYLE)
        layout.addWidget(self._heading)
        self._status = QLabel()
        self._status.setObjectName(
            "calibrationSettingsResultStatus" if compact else "calibrationResultStatus"
        )
        self._status.setWordWrap(True)
        layout.addWidget(self._status)
        self._details = QLabel()
        self._details.setObjectName(
            "calibrationSettingsResultDetails" if compact else "calibrationResultDetails"
        )
        self._details.setWordWrap(True)
        layout.addWidget(self._details)
        self._evidence: QTableWidget | None = None
        self._evidence_heading: QLabel | None = None
        if compact:
            self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        else:
            self._evidence_heading = QLabel()
            self._evidence_heading.setStyleSheet(SECTION_TITLE_STYLE)
            layout.addWidget(self._evidence_heading)
            self._evidence = QTableWidget(0, 3)
            self._evidence.setObjectName("calibrationEvidenceTable")
            self._evidence.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
            self._evidence.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
            self._evidence.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
            self._evidence.horizontalHeader().setDefaultAlignment(
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
            )
            self._evidence.horizontalHeader().setSectionResizeMode(
                QHeaderView.ResizeMode.ResizeToContents
            )
            self._evidence.horizontalHeader().setSectionResizeMode(
                0, QHeaderView.ResizeMode.Stretch
            )
            self._evidence.verticalHeader().setDefaultSectionSize(44)
            self._evidence.verticalHeader().hide()
            self._evidence.setShowGrid(False)
            self._evidence.setAlternatingRowColors(True)
            layout.addWidget(self._evidence, 1)
        self.retranslateUi()

    def set_evaluation(self, report: CalibrationEvaluation) -> None:
        self._evaluation = report
        self._unavailable = None
        self._status.setText(state_text(report.state))
        self._status.setStyleSheet(
            f"color: {result_color(report)}; background: {BG_COLOR}; border-radius: 8px;"
            + (
                "padding: 6px 10px; font-size: 14pt; font-weight: bold;"
                if self._compact
                else "padding: 10px; font-size: 16pt; font-weight: bold;"
            )
        )

        def number(value: float | None, unit: str) -> str:
            return translate("Unavailable") if value is None else f"{value:.2f} {unit}"

        metrics = (
            (translate("Observed state"), state_text(report.observed_state)),
            (translate("Reason"), translate(_REASONS[report.reason])),
            (translate("Translation"), number(report.translation_pixels, "px")),
            (
                translate("X / Y offset"),
                number(report.offset_x_pixels, "px") + " / " + number(report.offset_y_pixels, "px"),
            ),
            (translate("Rotation"), number(report.rotation_degrees, "°")),
            (translate("Held warning"), translate("Yes" if report.held_warning else "No")),
            (translate("Image usable"), translate("Yes" if report.image_usable else "No")),
        )
        padding = 1 if self._compact else 3
        self._details.setTextFormat(Qt.TextFormat.RichText)
        self._details.setText(
            f'<table width="100%" cellspacing="0" cellpadding="{padding}">'
            + "".join(
                f"<tr><td>{escape(label)}</td><td><b>{escape(value)}</b></td></tr>"
                for label, value in metrics
            )
            + "</table>"
        )
        if self._evidence is not None:
            self._evidence.setRowCount(len(report.evidence))
            for row, evidence in enumerate(report.evidence):
                values = (
                    evidence.name,
                    f"{evidence.score:.3f}",
                    translate("Pass" if evidence.passed else "Fail"),
                )
                for column, value in enumerate(values):
                    item = QTableWidgetItem(value)
                    item.setToolTip(value)
                    self._evidence.setItem(row, column, item)

    def clear_evaluation(self) -> None:
        self._evaluation = None
        self._unavailable = None
        self._status.setText(translate("No current result"))
        self._status.setStyleSheet(f"color: {TEXT_COLOR};")
        self._details.clear()
        if self._evidence is not None:
            self._evidence.setRowCount(0)

    def show_unavailable(self, title: str, detail: str) -> None:
        """The view supplies a translated presentation title and raw failure detail."""
        self.clear_evaluation()
        self._unavailable = (title, detail)
        self._status.setText(title)
        self._status.setStyleSheet(f"color: {ERROR_COLOR}; font-weight: bold;")
        self._details.setText(detail)
        self._details.setTextFormat(Qt.TextFormat.PlainText)

    def retranslateUi(self) -> None:
        self._heading.setText(translate("Inspection result"))
        if self._evidence_heading is not None:
            self._evidence_heading.setText(translate("Matching evidence"))
        if self._evidence is not None:
            self._evidence.setHorizontalHeaderLabels(
                [translate(source) for source in ("Landmark", "Score", "Result")]
            )
        if self._evaluation is not None:
            self.set_evaluation(self._evaluation)
        elif self._unavailable is None:
            self.clear_evaluation()

    def changeEvent(self, event: QEvent) -> None:
        if event.type() == QEvent.Type.LanguageChange:
            self.retranslateUi()
        super().changeEvent(event)
