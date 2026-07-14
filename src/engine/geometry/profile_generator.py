from dataclasses import dataclass

import cv2
import numpy as np

from src.models.height_map import HeightMap


@dataclass(slots=True)
class SliceProfile:
    x: int
    heights: np.ndarray


class ProfileGenerator:
    """Creates slice profiles from a HeightMap."""

    @staticmethod
    def generate(
        height_map: HeightMap,
        slice_count: int,
    ) -> list[SliceProfile]:

        positions = np.linspace(
            0,
            height_map.width - 1,
            slice_count,
            dtype=np.int32,
        )

        return ProfileGenerator.generate_at_positions(
            height_map,
            positions,
        )

    @staticmethod
    def generate_at_positions(
        height_map: HeightMap,
        positions: np.ndarray,
    ) -> list[SliceProfile]:

        image = height_map.data.astype(np.float32)

        # Neue Glättung über beide Achsen
        image = cv2.GaussianBlur(
            image,
            (5, 5),
            0,
        )

        profiles = []

        width = image.shape[1]

        for x in positions:

            x = int(np.clip(x, 0, width - 1))

            profiles.append(
                SliceProfile(
                    x=x,
                    heights=image[:, x].copy(),
                )
            )

        return profiles