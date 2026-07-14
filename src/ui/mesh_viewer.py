import numpy as np
import pyqtgraph.opengl as gl
import trimesh
from PySide6.QtWidgets import QHBoxLayout, QPushButton, QVBoxLayout, QWidget


class MeshViewer(QWidget):
    """Interactive OpenGL viewer for ReliefForge meshes."""

    def __init__(self):
        super().__init__()

        self.current_mesh: trimesh.Trimesh | None = None
        self.mesh_item: gl.GLMeshItem | None = None
        self.wireframe_enabled = False

        self.setMinimumSize(400, 400)

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(6)

        toolbar = QHBoxLayout()
        toolbar.setContentsMargins(8, 8, 8, 0)

        self.reset_button = QPushButton("Reset View")
        self.reset_button.clicked.connect(self.reset_view)

        self.fit_button = QPushButton("Zoom to Fit")
        self.fit_button.clicked.connect(self.zoom_to_fit)

        self.wireframe_button = QPushButton("Wireframe")
        self.wireframe_button.setCheckable(True)
        self.wireframe_button.toggled.connect(self.set_wireframe)

        toolbar.addWidget(self.reset_button)
        toolbar.addWidget(self.fit_button)
        toolbar.addWidget(self.wireframe_button)
        toolbar.addStretch()

        root_layout.addLayout(toolbar)

        self.view = gl.GLViewWidget()
        self.view.setBackgroundColor((28, 29, 32))
        root_layout.addWidget(self.view, 1)

        self._add_grid()
        self._add_axes()
        self.reset_view()

    def _add_grid(self) -> None:
        grid = gl.GLGridItem()
        grid.setSize(300, 300)
        grid.setSpacing(10, 10)
        grid.translate(0, 0, 0)
        self.view.addItem(grid)

    def _add_axes(self) -> None:
        axis = gl.GLAxisItem()
        axis.setSize(60, 60, 60)
        self.view.addItem(axis)

    def show_mesh(self, mesh: trimesh.Trimesh) -> None:
        if mesh is None or mesh.is_empty:
            raise ValueError("The mesh is empty.")

        self.current_mesh = mesh.copy()

        if self.mesh_item is not None:
            self.view.removeItem(self.mesh_item)

        vertices = np.asarray(
            self.current_mesh.vertices,
            dtype=np.float32,
        )
        faces = np.asarray(
            self.current_mesh.faces,
            dtype=np.uint32,
        )

        mesh_data = gl.MeshData(
            vertexes=vertices,
            faces=faces,
        )

        self.mesh_item = gl.GLMeshItem(
            meshdata=mesh_data,
            smooth=True,
            drawFaces=True,
            drawEdges=self.wireframe_enabled,
            edgeColor=(0.2, 0.7, 1.0, 1.0),
            color=(0.72, 0.76, 0.82, 1.0),
            shader="shaded",
        )

        self.view.addItem(self.mesh_item)
        self._center_mesh()
        self.zoom_to_fit()

    def load_stl(self, filename: str) -> None:
        loaded = trimesh.load(filename, force="mesh")

        if not isinstance(loaded, trimesh.Trimesh):
            raise ValueError("The file does not contain a valid mesh.")

        self.show_mesh(loaded)

    def _center_mesh(self) -> None:
        if self.current_mesh is None or self.mesh_item is None:
            return

        center = np.asarray(
            self.current_mesh.bounding_box.centroid,
            dtype=np.float32,
        )

        self.mesh_item.translate(
            -float(center[0]),
            -float(center[1]),
            -float(center[2]),
        )

    def zoom_to_fit(self) -> None:
        if self.current_mesh is None:
            self.reset_view()
            return

        largest_dimension = max(
            float(value) for value in self.current_mesh.extents
        )

        camera_distance = max(
            80.0,
            largest_dimension * 2.3,
        )

        self.view.setCameraPosition(
            distance=camera_distance,
            elevation=28,
            azimuth=35,
        )

    def reset_view(self) -> None:
        self.view.setCameraPosition(
            distance=300,
            elevation=28,
            azimuth=35,
        )

    def set_wireframe(self, enabled: bool) -> None:
        self.wireframe_enabled = enabled

        if self.current_mesh is not None:
            self.show_mesh(self.current_mesh)