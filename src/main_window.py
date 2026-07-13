from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFileDialog,
    QLabel,
    QMainWindow,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from src.image_viewer import ImageViewer


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("ReliefForge")
        self.resize(1400, 900)

        splitter = QSplitter(Qt.Horizontal)

        # Linke Seite
        self.preview = ImageViewer()

        # Rechte Seite
        sidebar = QWidget()
        sidebar.setFixedWidth(300)

        layout = QVBoxLayout(sidebar)

        title = QLabel("ReliefForge")
        title.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
        """)

        self.open_button = QPushButton("Open Image")
        self.open_button.clicked.connect(self.open_image)

        generate_button = QPushButton("Generate STL")

        layout.addWidget(title)
        layout.addSpacing(20)
        layout.addWidget(self.open_button)
        layout.addWidget(generate_button)
        layout.addStretch()

        splitter.addWidget(self.preview)
        splitter.addWidget(sidebar)

        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 0)

        self.setCentralWidget(splitter)

    def open_image(self):
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Open Image",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp *.webp)"
        )

        if filename:
            self.preview.load_image(filename)