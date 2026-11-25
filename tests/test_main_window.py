import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6.QtCore import QPoint, QRect, Qt
from PySide6.QtGui import QColor, QPixmap
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from snipping_tool.main_window import MainWindow

app = QApplication.instance() or QApplication([])


def shot():
    p = QPixmap(300, 200)
    p.fill(QColor("green"))
    return p


def test_new_snip_capture_opens_preview():
    w = MainWindow()
    w.show()
    w._start_overlay(shot(), QRect(0, 0, 300, 200))
    o = w.overlay
    QTest.mousePress(o, Qt.LeftButton, pos=QPoint(5, 5))
    QTest.mouseRelease(o, Qt.LeftButton, pos=QPoint(65, 45))
    assert w.preview is not None and (w.preview.pix.width(), w.preview.pix.height()) == (60, 40)
    assert w.isVisible() and w.overlay is None


def test_new_snip_cancel_returns():
    w = MainWindow()
    w._start_overlay(shot(), QRect(0, 0, 300, 200))
    QTest.keyClick(w.overlay, Qt.Key_Escape)
    assert w.preview is None and w.overlay is None and w.isVisible()
