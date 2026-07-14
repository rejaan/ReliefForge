from __future__ import annotations

import numpy as np

from src.engine.v5.adaptive_profile import AdaptiveProfile
from src.engine.v5.adaptive_slice_planner import AdaptiveSlicePlanner
from src.models.height_map import HeightMap


class AdaptiveProfileGenerator:
    """Creates adaptive profiles with pixel and millimeter positions."""

    @staticmethod
    def generate(
        height_map: HeightMap,
        slice_count: int,
        model_width_mm: float,
        mirror_horizontal: bool = True,
    ) -> list[AdaptiveProfile]:
        if slice_count < 2:
            raise ValueError(
                "slice_count must be at least 2."
            )

        if model_width_mm <= 0:
            raise ValueError(
                "model_width_mm must be greater than zero."
            )

        image = np.asarray(
            height_map.data,
            dtype=np.uint8,
        )

        if image.ndim != 2:
            raise ValueError(
                "AdaptiveProfileGenerator expects "
                "a grayscale HeightMap."
            )

        image_width = image.shape[1]

        if image_width < 2:
            raise ValueError(
                "Image width must be at least 2 pixels."
            )

        plan = AdaptiveSlicePlanner.create_plan(
            image=image,
            slice_count=slice_count,
        )

        profiles: list[AdaptiveProfile] = []

        for position in plan.slice_positions:
            x_pixel = float(
                np.clip(
                    position,
                    0.0,
                    float(image_width - 1),
                )
            )

            column_index = int(round(x_pixel))
            column_index = int(
                np.clip(
                    column_index,
                    0,
                    image_width - 1,
                )
            )

            normalized_x = (
                x_pixel
                / float(image_width - 1)
            )

            if mirror_horizontal:
                normalized_x = 1.0 - normalized_x

            x_mm = (
                normalized_x
                * float(model_width_mm)
            )

            profiles.append(
                AdaptiveProfile(
                    x_pixel=x_pixel,
                    x_mm=x_mm,
                    heights=image[:, column_index].copy(),
                )
            )

        profiles.sort(
            key=lambda profile: profile.x_mm
        )

        return profiles