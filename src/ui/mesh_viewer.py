import numpy as np
import pyqtgraph.opengl as gl
import trimesh
from PySide6.QtWidgets import QWidget, QVBoxLayout


class MeshViewer(QWidget):
    """Interactive OpenGL viewer for ReliefForge meshes."""

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.view = gl.GLViewWidget()
        self.view.setCameraPosition(distance=250, elevation=25, azimuth=35)
        self.view.setBackgroundColor((35, 35, 35))

        layout.addWidget(self.view)

        self.mesh_item = None

        grid = gl.GLGridItem()
        grid.setSize(300, 300)
        grid.setSpacing(10, 10)
        self.view.addItem(grid)

    def show_mesh(self, mesh: trimesh.Trimesh) -> None:
        if mesh is None or mesh.is_empty:
            raise ValueError("The mesh is empty.")

        if self.mesh_item is not None:
            self.view.removeItem(self.mesh_item)

        vertices = np.asarray(mesh.vertices, dtype=np.float32)
        faces = np.asarray(mesh.faces, dtype=np.uint32)

        mesh_data = gl.MeshData(
            vertexes=vertices,
            faces=faces,
        )

        self.mesh_item = gl.GLMeshItem(
            meshdata=mesh_data,
            smooth=True,
            drawFaces=True,
            drawEdges=False,
            shader="shaded",
        )

        self.view.addItem(self.mesh_item)
        self._center_mesh(mesh)

    def load_stl(self, filename: str) -> None:
        loaded = trimesh.load(filename, force="mesh")

        if not isinstance(loaded, trimesh.Trimesh):
            raise ValueError("The file does not contain a valid mesh.")

        self.show_mesh(loaded)

    def _center_mesh(self, mesh: trimesh.Trimesh) -> None:
        center = np.asarray(mesh.bounding_box.centroid, dtype=np.float32)

        self.mesh_item.translate(
            -float(center[0]),
            -float(center[1]),
            -float(center[2]),
        )

        largest_dimension = max(float(value) for value in mesh.extents)
        camera_distance = max(50.0, largest_dimension * 2.2)

        self.view.setCameraPosition(
            distance=camera_distance,
            elevation=25,
            azimuth=35,
        )