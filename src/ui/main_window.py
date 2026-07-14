from PySide6.QtCore import Qt, QTimer
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

from src.engine.relief_generator import ReliefGenerator
from src.engine.relief_generator_v2 import ReliefGeneratorV2
from src.models.relief_settings import ReliefSettings
from src.ui.image_viewer import ImageViewer
from src.ui.mesh_viewer import MeshViewer


class MainWindow(QMainWindow):
    """Main application window for ReliefForge."""

    def __init__(self):
        super().__init__()

        self.image_path: str | None = None

        self.setWindowTitle("ReliefForge v0.2.1 Alpha")
        self.resize(1500, 900)
        self.setMinimumSize(1100, 700)

        self.preview_timer = QTimer(self)
        self.preview_timer.setSingleShot(True)
        self.preview_timer.setInterval(200)
        self.preview_timer.timeout.connect(self.generate_preview)

        self._build_interface()
        self.statusBar().showMessage("Ready")

    def _build_interface(self) -> None:
        main_splitter = QSplitter(Qt.Horizontal)
        main_splitter.setChildrenCollapsible(False)

        self.image_viewer = ImageViewer()
        self.image_viewer.setMinimumWidth(350)

        self.mesh_viewer = MeshViewer()
        self.mesh_viewer.setMinimumWidth(350)

        viewer_splitter = QSplitter(Qt.Horizontal)
        viewer_splitter.setChildrenCollapsible(False)
        viewer_splitter.addWidget(self.image_viewer)
        viewer_splitter.addWidget(self.mesh_viewer)
        viewer_splitter.setStretchFactor(0, 1)
        viewer_splitter.setStretchFactor(1, 1)
        viewer_splitter.setSizes([600, 600])

        sidebar = self._create_sidebar()

        main_splitter.addWidget(viewer_splitter)
        main_splitter.addWidget(sidebar)
        main_splitter.setStretchFactor(0, 1)
        main_splitter.setStretchFactor(1, 0)
        main_splitter.setSizes([1180, 320])

        self.setCentralWidget(main_splitter)

    def _create_sidebar(self) -> QWidget:
        sidebar = QWidget()
        sidebar.setFixedWidth(320)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        title = QLabel("ReliefForge")
        title.setStyleSheet(
            """
            font-size: 28px;
            font-weight: bold;
            """
        )

        version = QLabel("v0.2.1 Alpha")
        version.setStyleSheet("color: #888888;")

        self.open_button = QPushButton("Open Image")
        self.open_button.clicked.connect(self.open_image)

        slice_label = QLabel("Slice Count")
        self.slice_slider = QSlider(Qt.Horizontal)
        self.slice_slider.setRange(20, 180)
        self.slice_slider.setValue(80)

        self.slice_value = QLabel("80")
        self.slice_value.setAlignment(Qt.AlignRight)

        self.slice_slider.valueChanged.connect(
            lambda value: self.slice_value.setText(str(value))
        )
        self.slice_slider.valueChanged.connect(self.schedule_preview)

        depth_label = QLabel("Relief Depth")
        self.depth_slider = QSlider(Qt.Horizontal)
        self.depth_slider.setRange(2, 30)
        self.depth_slider.setValue(12)

        self.depth_value = QLabel("12 mm")
        self.depth_value.setAlignment(Qt.AlignRight)

        self.depth_slider.valueChanged.connect(
            lambda value: self.depth_value.setText(f"{value} mm")
        )
        self.depth_slider.valueChanged.connect(self.schedule_preview)

        self.preview_button = QPushButton("Generate Preview")
        self.preview_button.clicked.connect(self.generate_preview)

        self.export_button = QPushButton("Generate 3D + Export STL")
        self.export_button.clicked.connect(self.export_stl)

        layout.addWidget(title)
        layout.addWidget(version)
        layout.addSpacing(15)
        layout.addWidget(self.open_button)

        layout.addSpacing(20)
        layout.addWidget(slice_label)
        layout.addWidget(self.slice_slider)
        layout.addWidget(self.slice_value)

        layout.addSpacing(10)
        layout.addWidget(depth_label)
        layout.addWidget(self.depth_slider)
        layout.addWidget(self.depth_value)

        layout.addStretch()
        layout.addWidget(self.preview_button)
        layout.addWidget(self.export_button)

        return sidebar

    def create_settings(self) -> ReliefSettings:
        return ReliefSettings(
            slice_count=self.slice_slider.value(),
            model_width_mm=180.0,
            base_thickness_mm=2.0,
            relief_depth_mm=float(self.depth_slider.value()),
            invert=True,
            blur_kernel=3,
            equalize_histogram=True,
        )

    def schedule_preview(self) -> None:
        if self.image_path:
            self.preview_timer.start()

    def open_image(self) -> None:
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Open Image",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp *.webp)",
        )

        if not filename:
            return

        self.image_path = filename
        self.image_viewer.load_image(filename)
        self.statusBar().showMessage(f"Image loaded: {filename}")
        self.generate_preview()

    def generate_preview(self) -> None:
        if not self.image_path:
            return

        try:
            pixmap = ReliefGenerator.create_slice_preview(
                image_path=self.image_path,
                slice_count=self.slice_slider.value(),
                relief_height=self.depth_slider.value(),
            )

            self.image_viewer.show_pixmap(pixmap)
            self.statusBar().showMessage("2D preview updated")

        except Exception as error:
            QMessageBox.critical(
                self,
                "Preview error",
                str(error),
            )

    def export_stl(self) -> None:
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
            self.export_button.setText("Generating...")
            self.statusBar().showMessage("Generating 3D mesh...")

            settings = self.create_settings()

            mesh = ReliefGeneratorV2.export_stl(
                image_path=self.image_path,
                output_path=output_path,
                settings=settings,
            )

            self.mesh_viewer.show_mesh(mesh)

            self.statusBar().showMessage(
                f"Ready — {len(mesh.vertices):,} vertices, "
                f"{len(mesh.faces):,} faces"
            )

            QMessageBox.information(
                self,
                "Export complete",
                "The STL was exported and loaded into the 3D viewer.",
            )

        except Exception as error:
            self.statusBar().showMessage("STL generation failed")

            QMessageBox.critical(
                self,
                "STL export error",
                str(error),
            )

        finally:
            self.export_button.setEnabled(True)
            self.export_button.setText("Generate 3D + Export STL")