from dataclasses import dataclass

import numpy as np

from src.models.height_map import HeightMap


@dataclass
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

        profiles = []

        positions = np.linspace(
            0,
            height_map.width - 1,
            slice_count,
            dtype=int,
        )

        for x in positions:
            column = height_map.data[:, x]

            profiles.append(
                SliceProfile(
                    x=x,
                    heights=column.copy(),
                )
            )

        return profiles