from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np


@dataclass(slots=True)
class SlicePlan:
    slice_positions: np.ndarray
    density_map: np.ndarray
    importance_map: np.ndarray
    slice_thickness: np.ndarray


class AdaptiveSlicePlanner:
    """
    Creates a variable slice distribution based on image complexity.

    Regions with many details receive more slices and thinner lamellae.
    Smooth regions receive fewer slices and thicker lamellae.
    """

    @staticmethod
    def create_plan(
        image: np.ndarray,
        slice_count: int,
    ) -> SlicePlan:
        if slice_count < 2:
            raise ValueError(
                "slice_count must be at least 2."
            )

        if image.ndim == 3:
            gray = cv2.cvtColor(
                image,
                cv2.COLOR_BGR2GRAY,
            )
        elif image.ndim == 2:
            gray = image.copy()
        else:
            raise ValueError(
                "image must be a grayscale or color image."
            )

        gray = np.clip(
            gray,
            0,
            255,
        ).astype(np.uint8)

        if gray.shape[1] < 2:
            raise ValueError(
                "Image width must be at least 2 pixels."
            )

        gx = cv2.Sobel(
            gray,
            cv2.CV_32F,
            1,
            0,
            ksize=3,
        )

        gy = cv2.Sobel(
            gray,
            cv2.CV_32F,
            0,
            1,
            ksize=3,
        )

        gradient = cv2.magnitude(
            gx,
            gy,
        )

        gradient = cv2.GaussianBlur(
            gradient,
            (11, 11),
            0,
        )

        importance = gradient.mean(
            axis=0
        ).astype(np.float32)

        importance += 0.05

        importance_sum = float(
            importance.sum()
        )

        if importance_sum <= 0.0:
            importance = np.ones(
                gray.shape[1],
                dtype=np.float32,
            )
            importance_sum = float(
                importance.sum()
            )

        importance /= importance_sum

        cumulative = np.cumsum(
            importance
        )

        cumulative[-1] = 1.0

        sample_positions = np.linspace(
            0.0,
            1.0,
            min(slice_count, gray.shape[1]),
            dtype=np.float32,
        )

        pixel_axis = np.arange(
            gray.shape[1],
            dtype=np.float32,
        )

        slice_positions = np.interp(
            sample_positions,
            cumulative,
            pixel_axis,
        ).astype(np.float32)

        density = importance.copy()

        maximum_density = float(
            density.max()
        )

        if maximum_density > 0.0:
            density /= maximum_density

        slice_density = np.interp(
            slice_positions,
            pixel_axis,
            density,
        ).astype(np.float32)

        minimum_thickness_mm = 0.6
        maximum_thickness_mm = 1.4

        slice_thickness = (
            maximum_thickness_mm
            - slice_density
            * (
                maximum_thickness_mm
                - minimum_thickness_mm
            )
        ).astype(np.float32)

        return SlicePlan(
            slice_positions=slice_positions,
            density_map=density.astype(np.float32),
            importance_map=importance.astype(np.float32),
            slice_thickness=slice_thickness,
        )