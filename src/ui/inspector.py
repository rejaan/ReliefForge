from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFormLayout,
    QFrame,
    QLabel,
    QVBoxLayout,
)

import trimesh


class Inspector(QFrame):
    """Displays information about the current relief model."""

    def __init__(self):
        super().__init__()

        self.setObjectName("inspectorFrame")

        self.setStyleSheet("""
        QFrame#inspectorFrame{
            background:#25262a;
            border:1px solid #34373d;
            border-radius:8px;
        }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14,14,14,14)

        title = QLabel("Model Information")
        title.setStyleSheet("""
        font-size:16px;
        font-weight:bold;
        """)

        layout.addWidget(title)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignLeft)

        self.image = QLabel("—")
        self.resolution = QLabel("—")
        self.vertices = QLabel("—")
        self.faces = QLabel("—")
        self.dimensions = QLabel("—")
        self.generation = QLabel("—")
        self.watertight = QLabel("—")

        form.addRow("Image", self.image)
        form.addRow("Resolution", self.resolution)
        form.addRow("Vertices", self.vertices)
        form.addRow("Faces", self.faces)
        form.addRow("Dimensions", self.dimensions)
        form.addRow("Generation", self.generation)
        form.addRow("Watertight", self.watertight)

        layout.addLayout(form)

    def clear(self):
        self.image.setText("—")
        self.resolution.setText("—")
        self.vertices.setText("—")
        self.faces.setText("—")
        self.dimensions.setText("—")
        self.generation.setText("—")
        self.watertight.setText("—")

    def set_image(self, filename: str):
        self.image.setText(filename)

    def set_resolution(self, width: int, height: int):
        self.resolution.setText(f"{width} × {height}")

    def update_mesh(
        self,
        mesh: trimesh.Trimesh,
        generation_time: float,
    ):
        self.vertices.setText(f"{len(mesh.vertices):,}")
        self.faces.setText(f"{len(mesh.faces):,}")

        x, y, z = mesh.extents

        self.dimensions.setText(
            f"{x:.1f} × {y:.1f} × {z:.1f} mm"
        )

        self.generation.setText(
            f"{generation_time:.2f} s"
        )

        self.watertight.setText(
            "Yes" if mesh.is_watertight else "No"
        )