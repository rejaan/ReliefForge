from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from src.engine.v4.spline_utils import SplineUtils


@dataclass(slots=True)
class SplineProfile:
    """Smooth one-dimensional relief profile."""

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

        if self.y_positions_mm.ndim != 1:
            raise ValueError(
                "y_positions_mm must be one-dimensional."
            )

        if self.depth_values_mm.ndim != 1:
            raise ValueError(
                "depth_values_mm must be one-dimensional."
            )

        if len(self.y_positions_mm) != len(self.depth_values_mm):
            raise ValueError(
                "Position and depth arrays must have the same length."
            )

        if len(self.y_positions_mm) < 2:
            raise ValueError(
                "A spline profile requires at least two points."
            )

        if np.any(np.diff(self.y_positions_mm) <= 0):
            raise ValueError(
                "Y positions must be strictly increasing."
            )

        if np.any(self.depth_values_mm < 0):
            raise ValueError(
                "Depth values cannot be negative."
            )

    @property
    def point_count(self) -> int:
        return len(self.y_positions_mm)

    @property
    def height_mm(self) -> float:
        return float(
            self.y_positions_mm[-1]
            - self.y_positions_mm[0]
        )

    @property
    def maximum_depth_mm(self) -> float:
        return float(
            np.max(self.depth_values_mm)
        )

    @classmethod
    def from_samples(
        cls,
        depth_values_mm: np.ndarray,
        model_height_mm: float,
        samples_per_segment: int = 4,
        smoothing_radius: int = 1,
    ) -> "SplineProfile":
        """
        Creates a smooth profile from raw depth samples.

        The raw samples are optionally smoothed first and then
        upsampled with Catmull-Rom interpolation.
        """

        values = np.asarray(
            depth_values_mm,
            dtype=np.float32,
        )

        if values.ndim != 1:
            raise ValueError(
                "depth_values_mm must be one-dimensional."
            )

        if len(values) < 2:
            raise ValueError(
                "At least two depth samples are required."
            )

        if model_height_mm <= 0:
            raise ValueError(
                "model_height_mm must be greater than zero."
            )

        if np.any(values < 0):
            raise ValueError(
                "Depth values cannot be negative."
            )

        smoothed_values = SplineUtils.gaussian(
            values,
            radius=max(0, int(smoothing_radius)),
        )

        interpolated_values = SplineUtils.catmull_rom(
            smoothed_values,
            samples_per_segment=max(
                1,
                int(samples_per_segment),
            ),
        )

        interpolated_values = np.clip(
            interpolated_values,
            0.0,
            None,
        ).astype(np.float32)

        y_positions = np.linspace(
            0.0,
            float(model_height_mm),
            len(interpolated_values),
            dtype=np.float32,
        )

        return cls(
            y_positions_mm=y_positions,
            depth_values_mm=interpolated_values,
        )