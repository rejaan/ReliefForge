from pathlib import Path

import trimesh
from PySide6.QtCore import Qt, QThread, QTimer
from PySide6.QtWidgets import (
    QFileDialog,
    QMainWindow,
    QMessageBox,
    QSplitter,
)

from src.engine.export import STLExporter
from src.engine.relief_generator import ReliefGenerator
from src.ui.image_viewer import ImageViewer
from src.ui.inspector import Inspector
from src.ui.mesh_viewer import MeshViewer
from src.ui.mesh_worker import MeshWorker
from src.ui.sidebar import Sidebar


class MainWindow(QMainWindow):
    """Main application window for ReliefForge."""

    def __init__(self):
        super().__init__()

        self.image_path: str | None = None
        self.image_resolution: tuple[int, int] | None = None
        self.current_mesh: trimesh.Trimesh | None = None

        self.mesh_thread: QThread | None = None
        self.mesh_worker: MeshWorker | None = None
        self.pending_mesh_update = False

        self.setWindowTitle("ReliefForge v0.3.4 – Background Processing")
        self.resize(1550, 920)
        self.setMinimumSize(1150, 720)

        self.live_update_timer = QTimer(self)
        self.live_update_timer.setSingleShot(True)
        self.live_update_timer.setInterval(400)
        self.live_update_timer.timeout.connect(self.update_live_views)

        self._build_interface()
        self._connect_signals()

        self.statusBar().showMessage("Ready")

    def _build_interface(self) -> None:
        self.image_viewer = ImageViewer()
        self.image_viewer.setMinimumWidth(350)

        self.mesh_viewer = MeshViewer()
        self.mesh_viewer.setMinimumWidth(350)

        self.sidebar = Sidebar()
        self.inspector = Inspector()

        viewer_splitter = QSplitter(Qt.Horizontal)
        viewer_splitter.setChildrenCollapsible(False)
        viewer_splitter.addWidget(self.image_viewer)
        viewer_splitter.addWidget(self.mesh_viewer)
        viewer_splitter.setStretchFactor(0, 1)
        viewer_splitter.setStretchFactor(1, 1)
        viewer_splitter.setSizes([600, 600])

        self.sidebar.layout().insertWidget(
            self.sidebar.layout().count() - 2,
            self.inspector,
        )

        main_splitter = QSplitter(Qt.Horizontal)
        main_splitter.setChildrenCollapsible(False)
        main_splitter.addWidget(viewer_splitter)
        main_splitter.addWidget(self.sidebar)
        main_splitter.setStretchFactor(0, 1)
        main_splitter.setStretchFactor(1, 0)
        main_splitter.setSizes([1200, 350])

        self.setCentralWidget(main_splitter)

    def _connect_signals(self) -> None:
        self.sidebar.open_image_requested.connect(self.open_image)
        self.sidebar.refresh_requested.connect(self.update_live_views)
        self.sidebar.export_requested.connect(self.export_stl)
        self.sidebar.settings_changed.connect(self.schedule_live_update)

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
        self.pending_mesh_update = False

        self.image_viewer.load_image(filename)

        pixmap = self.image_viewer._original_pixmap

        if pixmap is not None:
            self.image_resolution = (
                pixmap.width(),
                pixmap.height(),
            )
        else:
            self.image_resolution = None

        self.inspector.clear()
        self.inspector.set_image(Path(filename).name)

        if self.image_resolution is not None:
            self.inspector.set_resolution(
                self.image_resolution[0],
                self.image_resolution[1],
            )

        self.statusBar().showMessage(
            f"Image loaded: {Path(filename).name}"
        )

        self.update_live_views()

    def schedule_live_update(self) -> None:
        if not self.image_path:
            return

        self.current_mesh = None
        self.pending_mesh_update = True

        self.statusBar().showMessage(
            "Waiting for parameter changes..."
        )

        self.live_update_timer.start()

    def update_live_views(self) -> None:
        if not self.image_path:
            return

        self.live_update_timer.stop()
        self.update_2d_preview()
        self.start_mesh_generation()

    def update_2d_preview(self) -> None:
        if not self.image_path:
            return

        try:
            pixmap = ReliefGenerator.create_slice_preview(
                image_path=self.image_path,
                slice_count=self.sidebar.slice_count(),
                relief_height=self.sidebar.relief_depth(),
            )

            self.image_viewer.show_pixmap(pixmap)

        except Exception as error:
            self.statusBar().showMessage(
                f"2D preview failed: {error}"
            )

    def start_mesh_generation(self) -> None:
        if not self.image_path:
            return

        if self.mesh_thread is not None:
            self.pending_mesh_update = True
            self.statusBar().showMessage(
                "Current calculation running — update queued"
            )
            return

        self.pending_mesh_update = False

        settings = self.sidebar.settings()

        self.mesh_thread = QThread(self)
        self.mesh_worker = MeshWorker(
            image_path=self.image_path,
            settings=settings,
        )

        self.mesh_worker.moveToThread(self.mesh_thread)

        self.mesh_thread.started.connect(self.mesh_worker.run)

        self.mesh_worker.finished.connect(self._on_mesh_ready)
        self.mesh_worker.failed.connect(self._on_mesh_failed)

        self.mesh_worker.finished.connect(self.mesh_thread.quit)
        self.mesh_worker.failed.connect(self.mesh_thread.quit)

        self.mesh_worker.finished.connect(
            self.mesh_worker.deleteLater
        )
        self.mesh_worker.failed.connect(
            self.mesh_worker.deleteLater
        )

        self.mesh_thread.finished.connect(
            self.mesh_thread.deleteLater
        )
        self.mesh_thread.finished.connect(
            self._on_mesh_thread_finished
        )

        self.statusBar().showMessage(
            "Generating 3D mesh in background..."
        )

        self.mesh_thread.start()

    def _on_mesh_ready(
        self,
        mesh: trimesh.Trimesh,
        generation_time: float,
    ) -> None:
        # Wurden während der Berechnung Regler verändert,
        # wird dieses inzwischen veraltete Ergebnis nicht angezeigt.
        if self.pending_mesh_update:
            self.statusBar().showMessage(
                "Applying newer settings..."
            )
            return

        self.current_mesh = mesh
        self.mesh_viewer.show_mesh(mesh)
        self.inspector.update_mesh(mesh, generation_time)

        self.statusBar().showMessage(
            f"Ready — {len(mesh.vertices):,} vertices, "
            f"{len(mesh.faces):,} faces, "
            f"{generation_time:.2f} s"
        )

    def _on_mesh_failed(self, error_text: str) -> None:
        self.current_mesh = None

        self.statusBar().showMessage(
            "Mesh generation failed"
        )

        QMessageBox.critical(
            self,
            "Mesh generation error",
            error_text,
        )

    def _on_mesh_thread_finished(self) -> None:
        self.mesh_thread = None
        self.mesh_worker = None

        if self.pending_mesh_update:
            self.pending_mesh_update = False
            QTimer.singleShot(0, self.start_mesh_generation)

    def export_stl(self) -> None:
        if not self.image_path:
            QMessageBox.warning(
                self,
                "No image",
                "Please open an image first.",
            )
            return

        if self.mesh_thread is not None:
            QMessageBox.information(
                self,
                "Mesh is being generated",
                "Please wait until the current calculation is finished.",
            )
            return

        if self.current_mesh is None or self.current_mesh.is_empty:
            QMessageBox.warning(
                self,
                "No mesh",
                "Please wait for the 3D preview to finish.",
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
                "The current mesh was exported successfully.",
            )

        except Exception as error:
            self.statusBar().showMessage(
                "STL export failed"
            )

            QMessageBox.critical(
                self,
                "STL export error",
                str(error),
            )

    def closeEvent(self, event) -> None:
        if self.mesh_thread is not None:
            self.mesh_thread.quit()
            self.mesh_thread.wait(3000)

        event.accept()