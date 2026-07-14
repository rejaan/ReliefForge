from dataclasses import dataclass

import cv2
import numpy as np

from src.models.height_map import HeightMap


@dataclass(slots=True)
class AnalysisResult:
    """Contains the internal image-analysis maps used by ReliefForge."""

    height_map: np.ndarray
    edge_map: np.ndarray
    background_map: np.ndarray
    detail_map: np.ndarray


class AnalysisEngine:
    """Creates reusable analysis maps from a HeightMap."""

    @staticmethod
    def analyze(height_map: HeightMap) -> AnalysisResult:
        image = np.asarray(
            height_map.data,
            dtype=np.uint8,
        )

        if image.ndim != 2:
            raise ValueError(
                "AnalysisEngine expects a grayscale HeightMap."
            )

        # Glätten, damit JPEG-Rauschen und einzelne Pixel
        # nicht sofort als Details erkannt werden.
        smoothed = cv2.GaussianBlur(
            image,
            (5, 5),
            0,
        )

        # Höhe: dunkle Bildbereiche werden später tiefer/höher.
        height_map_array = (
            255.0 - smoothed.astype(np.float32)
        ) / 255.0

        # Kantenkarte.
        edges = cv2.Canny(
            smoothed,
            threshold1=50,
            threshold2=150,
        )

        edge_map = edges.astype(np.float32) / 255.0

        # Hintergrundkarte:
        # 1.0 = wahrscheinlich Hintergrund
        # 0.0 = wahrscheinlich Motiv
        background_map = np.clip(
            smoothed.astype(np.float32) / 255.0,
            0.0,
            1.0,
        )

        # Detailkarte kombiniert Kanten mit lokalen
        # Helligkeitsunterschieden.
        local_mean = cv2.GaussianBlur(
            smoothed,
            (11, 11),
            0,
        )

        local_difference = cv2.absdiff(
            smoothed,
            local_mean,
        ).astype(np.float32) / 255.0

        detail_map = np.clip(
            edge_map * 0.7 + local_difference * 0.3,
            0.0,
            1.0,
        )

        return AnalysisResult(
            height_map=height_map_array.astype(np.float32),
            edge_map=edge_map.astype(np.float32),
            background_map=background_map.astype(np.float32),
            detail_map=detail_map.astype(np.float32),
        )