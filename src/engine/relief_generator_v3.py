from pathlib import Path

import numpy as np
import trimesh

from src.engine.export import STLExporter
from src.engine.geometry.lamella_builder import LamellaBuilder
from src.engine.geometry.mesh_assembler import MeshAssembler
from src.engine.geometry.profile_generator import ProfileGenerator
from src.engine.geometry.trimesh_builder import TrimeshBuilder
from src.engine.processors.image_processing import ImageProcessor
from src.models.lamella import Lamella
from src.models.relief_settings import ReliefSettings


class ReliefGeneratorV3:
    """Generates sliced relief meshes using individual Lamella objects."""

    @staticmethod
    def generate_mesh(
        image_path: str,
        settings: ReliefSettings,
    ) -> trimesh.Trimesh:
        path = Path(image_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Image not found: {image_path}"
            )

        ReliefGeneratorV3._validate_settings(settings)

        height_map = ImageProcessor.load(str(path))

        if settings.equalize_histogram:
            height_map = ImageProcessor.equalize(height_map)

        if settings.blur_kernel > 1:
            kernel_size = int(settings.blur_kernel)

            if kernel_size % 2 == 0:
                kernel_size += 1

            height_map = ImageProcessor.blur(
                height_map,
                kernel_size=kernel_size,
            )

        profiles = ProfileGenerator.generate(
            height_map=height_map,
            slice_count=settings.slice_count,
        )

        if len(profiles) < 2:
            raise ValueError(
                "At least two slice profiles are required."
            )

        source_width = max(
            float(profiles[-1].x - profiles[0].x),
            1.0,
        )

        source_height = float(
            len(profiles[0].heights) - 1
        )

        model_height_mm = (
            settings.model_width_mm
            * source_height
            / source_width
        )

        lamellas = ReliefGeneratorV3._create_lamellas(
            profiles=profiles,
            settings=settings,
            model_height_mm=model_height_mm,
        )

        mesh_data = MeshAssembler.build(lamellas)
        mesh = TrimeshBuilder.build(mesh_data)

        if mesh.is_empty:
            raise ValueError(
                "Generated V3 mesh is empty."
            )

        return mesh

    @staticmethod
    def _create_lamellas(
        profiles,
        settings: ReliefSettings,
        model_height_mm: float,
    ) -> list[Lamella]:
        ordered_profiles = list(profiles)

        # Korrigiert die horizontale Spiegelung.
        if settings.mirror_horizontal:
            ordered_profiles.reverse()

        slice_count = len(ordered_profiles)

        nominal_pitch = (
            settings.model_width_mm
            / float(slice_count - 1)
        )

        maximum_thickness = max(
            0.1,
            nominal_pitch - settings.slice_spacing_mm,
        )

        actual_thickness = min(
            settings.slice_thickness_mm,
            maximum_thickness,
        )

        half_thickness = actual_thickness / 2.0

        center_positions = np.linspace(
            half_thickness,
            settings.model_width_mm - half_thickness,
            slice_count,
            dtype=np.float32,
        )

        lamellas: list[Lamella] = []

        for profile, center_x in zip(
            ordered_profiles,
            center_positions,
        ):
            lamella = LamellaBuilder.build(
                profile=profile,
                center_x_mm=float(center_x),
                model_height_mm=model_height_mm,
                base_thickness_mm=settings.base_thickness_mm,
                relief_depth_mm=settings.relief_depth_mm,
                thickness_mm=actual_thickness,
                invert=settings.invert,
                contrast=settings.depth_contrast,
                background_cutoff=settings.background_cutoff,
            )

            lamellas.append(lamella)

        return lamellas

    @staticmethod
    def _validate_settings(
        settings: ReliefSettings,
    ) -> None:
        if settings.slice_count < 2:
            raise ValueError(
                "Slice count must be at least 2."
            )

        if settings.model_width_mm <= 0:
            raise ValueError(
                "Model width must be greater than zero."
            )

        if settings.base_thickness_mm < 0:
            raise ValueError(
                "Base thickness cannot be negative."
            )

        if settings.relief_depth_mm <= 0:
            raise ValueError(
                "Relief depth must be greater than zero."
            )

        if settings.slice_thickness_mm <= 0:
            raise ValueError(
                "Slice thickness must be greater than zero."
            )

        if settings.slice_spacing_mm < 0:
            raise ValueError(
                "Slice spacing cannot be negative."
            )

        if settings.depth_contrast <= 0:
            raise ValueError(
                "Depth contrast must be greater than zero."
            )

        if not 0.0 <= settings.background_cutoff < 1.0:
            raise ValueError(
                "Background cutoff must be between 0.0 and 1.0."
            )

    @staticmethod
    def export_stl(
        image_path: str,
        output_path: str,
        settings: ReliefSettings,
    ) -> trimesh.Trimesh:
        mesh = ReliefGeneratorV3.generate_mesh(
            image_path=image_path,
            settings=settings,
        )

        STLExporter.export(
            mesh=mesh,
            output_path=output_path,
        )

        return mesh