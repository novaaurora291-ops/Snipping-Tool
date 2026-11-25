"""Rectangle capture: a frozen screenshot of the whole desktop, drag a rectangle, release to capture, Esc cancels."""
from PySide6.QtCore import QPoint, QRect, Qt, Signal
from PySide6.QtGui import QColor, QGuiApplication, QPainter, QPen, QPixmap
from PySide6.QtWidgets import QWidget


def grab_desktop():
    """One pixmap of every screen, laid out like the virtual desktop (logical pixels)."""
    screens = QGuiApplication.screens()
    if len(screens) == 1:
        # one screen: keep the grab at its full (physical) resolution; the overlay maps logical -> physical
        return screens[0].geometry(), screens[0].grabWindow(0)
    virt = QRect()
    for s in screens:
        virt = virt.united(s.geometry())
    shot = QPixmap(virt.size())
    shot.fill(Qt.black)
    p = QPainter(shot)
    for s in screens:
        g = s.geometry()
        p.drawPixmap(g.topLeft() - virt.topLeft(), s.grabWindow(0).scaled(g.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
                     if s.devicePixelRatio() != 1 else s.grabWindow(0))
    p.end()
    return virt, shot


class SnipOverlay(QWidget):
    """Full-desktop overlay. Signals: captured(QPixmap) after a drag, cancelled() on Esc / right click / empty drag."""
    captured = Signal(QPixmap)
    cancelled = Signal()
    MIN_SIZE = 3

    def __init__(self, shot=None, geometry=None):
        super().__init__(None, Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setCursor(Qt.CrossCursor)
        self.setFocusPolicy(Qt.StrongFocus)
        if shot is None:
            geometry, shot = grab_desktop()
        self.shot = shot
        self.setGeometry(geometry or QRect(QPoint(0, 0), shot.size()))
        self.origin = None
        self.end = None
        self.done = False

    def start(self):
        self.show()
        self.raise_()
        self.activateWindow()
        self.setFocus()

    def selection(self):
        """The dragged area: exactly |dx| x |dy| pixels (QRect(p0, p1) would include both corners, +1 px)."""
        if self.end is None:
            return QRect()
        a, b = self._p0, self.end
        return QRect(min(a.x(), b.x()), min(a.y(), b.y()), abs(b.x() - a.x()), abs(b.y() - a.y()))

    def paintEvent(self, e):
        p = QPainter(self)
        p.drawPixmap(self.rect(), self.shot)
        p.fillRect(self.rect(), QColor(0, 0, 0, 110))
        r = self.selection()
        if not r.isEmpty():
            p.drawPixmap(r, self.shot, self._src(r))
            p.setPen(QPen(QColor("#9BEA2C"), 2))
            p.drawRect(r.adjusted(0, 0, -1, -1))
            p.setPen(Qt.white)
            p.drawText(r.left(), max(14, r.top() - 6), f"{r.width()} x {r.height()}")

    def _src(self, r):
        sx = self.shot.width() / max(1, self.width())
        sy = self.shot.height() / max(1, self.height())
        return QRect(int(r.x() * sx), int(r.y() * sy), int(r.width() * sx), int(r.height() * sy))

    def mousePressEvent(self, e):
        if e.button() == Qt.RightButton:
            return self.cancel()
        if e.button() == Qt.LeftButton:
            self.origin = self._p0 = e.position().toPoint()
            self.end = self.origin
            self.update()

    def mouseMoveEvent(self, e):
        if self.origin is not None:
            self.end = e.position().toPoint()
            self.update()

    def mouseReleaseEvent(self, e):
        if e.button() != Qt.LeftButton or self.origin is None:
            return
        self.end = e.position().toPoint()
        self.origin = None
        r = self.selection()
        if r.width() < self.MIN_SIZE or r.height() < self.MIN_SIZE:
            return self.cancel()
        self.finish(self.shot.copy(self._src(r)))

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.cancel()
        else:
            super().keyPressEvent(e)

    def finish(self, pix):
        if self.done:
            return
        self.done = True
        self.close()
        self.captured.emit(pix)

    def cancel(self):
        if self.done:
            return
        self.done = True
        self.close()
        self.cancelled.emit()
