from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QLabel


class ImageViewer(QLabel):
    def __init__(self):
        super().__init__()

        self.setAlignment(Qt.AlignCenter)
        self.setText("No image loaded")

        self._original_pixmap = None
        self._zoom = 1.0

        self.setStyleSheet("""
            QLabel {
                background-color: #2b2b2b;
                color: white;
                font-size: 22px;
                border-radius: 8px;
            }
        """)

    def load_image(self, filename):
        pixmap = QPixmap(filename)

        if pixmap.isNull():
            self.setText("Could not load image")
            self._original_pixmap = None
            return

        self._original_pixmap = pixmap
        self._zoom = 1.0
        self.update_view()

    def show_pixmap(self, pixmap):
        if pixmap is None or pixmap.isNull():
            self.setText("Could not display preview")
            self._original_pixmap = None
            return

        self._original_pixmap = pixmap
        self._zoom = 1.0
        self.update_view()

    def update_view(self):
        if self._original_pixmap is None:
            return

        target_size = self.size() * self._zoom

        pixmap = self._original_pixmap.scaled(
            target_size,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )

        self.setPixmap(pixmap)

    def wheelEvent(self, event):
        if self._original_pixmap is None:
            return

        if event.angleDelta().y() > 0:
            self._zoom *= 1.1
        else:
            self._zoom /= 1.1

        self._zoom = max(0.2, min(self._zoom, 8.0))
        self.update_view()

    def resizeEvent(self, event):
        self.update_view()
        super().resizeEvent(event)