"""
Phase 2: Spatial UI overlay — frameless, translucent radial menu (PyQt6).
"""

from __future__ import annotations

import math
from collections.abc import Callable
from typing import TYPE_CHECKING

from PyQt6.QtCore import QPoint, Qt, QTimer
from PyQt6.QtGui import (
    QColor,
    QCursor,
    QFont,
    QPainter,
    QPen,
)
from PyQt6.QtWidgets import (
    QApplication,
    QLineEdit,
    QMainWindow,
    QWidget,
)

if TYPE_CHECKING:
    from PyQt6.QtGui import QMouseEvent, QPaintEvent, QKeyEvent

# ── Layout constants ──────────────────────────────────────────────────────────
_WINDOW_SIZE = 320          # square canvas side
_ORBIT_RADIUS = 100         # distance from center to node center
_NODE_RADIUS = 38           # node circle radius
_CENTER_RADIUS = 22         # anchor dot radius

# ── Nodes (label, angle in degrees) ──────────────────────────────────────────
_NODES: list[tuple[str, float]] = [
    ("Init\nSandbox", 270.0),   # top
    ("Prompt",        30.0),    # top-right
    ("Cancel",        150.0),   # top-left
]

# ── Colours ───────────────────────────────────────────────────────────────────
_BG_ALPHA = 0                          # fully transparent canvas
_NODE_FILL = QColor(30, 30, 50, 220)
_NODE_HOVER = QColor(80, 100, 200, 240)
_CENTER_FILL = QColor(200, 200, 255, 230)
_TEXT_COLOR = QColor(240, 240, 255)
_PROMPT_ACTIVE_FILL = QColor(50, 70, 180, 240)


def _deg_to_rad(deg: float) -> float:
    return math.radians(deg)


def _node_center(window_center: QPoint, angle_deg: float) -> QPoint:
    rad = _deg_to_rad(angle_deg)
    return QPoint(
        round(window_center.x() + _ORBIT_RADIUS * math.cos(rad)),
        round(window_center.y() + _ORBIT_RADIUS * math.sin(rad)),
    )


