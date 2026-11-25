"""Main window: New Snip hides the window, runs the rectangle capture and opens the preview."""
from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import QLabel, QMainWindow, QPushButton, QVBoxLayout, QWidget

from .capture import SnipOverlay
from .preview import PreviewWindow


class MainWindow(QMainWindow):
    HIDE_MS = 250    # time for the window to leave the screen before the desktop is grabbed

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Snipping Tool")
        w = QWidget()
        v = QVBoxLayout(w)
        self.b_new = QPushButton("New Snip")
        self.b_new.setMinimumHeight(44)
        self.b_new.clicked.connect(self.new_snip)
        self.status = QLabel("Drag a rectangle to capture. Esc cancels.")
        self.status.setAlignment(Qt.AlignCenter)
        v.addWidget(self.b_new)
        v.addWidget(self.status)
        self.setCentralWidget(w)
        self.resize(360, 130)
        self.overlay = None
        self.preview = None

    def new_snip(self):
        if self.overlay is not None:
            return                     # a capture is already open
        self.b_new.setEnabled(False)
        self.hide()
        QTimer.singleShot(self.HIDE_MS, self._start_overlay)

    def _start_overlay(self, shot=None, geometry=None):
        self.overlay = SnipOverlay(shot, geometry)
        self.overlay.captured.connect(self.on_captured)
        self.overlay.cancelled.connect(self.on_cancelled)
        self.overlay.start()

    def on_captured(self, pix):
        self.overlay = None
        self._back("Captured")
        self.preview = PreviewWindow(pix)
        self.preview.show()
        self.preview.raise_()
        self.preview.activateWindow()

    def on_cancelled(self):
        self.overlay = None
        self._back("Cancelled")

    def _back(self, msg):
        self.b_new.setEnabled(True)
        self.status.setText(msg)
        self.show()
