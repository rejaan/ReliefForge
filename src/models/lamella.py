from dataclasses import dataclass

import numpy as np


@dataclass(slots=True)
class Lamella:
    """Geometric description of one relief lamella."""

    center_x_mm: float
    thickness_mm: float
    y_positions_mm: np.ndarray
    depth_values_mm: np.ndarray

    def __post_init__(self) -> None:
        self.y_positions_mm = np.asarray(
            self.y_positions_mm,
            dtype=np.float32,
        )

        self.depth_values_mm = np.asarray(
            self.depth_values_mm,
            dtype=np.float32,
        )

        if self.thickness_mm <= 0:
            raise ValueError(
                "Lamella thickness must be greater than zero."
            )

        if self.y_positions_mm.ndim != 1:
            raise ValueError(
                "y_positions_mm must be a one-dimensional array."
            )

        if self.depth_values_mm.ndim != 1:
            raise ValueError(
                "depth_values_mm must be a one-dimensional array."
            )

        if len(self.y_positions_mm) < 2:
            raise ValueError(
                "A lamella requires at least two profile points."
            )

        if len(self.y_positions_mm) != len(self.depth_values_mm):
            raise ValueError(
                "Position and depth arrays must have the same length."
            )

        if np.any(np.diff(self.y_positions_mm) < 0):
            raise ValueError(
                "The Y positions must be ordered from low to high."
            )

        if np.any(self.depth_values_mm < 0):
            raise ValueError(
                "Lamella depth values cannot be negative."
            )

    @property
    def left_x_mm(self) -> float:
        return self.center_x_mm - self.thickness_mm / 2.0

    @property
    def right_x_mm(self) -> float:
        return self.center_x_mm + self.thickness_mm / 2.0

    @property
    def point_count(self) -> int:
        return len(self.y_positions_mm)

    @property
    def maximum_depth_mm(self) -> float:
        return float(np.max(self.depth_values_mm))

    @property
    def height_mm(self) -> float:
        return float(
            self.y_positions_mm[-1] - self.y_positions_mm[0]
        )