from __future__ import annotations

import numpy as np

from src.engine.geometry.profile_generator import SliceProfile
from src.engine.v4.spline_profile import SplineProfile
from src.models.lamella import Lamella


class SplineLamellaBuilder:
    """Builds a smooth lamella from one image slice profile."""

    @staticmethod
    def build(
        profile: SliceProfile,
        center_x_mm: float,
        model_height_mm: float,
        base_thickness_mm: float,
        relief_depth_mm: float,
        thickness_mm: float,
        invert: bool = True,
        contrast: float = 1.0,
        background_cutoff: float = 0.08,
        samples_per_segment: int = 3,
        smoothing_radius: int = 1,
    ) -> Lamella:
        grayscale = np.asarray(
            profile.heights,
            dtype=np.float32,
        )

        if grayscale.ndim != 1:
            raise ValueError(
                "Profile heights must be one-dimensional."
            )

        if len(grayscale) < 2:
            raise ValueError(
                "A profile requires at least two height samples."
            )

        if model_height_mm <= 0:
            raise ValueError(
                "model_height_mm must be greater than zero."
            )

        if relief_depth_mm <= 0:
            raise ValueError(
                "relief_depth_mm must be greater than zero."
            )

        if thickness_mm <= 0:
            raise ValueError(
                "thickness_mm must be greater than zero."
            )

        normalized = np.clip(
            grayscale / 255.0,
            0.0,
            1.0,
        )

        if invert:
            normalized = 1.0 - normalized

        cutoff = float(
            np.clip(
                background_cutoff,
                0.0,
                0.95,
            )
        )

        if cutoff > 0.0:
            normalized = np.where(
                normalized <= cutoff,
                0.0,
                (normalized - cutoff) / (1.0 - cutoff),
            )

        normalized = np.power(
            normalized,
            max(0.1, float(contrast)),
        )

        raw_depth_values = (
            float(base_thickness_mm)
            + normalized * float(relief_depth_mm)
        )

        spline_profile = SplineProfile.from_samples(
            depth_values_mm=raw_depth_values,
            model_height_mm=float(model_height_mm),
            samples_per_segment=max(
                1,
                int(samples_per_segment),
            ),
            smoothing_radius=max(
                0,
                int(smoothing_radius),
            ),
        )

        return Lamella(
            center_x_mm=float(center_x_mm),
            thickness_mm=float(thickness_mm),
            y_positions_mm=spline_profile.y_positions_mm,
            depth_values_mm=spline_profile.depth_values_mm,
        )