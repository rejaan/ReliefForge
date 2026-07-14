from pathlib import Path

import trimesh

from src.engine.export import STLExporter
from src.engine.geometry.mesh_builder import MeshBuilder
from src.engine.geometry.profile_generator import ProfileGenerator
from src.engine.geometry.trimesh_builder import TrimeshBuilder
from src.engine.processors.image_processing import ImageProcessor
from src.models.relief_settings import ReliefSettings


class ReliefGeneratorV2:
    """Coordinates the complete ReliefForge V2 pipeline."""

    @staticmethod
    def generate_mesh(
        image_path: str,
        settings: ReliefSettings,
    ) -> trimesh.Trimesh:

        path = Path(image_path)

        if not path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        height_map = ImageProcessor.load(str(path))

        if settings.equalize_histogram:
            height_map = ImageProcessor.equalize(height_map)

        if settings.blur_kernel > 1:
            height_map = ImageProcessor.blur(
                height_map,
                kernel_size=settings.blur_kernel,
            )

        profiles = ProfileGenerator.generate(
            height_map=height_map,
            slice_count=settings.slice_count,
        )

        mesh_data = MeshBuilder.build(
            profiles=profiles,
            model_width_mm=settings.model_width_mm,
            base_thickness_mm=settings.base_thickness_mm,
            relief_depth_mm=settings.relief_depth_mm,
            invert=settings.invert,
        )

        mesh = TrimeshBuilder.build(mesh_data)

        if mesh.is_empty:
            raise ValueError("Generated mesh is empty.")

        return mesh

    @staticmethod
    def export_stl(
        image_path: str,
        output_path: str,
        settings: ReliefSettings,
    ) -> trimesh.Trimesh:

        mesh = ReliefGeneratorV2.generate_mesh(
            image_path=image_path,
            settings=settings,
        )

        STLExporter.export(mesh, output_path)

        return mesh