class _Canvas(QWidget):
    """Internal widget that owns painting and mouse events."""

    def __init__(
        self,
        on_init_sandbox: Callable[[], None],
        on_cancel: Callable[[], None],
        parent: QMainWindow,
    ) -> None:
        super().__init__(parent)
        self._on_init_sandbox = on_init_sandbox
        self._on_cancel = on_cancel
        self._hovered: int | None = None  # index into _NODES
        self._prompt_active = False

        # ── Prompt input ──────────────────────────────────────────────────
        self._prompt_input = QLineEdit(self)
        self._prompt_input.setFixedWidth(220)
        self._prompt_input.setFixedHeight(32)
        self._prompt_input.setPlaceholderText("Describe what you want…")
        self._prompt_input.setStyleSheet(
            "QLineEdit {"
            "  background: rgba(20,20,40,220);"
            "  color: #dde;"
            "  border: 1px solid rgba(120,140,255,180);"
            "  border-radius: 6px;"
            "  padding: 4px 8px;"
            "  font-size: 13px;"
            "}"
        )
        self._prompt_input.hide()
        self._prompt_input.returnPressed.connect(self._on_prompt_submitted)

        self.setMouseTracking(True)

    # ── Public helpers ────────────────────────────────────────────────────────

    def show_prompt(self) -> None:
        c = self._window_center()
        pw = self._prompt_input.width()
        self._prompt_input.move(c.x() - pw // 2, c.y() + _ORBIT_RADIUS + _NODE_RADIUS + 8)
        self._prompt_input.show()
        self._prompt_input.setFocus()
        self._prompt_active = True
        self.update()

    def hide_prompt(self) -> None:
        self._prompt_input.hide()
        self._prompt_input.clear()
        self._prompt_active = False
        self.update()

    def prompt_text(self) -> str:
        return self._prompt_input.text()

    def set_placeholder(self, text: str) -> None:
        self._prompt_input.setPlaceholderText(text)

    # ── Geometry helpers ──────────────────────────────────────────────────────

    def _window_center(self) -> QPoint:
        return QPoint(self.width() // 2, self.height() // 2)

    def _hit_test(self, pos: QPoint) -> int | None:
        """Return the index of the node under pos, or None."""
        c = self._window_center()
        for i, (_, angle) in enumerate(_NODES):
            nc = _node_center(c, angle)
            dx, dy = pos.x() - nc.x(), pos.y() - nc.y()
            if math.hypot(dx, dy) <= _NODE_RADIUS:
                return i
        return None

    # ── Qt events ─────────────────────────────────────────────────────────────

    def paintEvent(self, _event: QPaintEvent) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        c = self._window_center()

        # Orbit guide ring
        p.setPen(QPen(QColor(180, 180, 255, 50), 1, Qt.PenStyle.DashLine))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawEllipse(c, _ORBIT_RADIUS, _ORBIT_RADIUS)

        # Nodes
        font = QFont("Helvetica", 9)
        font.setBold(True)
        p.setFont(font)

        for i, (label, angle) in enumerate(_NODES):
            nc = _node_center(c, angle)
            is_hover = i == self._hovered
            is_prompt_node = label.startswith("Prompt")

            if is_prompt_node and self._prompt_active:
                fill = _PROMPT_ACTIVE_FILL
            elif is_hover:
                fill = _NODE_HOVER
            else:
                fill = _NODE_FILL

            # Spoke
            p.setPen(QPen(QColor(180, 180, 255, 80), 1))
            p.drawLine(c, nc)

            # Node circle
            p.setPen(QPen(QColor(180, 180, 255, 160), 1))
            p.setBrush(fill)
            p.drawEllipse(nc, _NODE_RADIUS, _NODE_RADIUS)

            # Label
            p.setPen(QPen(_TEXT_COLOR))
            rect = p.boundingRect(
                nc.x() - _NODE_RADIUS,
                nc.y() - _NODE_RADIUS,
                _NODE_RADIUS * 2,
                _NODE_RADIUS * 2,
                Qt.AlignmentFlag.AlignCenter,
                label,
            )
            p.drawText(rect, Qt.AlignmentFlag.AlignCenter, label)

        # Center anchor
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(_CENTER_FILL)
        p.drawEllipse(c, _CENTER_RADIUS, _CENTER_RADIUS)

        p.end()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        prev = self._hovered
        self._hovered = self._hit_test(event.pos())
        if self._hovered != prev:
            self.update()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() != Qt.MouseButton.LeftButton:
            return
        hit = self._hit_test(event.pos())
        if hit is None:
            return
        label, _ = _NODES[hit]
        if label.startswith("Init"):
            self._on_init_sandbox()
        elif label.startswith("Prompt"):
            self.show_prompt()
        elif label.startswith("Cancel"):
            self._on_cancel()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() in (Qt.Key.Key_Escape, Qt.Key.Key_Return):
            self._on_cancel()
        else:
            super().keyPressEvent(event)

    # ── Internal slots ────────────────────────────────────────────────────────

    def _on_prompt_submitted(self) -> None:
        # Bubble up via parent window callback
        win: RadialMenuWindow = self.parent()  # type: ignore[assignment]
        win.on_prompt_submitted(self.prompt_text())


class RadialMenuWindow(QMainWindow):
    """
    Phase 2.1 – 2.6: Frameless, translucent radial menu window.
    """

    def __init__(
        self,
        on_init_sandbox: Callable[[], None],
        on_prompt: Callable[[str], None],
    ) -> None:
        super().__init__()
        self._on_prompt = on_prompt

        # Phase 2.1: window flags
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool  # keeps it off the taskbar / dock
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(_WINDOW_SIZE, _WINDOW_SIZE)

        self._canvas = _Canvas(
            on_init_sandbox=on_init_sandbox,
            on_cancel=self._hide_overlay,
            parent=self,
        )
        self._canvas.setGeometry(0, 0, _WINDOW_SIZE, _WINDOW_SIZE)
        self.setCentralWidget(self._canvas)

    # ── Public API ────────────────────────────────────────────────────────────

    def show_at_cursor(self) -> None:
        """Phase 2.2: centre the window on the current global mouse position."""
        pos = QCursor.pos()
        half = _WINDOW_SIZE // 2
        self.move(pos.x() - half, pos.y() - half)
        self.show()
        self.activateWindow()
        self._canvas.setFocus()

    def set_prompt_placeholder(self, text: str) -> None:
        self._canvas.set_placeholder(text)

    def on_prompt_submitted(self, text: str) -> None:
        self._hide_overlay()
        self._on_prompt(text)

    # ── Phase 2.6: hide & clear ───────────────────────────────────────────────

    def _hide_overlay(self) -> None:
        self._canvas.hide_prompt()
        self.hide()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() in (Qt.Key.Key_Escape,):
            self._hide_overlay()
        else:
            super().keyPressEvent(event)
