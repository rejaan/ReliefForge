from pathlib import Path

import cv2
import numpy as np

from src.models.height_map import HeightMap


class ImageProcessor:
    """Loads and prepares images for the relief engine."""

    @staticmethod
    def load(image_path: str) -> HeightMap:
        path = Path(image_path)

        if not path.exists():
            raise FileNotFoundError(image_path)

        image = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)

        if image is None:
            raise ValueError("Image could not be loaded.")

        return HeightMap(image)

    @staticmethod
    def equalize(height_map: HeightMap) -> HeightMap:
        image = cv2.equalizeHist(height_map.data)
        return HeightMap(image)

    @staticmethod
    def blur(height_map: HeightMap, kernel_size: int = 3) -> HeightMap:
        image = cv2.GaussianBlur(
            height_map.data,
            (kernel_size, kernel_size),
            0,
        )
        return HeightMap(image)

    @staticmethod
    def resize(
        height_map: HeightMap,
        width: int,
        height: int,
    ) -> HeightMap:
        image = cv2.resize(
            height_map.data,
            (width, height),
            interpolation=cv2.INTER_AREA,
        )

        return HeightMap(image)