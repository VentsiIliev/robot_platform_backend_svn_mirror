"""Image-space selection, dragging and resizing; no detection or persistence logic."""

from collections.abc import Callable
from math import floor

from PyQt6.QtCore import QPointF, QRectF, Qt, pyqtSignal
from PyQt6.QtGui import QBrush, QColor, QImage, QMouseEvent, QPainter, QPen, QPixmap, QResizeEvent
from PyQt6.QtWidgets import (
    QGraphicsItem,
    QGraphicsPixmapItem,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsSceneMouseEvent,
    QGraphicsView,
    QLabel,
    QStyleOptionGraphicsItem,
    QWidget,
)

from pl_gui.settings.settings_view.styles import (
    BG_COLOR,
    BORDER,
    ERROR_COLOR,
    PRIMARY,
    STATUS_OK,
)
from src.robot_systems.paint.contracts.paint_head_calibration.models import (
    ImagePixels,
    ImageSize,
    LandmarkEvidence,
    LandmarkRole,
    LandmarkSupport,
    Region,
)

from ...editor_contracts import EditorKind, EditorObject, EditorTarget, EditorTool, GeometryEdit

_COLORS = {
    EditorKind.INSPECTION: STATUS_OK,
    EditorKind.EMPTY_MOUNT: PRIMARY,
    EditorKind.EXCLUDED: ERROR_COLOR,
    EditorKind.LANDMARK: PRIMARY,
}
_TOOLS = {
    EditorTool.INSPECTION: EditorKind.INSPECTION,
    EditorTool.EMPTY_MOUNT: EditorKind.EMPTY_MOUNT,
    EditorTool.EXCLUDED: EditorKind.EXCLUDED,
    EditorTool.RECTANGLE_LANDMARK: EditorKind.LANDMARK,
    EditorTool.CIRCLE_LANDMARK: EditorKind.LANDMARK,
}


class _RegionItem(QGraphicsRectItem):
    def __init__(
        self,
        item: EditorObject,
        bounds: ImageSize,
        notify: Callable[[GeometryEdit], None],
    ) -> None:
        super().__init__(0, 0, item.region.width, item.region.height)
        self._object = item
        self._bounds = bounds
        self._notify = notify
        self._resizing = False
        self.setPos(item.region.x, item.region.y)
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable
            | QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
        )
        self.setZValue(20 if item.target.kind is EditorKind.LANDMARK else 10)
        self.setToolTip(item.name)
        color = _COLORS[item.target.kind]
        if item.role is LandmarkRole.PRESENT:
            color = STATUS_OK
        self._color = QColor(color)

    @property
    def target(self) -> EditorTarget:
        return self._object.target

    def paint(
        self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget | None = None
    ) -> None:
        pen = QPen(self._color, 2)
        pen.setCosmetic(True)
        if self._object.target.kind is EditorKind.EXCLUDED:
            pen.setStyle(Qt.PenStyle.DashLine)
        painter.setPen(pen)
        fill = QColor(self._color)
        fill.setAlpha(25)
        painter.setBrush(QBrush(fill))
        if self._object.support is LandmarkSupport.CIRCLE:
            painter.drawEllipse(self.rect())
        else:
            painter.drawRect(self.rect())
        if self.isSelected():
            scale = max(0.01, abs(painter.worldTransform().m11()))
            size = 10 / scale
            painter.setBrush(QColor(BG_COLOR))
            painter.drawRect(
                QRectF(self.rect().right() - size / 2, self.rect().bottom() - size / 2, size, size)
            )

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        scale = (
            max(0.01, abs(self.scene().views()[0].transform().m11()))
            if self.scene() and self.scene().views()
            else 1
        )
        point = event.pos()
        self._resizing = (
            abs(point.x() - self.rect().right()) <= 14 / scale
            and abs(point.y() - self.rect().bottom()) <= 14 / scale
        )
        if self._resizing:
            self.setSelected(True)
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        if self._resizing:
            width = min(max(2.0, event.pos().x()), max(2.0, self._bounds.width - self.pos().x()))
            height = min(max(2.0, event.pos().y()), max(2.0, self._bounds.height - self.pos().y()))
            self.setRect(0, 0, width, height)
            event.accept()
        else:
            super().mouseMoveEvent(event)
            self.setPos(
                max(0.0, min(self.pos().x(), self._bounds.width - self.rect().width())),
                max(0.0, min(self.pos().y(), self._bounds.height - self.rect().height())),
            )

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        if not self._resizing:
            super().mouseReleaseEvent(event)
        self._resizing = False
        region = Region(
            max(0, floor(self.pos().x())),
            max(0, floor(self.pos().y())),
            max(2, floor(self.rect().width())),
            max(2, floor(self.rect().height())),
        )
        if region != self._object.region:
            self._notify(
                GeometryEdit(
                    self.target,
                    region,
                    self._object.support,
                    self._object.role or LandmarkRole.PRESENT,
                )
            )


