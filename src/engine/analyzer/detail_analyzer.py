from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np


@dataclass(slots=True)
class DetailAnalysis:
    width: int
    height: int

    mean_brightness: float
    contrast: float

    edge_density: float
    sharpness: float

    detail_score: float


class DetailAnalyzer:
    """Analyzes the complexity of an image."""

    @staticmethod
    def analyze(image: np.ndarray) -> DetailAnalysis:

        if image.ndim == 3:
            gray = cv2.cvtColor(
                image,
                cv2.COLOR_BGR2GRAY,
            )
        else:
            gray = image.copy()

        gray = gray.astype(np.uint8)

        height, width = gray.shape

        mean = float(np.mean(gray))
        contrast = float(np.std(gray))

        edges = cv2.Canny(
            gray,
            80,
            160,
        )

        edge_density = float(
            np.count_nonzero(edges)
            / edges.size
        )

        laplacian = cv2.Laplacian(
            gray,
            cv2.CV_64F,
        )

        sharpness = float(
            laplacian.var()
        )

        detail_score = (
            edge_density * 0.5
            + min(sharpness / 1000.0, 1.0) * 0.5
        )

        return DetailAnalysis(
            width=width,
            height=height,
            mean_brightness=mean,
            contrast=contrast,
            edge_density=edge_density,
            sharpness=sharpness,
            detail_score=detail_score,
        )