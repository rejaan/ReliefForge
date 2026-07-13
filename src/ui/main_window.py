from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFileDialog,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSlider,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from src.engine.export import STLExporter
from src.ui.image_viewer import ImageViewer
from src.engine.mesh_generator import MeshGenerator
from src.engine.relief_generator import ReliefGenerator


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.image_path = None

        self.setWindowTitle("ReliefForge")
        self.resize(1400, 900)

        splitter = QSplitter(Qt.Horizontal)

        self.preview = ImageViewer()

        sidebar = QWidget()
        sidebar.setFixedWidth(320)

        layout = QVBoxLayout(sidebar)

        title = QLabel("ReliefForge")
        title.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
        """)

        self.open_button = QPushButton("Open Image")
        self.open_button.clicked.connect(self.open_image)

        slice_label = QLabel("Slice Count")

        self.slice_slider = QSlider(Qt.Horizontal)
        self.slice_slider.setMinimum(20)
        self.slice_slider.setMaximum(180)
        self.slice_slider.setValue(80)

        self.slice_value = QLabel("80")
        self.slice_value.setAlignment(Qt.AlignRight)
        self.slice_slider.valueChanged.connect(
            lambda value: self.slice_value.setText(str(value))
        )

        height_label = QLabel("Relief Depth")

        self.height_slider = QSlider(Qt.Horizontal)
        self.height_slider.setMinimum(2)
        self.height_slider.setMaximum(30)
        self.height_slider.setValue(12)

        self.height_value = QLabel("12 mm")
        self.height_value.setAlignment(Qt.AlignRight)
        self.height_slider.valueChanged.connect(
            lambda value: self.height_value.setText(f"{value} mm")
        )

        self.preview_button = QPushButton("Generate Preview")
        self.preview_button.clicked.connect(self.generate_preview)

        self.export_button = QPushButton("Export STL")
        self.export_button.clicked.connect(self.export_stl)

        layout.addWidget(title)
        layout.addSpacing(20)
        layout.addWidget(self.open_button)

        layout.addSpacing(25)
        layout.addWidget(slice_label)
        layout.addWidget(self.slice_slider)
        layout.addWidget(self.slice_value)

        layout.addSpacing(15)
        layout.addWidget(height_label)
        layout.addWidget(self.height_slider)
        layout.addWidget(self.height_value)

        layout.addStretch()
        layout.addWidget(self.preview_button)
        layout.addWidget(self.export_button)

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
            "Images (*.png *.jpg *.jpeg *.bmp *.webp)",
        )

        if filename:
            self.image_path = filename
            self.preview.load_image(filename)

    def generate_preview(self):
        if not self.image_path:
            QMessageBox.warning(
                self,
                "No image",
                "Please open an image first.",
            )
            return

        try:
            pixmap = ReliefGenerator.create_slice_preview(
                image_path=self.image_path,
                slice_count=self.slice_slider.value(),
                relief_height=self.height_slider.value(),
            )

            self.preview.show_pixmap(pixmap)

        except Exception as error:
            QMessageBox.critical(
                self,
                "Preview error",
                str(error),
            )

    def export_stl(self):
        if not self.image_path:
            QMessageBox.warning(
                self,
                "No image",
                "Please open an image first.",
            )
            return

        output_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export STL",
            "reliefforge_model.stl",
            "STL Files (*.stl)",
        )

        if not output_path:
            return

        try:
            self.export_button.setEnabled(False)
            self.export_button.setText("Generating STL...")

            mesh = MeshGenerator.create_slice_mesh(
                image_path=self.image_path,
                width_mm=180.0,
                height_mm=130.0,
                slice_count=self.slice_slider.value(),
                slice_thickness_mm=0.8,
                base_depth_mm=2.0,
                relief_depth_mm=self.height_slider.value(),
                profile_samples=180,
            )

            STLExporter.export(mesh, output_path)

            QMessageBox.information(
                self,
                "Export complete",
                "The STL file was created successfully.",
            )

        except Exception as error:
            QMessageBox.critical(
                self,
                "STL export error",
                str(error),
            )

        finally:
            self.export_button.setEnabled(True)
            self.export_button.setText("Export STL")