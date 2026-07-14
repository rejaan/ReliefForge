from pathlib import Path

from src.engine.processors.image_processing import ImageProcessor
from src.engine.geometry.profile_generator import ProfileGenerator
from src.engine.geometry.mesh_builder import MeshBuilder
from src.engine.geometry.trimesh_builder import TrimeshBuilder
from src.engine.export import STLExporter


class ReliefGeneratorV2:
    """New relief generation pipeline."""

    @staticmethod
    def generate(
        image_path: str,
        output_path: str,
        slice_count: int = 100,
    ):
        image_path = Path(image_path)
        output_path = Path(output_path)

        # Schritt 1
        height_map = ImageProcessor.load(image_path)

        # Schritt 2
        profiles = ProfileGenerator.generate(
            height_map,
            slice_count=slice_count,
        )

        # Schritt 3
        mesh_data = MeshBuilder.build(profiles)

        # Schritt 4
        mesh = TrimeshBuilder.build(mesh_data)

        # Schritt 5
        STLExporter.export(mesh, output_path)