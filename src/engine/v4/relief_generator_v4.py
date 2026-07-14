from __future__ import annotations

from pathlib import Path

import numpy as np
import trimesh

from src.engine.export import STLExporter
from src.engine.geometry.profile_generator import ProfileGenerator
from src.engine.geometry.trimesh_builder import TrimeshBuilder
from src.engine.processors.image_processing import ImageProcessor
from src.engine.v4.spline_lamella_builder import SplineLamellaBuilder
from src.engine.v4.spline_mesh_builder import SplineMeshBuilder
from src.models.lamella import Lamella
from src.models.relief_settings import ReliefSettings


class ReliefGeneratorV4:
    """Generates smooth spline-based lamella relief meshes."""

    @staticmethod
    def generate_mesh(
        image_path: str,
        settings: ReliefSettings,
        samples_per_segment: int = 3,
        smoothing_radius: int = 1,
    ) -> trimesh.Trimesh:
        path = Path(image_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Image not found: {image_path}"
            )

        ReliefGeneratorV4._validate_settings(
            settings=settings,
            samples_per_segment=samples_per_segment,
            smoothing_radius=smoothing_radius,
        )

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
            float(height_map.width - 1),
            1.0,
        )

        source_height = float(
            height_map.height - 1
        )

        model_height_mm = (
            float(settings.model_width_mm)
            * source_height
            / source_width
        )

        lamellas = ReliefGeneratorV4._create_lamellas(
            profiles=profiles,
            settings=settings,
            model_height_mm=model_height_mm,
            samples_per_segment=samples_per_segment,
            smoothing_radius=smoothing_radius,
        )

        mesh_data = SplineMeshBuilder.build(
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
                "Generated V4 mesh is empty."
            )

        return mesh

    @staticmethod
    def _create_lamellas(
        profiles,
        settings: ReliefSettings,
        model_height_mm: float,
        samples_per_segment: int,
        smoothing_radius: int,
    ) -> list[Lamella]:
        ordered_profiles = list(profiles)

        if settings.mirror_horizontal:
            ordered_profiles.reverse()

        slice_count = len(ordered_profiles)

        pitch_mm = (
            float(settings.model_width_mm)
            / float(slice_count - 1)
        )

        maximum_thickness_mm = max(
            0.1,
            pitch_mm - float(settings.slice_spacing_mm),
        )

        actual_thickness_mm = min(
            float(settings.slice_thickness_mm),
            maximum_thickness_mm,
        )

        half_thickness_mm = actual_thickness_mm / 2.0

        center_positions_mm = np.linspace(
            half_thickness_mm,
            float(settings.model_width_mm)
            - half_thickness_mm,
            slice_count,
            dtype=np.float32,
        )

        lamellas: list[Lamella] = []

        for profile, center_x_mm in zip(
            ordered_profiles,
            center_positions_mm,
        ):
            lamella = SplineLamellaBuilder.build(
                profile=profile,
                center_x_mm=float(center_x_mm),
                model_height_mm=float(model_height_mm),
                base_thickness_mm=(
                    float(settings.base_thickness_mm)
                ),
                relief_depth_mm=(
                    float(settings.relief_depth_mm)
                ),
                thickness_mm=actual_thickness_mm,
                invert=settings.invert,
                contrast=float(settings.depth_contrast),
                background_cutoff=(
                    float(settings.background_cutoff)
                ),
                samples_per_segment=samples_per_segment,
                smoothing_radius=smoothing_radius,
            )

            lamellas.append(lamella)

        return lamellas

    @staticmethod
    def _validate_settings(
        settings: ReliefSettings,
        samples_per_segment: int,
        smoothing_radius: int,
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

        if settings.base_plate_thickness_mm < 0:
            raise ValueError(
                "Base plate thickness cannot be negative."
            )

        if settings.base_plate_margin_mm < 0:
            raise ValueError(
                "Base plate margin cannot be negative."
            )

        if not 0.0 <= settings.background_cutoff < 1.0:
            raise ValueError(
                "Background cutoff must be between 0 and 1."
            )

        if samples_per_segment < 1:
            raise ValueError(
                "samples_per_segment must be at least 1."
            )

        if smoothing_radius < 0:
            raise ValueError(
                "smoothing_radius cannot be negative."
            )

    @staticmethod
    def export_stl(
        image_path: str,
        output_path: str,
        settings: ReliefSettings,
        samples_per_segment: int = 3,
        smoothing_radius: int = 1,
    ) -> trimesh.Trimesh:
        mesh = ReliefGeneratorV4.generate_mesh(
            image_path=image_path,
            settings=settings,
            samples_per_segment=samples_per_segment,
            smoothing_radius=smoothing_radius,
        )

        STLExporter.export(
            mesh=mesh,
            output_path=output_path,
        )

        return mesh