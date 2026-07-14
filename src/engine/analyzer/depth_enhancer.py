from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np


@dataclass(slots=True)
class DepthEnhancementResult:
    """Result of adaptive depth enhancement."""

    depth_map: np.ndarray
    edge_map: np.ndarray
    local_contrast_map: np.ndarray


class DepthEnhancer:
    """Enhances relief depth using edges and local contrast."""

    @staticmethod
    def enhance(
        image: np.ndarray,
        edge_strength: float = 0.35,
        contrast_strength: float = 0.25,
        smoothing_kernel: int = 5,
    ) -> DepthEnhancementResult:
        gray = DepthEnhancer._to_grayscale(image)

        smoothing_kernel = DepthEnhancer._valid_kernel(
            smoothing_kernel
        )

        smoothed = cv2.GaussianBlur(
            gray,
            (smoothing_kernel, smoothing_kernel),
            0,
        )

        normalized = (
            smoothed.astype(np.float32) / 255.0
        )

        # Standard ReliefForge mapping:
        # dark pixels create more relief depth.
        base_depth = 1.0 - normalized

        edge_map = DepthEnhancer._create_edge_map(
            smoothed
        )

        local_contrast_map = (
            DepthEnhancer._create_local_contrast_map(
                smoothed
            )
        )

        enhanced_depth = (
            base_depth
            + edge_map * max(0.0, float(edge_strength))
            + local_contrast_map
            * max(0.0, float(contrast_strength))
        )

        enhanced_depth = cv2.GaussianBlur(
            enhanced_depth,
            (3, 3),
            0,
        )

        enhanced_depth = np.clip(
            enhanced_depth,
            0.0,
            1.0,
        ).astype(np.float32)

        return DepthEnhancementResult(
            depth_map=enhanced_depth,
            edge_map=edge_map,
            local_contrast_map=local_contrast_map,
        )

    @staticmethod
    def _to_grayscale(
        image: np.ndarray,
    ) -> np.ndarray:
        array = np.asarray(image)

        if array.ndim == 2:
            gray = array

        elif array.ndim == 3:
            if array.shape[2] == 4:
                gray = cv2.cvtColor(
                    array,
                    cv2.COLOR_BGRA2GRAY,
                )
            else:
                gray = cv2.cvtColor(
                    array,
                    cv2.COLOR_BGR2GRAY,
                )

        else:
            raise ValueError(
                "DepthEnhancer expects a 2D grayscale "
                "or 3D color image."
            )

        return np.clip(
            gray,
            0,
            255,
        ).astype(np.uint8)

    @staticmethod
    def _create_edge_map(
        gray: np.ndarray,
    ) -> np.ndarray:
        sobel_x = cv2.Sobel(
            gray,
            cv2.CV_32F,
            1,
            0,
            ksize=3,
        )

        sobel_y = cv2.Sobel(
            gray,
            cv2.CV_32F,
            0,
            1,
            ksize=3,
        )

        magnitude = cv2.magnitude(
            sobel_x,
            sobel_y,
        )

        maximum = float(np.max(magnitude))

        if maximum > 0.0:
            magnitude /= maximum

        return np.clip(
            magnitude,
            0.0,
            1.0,
        ).astype(np.float32)

    @staticmethod
    def _create_local_contrast_map(
        gray: np.ndarray,
    ) -> np.ndarray:
        local_mean = cv2.GaussianBlur(
            gray,
            (11, 11),
            0,
        )

        difference = cv2.absdiff(
            gray,
            local_mean,
        ).astype(np.float32)

        maximum = float(np.max(difference))

        if maximum > 0.0:
            difference /= maximum

        return np.clip(
            difference,
            0.0,
            1.0,
        ).astype(np.float32)

    @staticmethod
    def _valid_kernel(
        kernel_size: int,
    ) -> int:
        kernel = max(
            1,
            int(kernel_size),
        )

        if kernel % 2 == 0:
            kernel += 1

        return kernel