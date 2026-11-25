import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6.QtCore import QPoint, QRect, Qt
from PySide6.QtGui import QColor, QPixmap
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from snipping_tool.capture import SnipOverlay

app = QApplication.instance() or QApplication([])


def shot():
    p = QPixmap(400, 300)
    p.fill(QColor("red"))
    return p


def test_drag_captures_rectangle():
    o = SnipOverlay(shot(), QRect(0, 0, 400, 300))
    got = []
    o.captured.connect(got.append)
    o.start()
    QTest.mousePress(o, Qt.LeftButton, pos=QPoint(10, 20))
    QTest.mouseMove(o, QPoint(80, 60))
    QTest.mouseRelease(o, Qt.LeftButton, pos=QPoint(110, 70))
    assert len(got) == 1 and (got[0].width(), got[0].height()) == (100, 50)
    assert got[0].toImage().pixelColor(5, 5) == QColor("red")


def test_esc_cancels():
    o = SnipOverlay(shot(), QRect(0, 0, 400, 300))
    got, cancel = [], []
    o.captured.connect(got.append)
    o.cancelled.connect(lambda: cancel.append(1))
    o.start()
    QTest.mousePress(o, Qt.LeftButton, pos=QPoint(10, 20))
    QTest.keyClick(o, Qt.Key_Escape)
    assert cancel == [1] and got == []


def test_tiny_drag_cancels():
    o = SnipOverlay(shot(), QRect(0, 0, 400, 300))
    cancel = []
    o.cancelled.connect(lambda: cancel.append(1))
    o.start()
    QTest.mousePress(o, Qt.LeftButton, pos=QPoint(10, 20))
    QTest.mouseRelease(o, Qt.LeftButton, pos=QPoint(11, 21))
    assert cancel == [1]
