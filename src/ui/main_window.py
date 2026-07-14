from pathlib import Path

import trimesh
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

from src.engine.export import STLExporter
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
        self.current_mesh: trimesh.Trimesh | None = None

        self.setWindowTitle("ReliefForge v0.2.2 – Live Mesh")
        self.resize(1500, 900)
        self.setMinimumSize(1100, 700)

        # Wartet kurz, nachdem ein Regler bewegt wurde.
        # So wird das Mesh nicht bei jedem einzelnen Slider-Schritt berechnet.
        self.live_update_timer = QTimer(self)
        self.live_update_timer.setSingleShot(True)
        self.live_update_timer.setInterval(400)
        self.live_update_timer.timeout.connect(self.update_live_views)

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

        version = QLabel("v0.2.2 – Live Mesh")
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
        self.slice_slider.valueChanged.connect(self.schedule_live_update)

        depth_label = QLabel("Relief Depth")

        self.depth_slider = QSlider(Qt.Horizontal)
        self.depth_slider.setRange(2, 30)
        self.depth_slider.setValue(12)

        self.depth_value = QLabel("12 mm")
        self.depth_value.setAlignment(Qt.AlignRight)

        self.depth_slider.valueChanged.connect(
            lambda value: self.depth_value.setText(f"{value} mm")
        )
        self.depth_slider.valueChanged.connect(self.schedule_live_update)

        self.refresh_button = QPushButton("Refresh 2D + 3D")
        self.refresh_button.clicked.connect(self.update_live_views)

        self.export_button = QPushButton("Export STL")
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
        layout.addWidget(self.refresh_button)
        layout.addWidget(self.export_button)

        return sidebar

    def create_settings(self) -> ReliefSettings:
        """Creates the current engine settings from the UI controls."""

        return ReliefSettings(
            slice_count=self.slice_slider.value(),
            model_width_mm=180.0,
            base_thickness_mm=2.0,
            relief_depth_mm=float(self.depth_slider.value()),
            invert=True,
            blur_kernel=3,
            equalize_histogram=True,
        )

    def schedule_live_update(self) -> None:
        """Schedules a combined 2D and 3D update."""

        if not self.image_path:
            return

        # Das gespeicherte Mesh entspricht nach einer Änderung
        # nicht mehr den aktuellen Einstellungen.
        self.current_mesh = None

        self.statusBar().showMessage("Waiting for parameter changes...")
        self.live_update_timer.start()

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
        self.current_mesh = None

        self.image_viewer.load_image(filename)

        image_name = Path(filename).name
        self.statusBar().showMessage(f"Image loaded: {image_name}")

        # Nach dem Öffnen sofort 2D- und 3D-Vorschau erzeugen.
        self.update_live_views()

    def update_live_views(self) -> None:
        """Updates both the 2D preview and the interactive 3D mesh."""

        if not self.image_path:
            return

        self.live_update_timer.stop()

        try:
            self._set_generation_state(True)
            self.statusBar().showMessage("Updating 2D and 3D preview...")

            self.update_2d_preview()
            self.update_3d_mesh()

            if self.current_mesh is not None:
                vertex_count = len(self.current_mesh.vertices)
                face_count = len(self.current_mesh.faces)

                self.statusBar().showMessage(
                    f"Ready — {vertex_count:,} vertices, "
                    f"{face_count:,} faces"
                )

        except Exception as error:
            self.current_mesh = None
            self.statusBar().showMessage(f"Preview failed: {error}")

        finally:
            self._set_generation_state(False)

    def update_2d_preview(self) -> None:
        """Generates the 2D slice preview."""

        if not self.image_path:
            return

        pixmap = ReliefGenerator.create_slice_preview(
            image_path=self.image_path,
            slice_count=self.slice_slider.value(),
            relief_height=self.depth_slider.value(),
        )

        self.image_viewer.show_pixmap(pixmap)

    def update_3d_mesh(self) -> None:
        """Generates the current 3D mesh and displays it directly."""

        if not self.image_path:
            return

        settings = self.create_settings()

        self.current_mesh = ReliefGeneratorV2.generate_mesh(
            image_path=self.image_path,
            settings=settings,
        )

        self.mesh_viewer.show_mesh(self.current_mesh)

    def export_stl(self) -> None:
        """Exports the current in-memory mesh as an STL file."""

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
            self._set_generation_state(True)
            self.statusBar().showMessage("Preparing STL export...")

            # Falls noch kein aktuelles Mesh existiert,
            # wird es vor dem Export neu berechnet.
            if self.current_mesh is None:
                self.update_3d_mesh()

            if self.current_mesh is None or self.current_mesh.is_empty:
                raise ValueError("No valid mesh is available for export.")

            STLExporter.export(
                mesh=self.current_mesh,
                output_path=output_path,
            )

            self.statusBar().showMessage(
                f"STL exported: {Path(output_path).name}"
            )

            QMessageBox.information(
                self,
                "Export complete",
                "The current 3D mesh was exported successfully.",
            )

        except Exception as error:
            self.statusBar().showMessage("STL export failed")

            QMessageBox.critical(
                self,
                "STL export error",
                str(error),
            )

        finally:
            self._set_generation_state(False)

    def _set_generation_state(self, generating: bool) -> None:
        """Enables or disables controls while the mesh is calculated."""

        self.open_button.setEnabled(not generating)
        self.refresh_button.setEnabled(not generating)
        self.export_button.setEnabled(not generating)
        self.slice_slider.setEnabled(not generating)
        self.depth_slider.setEnabled(not generating)

        if generating:
            self.refresh_button.setText("Updating...")
        else:
            self.refresh_button.setText("Refresh 2D + 3D")