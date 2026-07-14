import numpy as np

from src.engine.geometry.profile_generator import SliceProfile
from src.models.lamella import Lamella


class LamellaBuilder:
    """Converts one image slice profile into a Lamella."""

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

        # Fast weiße beziehungsweise sehr schwache Bereiche
        # werden vollständig auf die flache Grundhöhe gesetzt.
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
            depth_values_mm=depth_values,
        )