class CalibrationCanvas(QGraphicsView):
    geometry_edited = pyqtSignal(object)
    object_selected = pyqtSignal(object)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("paintHeadCalibrationCanvas")
        self.setMinimumSize(260, 220)
        self.setStyleSheet(
            f"QGraphicsView {{ background: {BG_COLOR}; border: 1px solid {BORDER}; }}"
        )
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)
        self._pixmap = QGraphicsPixmapItem()
        self._scene.addItem(self._pixmap)
        self._size: ImageSize | None = None
        self._objects: list[_RegionItem] = []
        self._diagnostics: list[QGraphicsRectItem] = []
        self._result_badge = QLabel(self.viewport())
        self._result_badge.setObjectName("calibrationImageResult")
        self._result_badge.move(12, 12)
        self._result_badge.hide()
        self._result_badge.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self._tool = EditorTool.SELECT
        self._role = LandmarkRole.PRESENT
        self._drawing: QGraphicsRectItem | None = None
        self._origin: QPointF | None = None
        self._fitting = True
        self._updating = False
        self._scene.selectionChanged.connect(self._on_selection_changed)

    @property
    def image_size(self) -> ImageSize | None:
        return self._size

    def set_image(self, pixels: ImagePixels) -> None:
        changed = self._size != pixels.size
        self._size = pixels.size
        image = QImage(
            pixels.bgr,
            pixels.size.width,
            pixels.size.height,
            pixels.size.width * 3,
            QImage.Format.Format_BGR888,
        ).copy()
        self._pixmap.setPixmap(QPixmap.fromImage(image))
        self._scene.setSceneRect(0, 0, pixels.size.width, pixels.size.height)
        if changed or self._fitting:
            self.fit_image()

    def set_result_overlay(
        self, text: str, color: str, evidence: tuple[LandmarkEvidence, ...] = ()
    ) -> None:
        """Draw diagnostics supplied by the view; never run or interpret detection."""
        self.clear_result_overlay()
        self._result_badge.setText(text)
        self._result_badge.setStyleSheet(
            f"background: {BG_COLOR}; color: {color}; border: 2px solid {color};"
            "border-radius: 6px; padding: 8px; font-size: 12pt; font-weight: bold;"
        )
        self._result_badge.adjustSize()
        self._result_badge.show()
        self._result_badge.raise_()
        for match in evidence:
            region = match.reference_region
            item = QGraphicsRectItem(
                region.x + (match.shift_x if match.passed else 0),
                region.y + (match.shift_y if match.passed else 0),
                region.width,
                region.height,
            )
            pen = QPen(QColor(STATUS_OK if match.passed else ERROR_COLOR), 3)
            pen.setCosmetic(True)
            if not match.passed:
                pen.setStyle(Qt.PenStyle.DashLine)
            item.setPen(pen)
            item.setZValue(40)
            item.setToolTip(f"{match.name}: {match.score:.3f}")
            self._scene.addItem(item)
            self._diagnostics.append(item)

    def clear_result_overlay(self) -> None:
        self._result_badge.hide()
        for item in self._diagnostics:
            self._scene.removeItem(item)
        self._diagnostics.clear()

    def set_objects(
        self,
        objects: tuple[EditorObject, ...],
        selected: EditorTarget | None = None,
        *,
        editable: bool = True,
    ) -> None:
        self._updating = True
        try:
            for item in self._objects:
                self._scene.removeItem(item)
            self._objects.clear()
            if self._size is None:
                return
            for value in objects:
                item = _RegionItem(value, self._size, self._on_geometry_edit)
                if not editable:
                    item.setFlags(QGraphicsItem.GraphicsItemFlag(0))
                self._scene.addItem(item)
                self._objects.append(item)
                item.setSelected(value.target == selected)
        finally:
            self._updating = False

    def set_tool(self, tool: EditorTool) -> None:
        self._tool = tool
        self.setInteractive(tool is not EditorTool.PAN)
        self.setDragMode(
            QGraphicsView.DragMode.ScrollHandDrag
            if tool is EditorTool.PAN
            else QGraphicsView.DragMode.NoDrag
        )
        self.viewport().setCursor(
            Qt.CursorShape.CrossCursor if tool in _TOOLS else Qt.CursorShape.ArrowCursor
        )

    def set_landmark_role(self, role: LandmarkRole) -> None:
        self._role = role

    def fit_image(self) -> None:
        if self._size is not None:
            self.fitInView(self._pixmap, Qt.AspectRatioMode.KeepAspectRatio)
        self._fitting = True

    def zoom_in(self) -> None:
        self.scale(1.25, 1.25)
        self._fitting = False

    def zoom_out(self) -> None:
        self.scale(0.8, 0.8)
        self._fitting = False

    def clear_image(self) -> None:
        self.clear_result_overlay()
        self._pixmap.setPixmap(QPixmap())
        self._size = None
        self.set_objects(())

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        if self._fitting:
            self.fit_image()

    def _bounded(self, point: QPointF) -> QPointF:
        if self._size is None:
            return QPointF()
        return QPointF(
            max(0.0, min(point.x(), self._size.width)),
            max(0.0, min(point.y(), self._size.height)),
        )

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if (
            event.button() == Qt.MouseButton.LeftButton
            and self._tool in _TOOLS
            and self._size is not None
        ):
            self._origin = self._bounded(self.mapToScene(event.pos()))
            self._drawing = QGraphicsRectItem()
            self._drawing.setPen(QPen(QColor(PRIMARY), 2, Qt.PenStyle.DashLine))
            self._drawing.setZValue(30)
            self._scene.addItem(self._drawing)
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._drawing is not None and self._origin is not None:
            self._drawing.setRect(
                QRectF(self._origin, self._bounded(self.mapToScene(event.pos()))).normalized()
            )
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if self._drawing is not None and self._origin is not None:
            rect = self._drawing.rect()
            self._scene.removeItem(self._drawing)
            self._drawing, self._origin = None, None
            if rect.width() >= 2 and rect.height() >= 2:
                self.geometry_edited.emit(
                    GeometryEdit(
                        EditorTarget(_TOOLS[self._tool], None),
                        Region(
                            floor(rect.x()),
                            floor(rect.y()),
                            floor(rect.width()),
                            floor(rect.height()),
                        ),
                        LandmarkSupport.CIRCLE
                        if self._tool is EditorTool.CIRCLE_LANDMARK
                        else LandmarkSupport.RECTANGLE,
                        self._role,
                    )
                )
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def _on_geometry_edit(self, edit: GeometryEdit) -> None:
        self.geometry_edited.emit(edit)

    def _on_selection_changed(self) -> None:
        if self._updating:
            return
        selected = self._scene.selectedItems()
        self.object_selected.emit(
            selected[0].target if selected and isinstance(selected[0], _RegionItem) else None
        )
