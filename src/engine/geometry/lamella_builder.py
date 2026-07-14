import numpy as np

from src.engine.geometry.profile_generator import SliceProfile
from src.models.lamella import Lamella


class LamellaBuilder:
    """Converts one image slice profile into a printable lamella."""

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
        smooth_radius: int = 3,
    ) -> Lamella:
        grayscale = np.asarray(
            profile.heights,
            dtype=np.float32,
        )

        normalized = np.clip(
            grayscale / 255.0,
            0.0,
            1.0,
        )

        if invert:
            normalized = 1.0 - normalized

        cutoff = float(
            np.clip(background_cutoff, 0.0, 0.95)
        )

        if cutoff > 0.0:
            normalized = np.where(
                normalized <= cutoff,
                0.0,
                (normalized - cutoff) / (1.0 - cutoff),
            )

        contrast = max(
            0.1,
            float(contrast),
        )

        normalized = np.power(
            normalized,
            contrast,
        )

        normalized = LamellaBuilder._smooth_profile(
            normalized,
            radius=smooth_radius,
        )

        depth_values = (
            float(base_thickness_mm)
            + normalized * float(relief_depth_mm)
        )

        y_positions = np.linspace(
            0.0,
            float(model_height_mm),
            len(depth_values),
            dtype=np.float32,
        )

        return Lamella(
            center_x_mm=float(center_x_mm),
            thickness_mm=float(thickness_mm),
            y_positions_mm=y_positions,
            depth_values_mm=depth_values.astype(np.float32),
        )

    @staticmethod
    def _smooth_profile(
        values: np.ndarray,
        radius: int,
    ) -> np.ndarray:
        """
        Smooths the lamella profile while preserving the overall shape.

        radius:
            0 = no smoothing
            1 = light smoothing
            3 = balanced default
            5+ = stronger smoothing
        """

        radius = max(
            0,
            int(radius),
        )

        if radius == 0 or len(values) < 3:
            return values.astype(np.float32)

        kernel_size = radius * 2 + 1

        kernel = np.ones(
            kernel_size,
            dtype=np.float32,
        )

        kernel /= float(kernel_size)

        padded = np.pad(
            values,
            pad_width=radius,
            mode="edge",
        )

        smoothed = np.convolve(
            padded,
            kernel,
            mode="valid",
        )

        return np.clip(
            smoothed,
            0.0,
            1.0,
        ).astype(np.float32)