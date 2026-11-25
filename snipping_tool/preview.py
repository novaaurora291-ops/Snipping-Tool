"""Preview of a capture with Copy (clipboard) and Save PNG."""
import os

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QGuiApplication, QPixmap
from PySide6.QtWidgets import (QFileDialog, QHBoxLayout, QLabel, QPushButton, QScrollArea, QVBoxLayout, QWidget)


def copy_to_clipboard(pix):
    QGuiApplication.clipboard().setPixmap(pix)
    return True


def save_png(pix, path):
    """Save as PNG (adds .png when missing). Returns the path written, or '' on failure."""
    if not path:
        return ""
    if not path.lower().endswith(".png"):
        path += ".png"
    d = os.path.dirname(os.path.abspath(path))
    os.makedirs(d, exist_ok=True)
    return path if pix.save(path, "PNG") else ""


class PreviewWindow(QWidget):
    saved = Signal(str)
    copied = Signal()

    def __init__(self, pix, parent=None):
        super().__init__(parent, Qt.Window)
        self.setWindowTitle("Snip preview")
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.pix = pix
        v = QVBoxLayout(self)
        self.img = QLabel()
        self.img.setAlignment(Qt.AlignCenter)
        self.img.setPixmap(pix)
        self.img.setAccessibleName("Captured image")
        sc = QScrollArea()
        sc.setWidget(self.img)
        sc.setWidgetResizable(True)
        v.addWidget(sc, 1)
        h = QHBoxLayout()
        self.info = QLabel(f"{pix.width()} x {pix.height()} px")
        h.addWidget(self.info, 1)
        self.b_copy = QPushButton("Copy")
        self.b_save = QPushButton("Save PNG")
        self.b_copy.clicked.connect(self.copy)
        self.b_save.clicked.connect(self.save_dialog)
        h.addWidget(self.b_copy)
        h.addWidget(self.b_save)
        v.addLayout(h)
        scr = QGuiApplication.primaryScreen().availableGeometry()
        self.resize(min(max(pix.width() + 40, 360), int(scr.width() * 0.8)),
                    min(max(pix.height() + 90, 200), int(scr.height() * 0.8)))

    def copy(self):
        copy_to_clipboard(self.pix)
        self.info.setText(f"{self.pix.width()} x {self.pix.height()} px - copied")
        self.copied.emit()

    def save_dialog(self):
        start = os.path.join(os.path.expanduser("~"), "Pictures", "snip.png")
        path, _ = QFileDialog.getSaveFileName(self, "Save PNG", start, "PNG image (*.png)")
        self.save_to(path)

    def save_to(self, path):
        out = save_png(self.pix, path)
        if out:
            self.info.setText(f"Saved: {out}")
            self.saved.emit(out)
        return out
