from pathlib import Path

import trimesh

from src.engine.export import STLExporter
from src.engine.geometry.lamella_builder import LamellaBuilder
from src.engine.geometry.mesh_assembler import MeshAssembler
from src.engine.geometry.trimesh_builder import TrimeshBuilder
from src.engine.processors.image_processing import ImageProcessor
from src.engine.v5.adaptive_profile_generator import (
    AdaptiveProfileGenerator,
)
from src.models.relief_settings import ReliefSettings


class ReliefGeneratorV5:
    """Adaptive V5 relief engine."""

    @staticmethod
    def generate_mesh(
        image_path: str,
        settings: ReliefSettings,
    ) -> trimesh.Trimesh:
        path = Path(image_path)

        if not path.exists():
            raise FileNotFoundError(image_path)

        height_map = ImageProcessor.prepare(
            image_path=str(path),
            equalize=settings.equalize_histogram,
            blur_kernel=settings.blur_kernel,
            adaptive_depth=True,
        )

        profiles = AdaptiveProfileGenerator.generate(
            height_map=height_map,
            slice_count=settings.slice_count,
            model_width_mm=settings.model_width_mm,
            mirror_horizontal=settings.mirror_horizontal,
        )

        model_height_mm = (
            settings.model_width_mm
            * (height_map.height - 1)
            / max(height_map.width - 1, 1)
        )

        lamellas = []

        for profile in profiles:
            lamella = LamellaBuilder.build(
                profile=profile,
                center_x_mm=profile.x_mm,
                model_height_mm=model_height_mm,
                base_thickness_mm=settings.base_thickness_mm,
                relief_depth_mm=settings.relief_depth_mm,
                thickness_mm=settings.slice_thickness_mm,
                invert=False,
                contrast=settings.depth_contrast,
                background_cutoff=settings.background_cutoff,
            )

            lamellas.append(lamella)

        mesh_data = MeshAssembler.build(
            lamellas=lamellas,
            base_plate_enabled=settings.base_plate_enabled,
            base_plate_thickness_mm=(
                settings.base_plate_thickness_mm
            ),
            base_plate_margin_mm=(
                settings.base_plate_margin_mm
            ),
        )

        mesh = TrimeshBuilder.build(mesh_data)

        if mesh.is_empty:
            raise ValueError(
                "Generated V5 mesh is empty."
            )

        return mesh

    @staticmethod
    def export_stl(
        image_path: str,
        output_path: str,
        settings: ReliefSettings,
    ) -> trimesh.Trimesh:
        mesh = ReliefGeneratorV5.generate_mesh(
            image_path=image_path,
            settings=settings,
        )

        STLExporter.export(
            mesh=mesh,
            output_path=output_path,
        )

        return mesh