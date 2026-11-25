import os, tempfile
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6.QtGui import QColor, QGuiApplication, QImage, QPixmap
from PySide6.QtWidgets import QApplication

from snipping_tool.preview import PreviewWindow, save_png

app = QApplication.instance() or QApplication([])


def pix():
    p = QPixmap(120, 80)
    p.fill(QColor("blue"))
    return p


def test_copy_puts_image_on_clipboard():
    w = PreviewWindow(pix())
    w.copy()
    img = QGuiApplication.clipboard().image()
    assert (img.width(), img.height()) == (120, 80)


def test_save_png_adds_extension_and_writes():
    d = tempfile.mkdtemp()
    out = save_png(pix(), os.path.join(d, "a"))
    assert out.endswith("a.png") and os.path.isfile(out)
    img = QImage(out)
    assert (img.width(), img.height()) == (120, 80) and img.pixelColor(3, 3) == QColor("blue")


def test_preview_save_to():
    d = tempfile.mkdtemp()
    w = PreviewWindow(pix())
    got = []
    w.saved.connect(got.append)
    assert w.save_to(os.path.join(d, "b.png")) and got
