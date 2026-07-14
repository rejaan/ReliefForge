from pathlib import Path

import cv2
import numpy as np

from src.engine.analyzer.depth_enhancer import (
    DepthEnhancer,
)
from src.models.height_map import HeightMap


class ImageProcessor:
    """Loads and prepares images for the relief engine."""

    @staticmethod
    def load(image_path: str) -> HeightMap:
        path = Path(image_path)

        if not path.exists():
            raise FileNotFoundError(image_path)

        image = cv2.imread(
            str(path),
            cv2.IMREAD_GRAYSCALE,
        )

        if image is None:
            raise ValueError(
                "Image could not be loaded."
            )

        return HeightMap(image)

    @staticmethod
    def equalize(
        height_map: HeightMap,
    ) -> HeightMap:

        image = cv2.equalizeHist(
            height_map.data
        )

        return HeightMap(image)

    @staticmethod
    def blur(
        height_map: HeightMap,
        kernel_size: int = 3,
    ) -> HeightMap:

        image = cv2.GaussianBlur(
            height_map.data,
            (kernel_size, kernel_size),
            0,
        )

        return HeightMap(image)

    @staticmethod
    def depth_enhance(
        height_map: HeightMap,
    ) -> HeightMap:

        result = DepthEnhancer.enhance(
            height_map.data
        )

        image = (
            result.depth_map * 255.0
        ).astype(np.uint8)

        return HeightMap(image)

    @staticmethod
    def normalize(
        height_map: HeightMap,
    ) -> HeightMap:

        image = cv2.normalize(
            height_map.data,
            None,
            0,
            255,
            cv2.NORM_MINMAX,
        )

        image = image.astype(np.uint8)

        return HeightMap(image)

    @staticmethod
    def prepare(
        image_path: str,
        *,
        equalize: bool = True,
        blur_kernel: int = 3,
        adaptive_depth: bool = True,
    ) -> HeightMap:

        height_map = ImageProcessor.load(
            image_path
        )

        if equalize:
            height_map = ImageProcessor.equalize(
                height_map
            )

        if blur_kernel > 1:

            kernel = int(blur_kernel)

            if kernel % 2 == 0:
                kernel += 1

            height_map = ImageProcessor.blur(
                height_map,
                kernel,
            )

        if adaptive_depth:
            height_map = (
                ImageProcessor.depth_enhance(
                    height_map
                )
            )

        height_map = ImageProcessor.normalize(
            height_map
        )

        return height_map

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