from __future__ import annotations

from src.engine.analyzer.image_classifier import (
    ImageClassification,
)
from src.models.relief_settings import ReliefSettings


class PresetGenerator:
    """
    Generates ReliefForge settings from an image
    classification.
    """

    @staticmethod
    def generate(
        classification: ImageClassification,
    ) -> ReliefSettings:

        settings = ReliefSettings()

        match classification.image_type:

            case "logo":

                settings.slice_count = 60
                settings.relief_depth_mm = 8.0
                settings.depth_contrast = 1.6
                settings.background_cutoff = 0.20
                settings.blur_kernel = 1

            case "text":

                settings.slice_count = 45
                settings.relief_depth_mm = 6.0
                settings.depth_contrast = 1.8
                settings.background_cutoff = 0.30
                settings.blur_kernel = 1

            case "portrait":

                settings.slice_count = 120
                settings.relief_depth_mm = 12.0
                settings.depth_contrast = 1.1
                settings.background_cutoff = 0.05
                settings.blur_kernel = 3

            case "landscape":

                settings.slice_count = 90
                settings.relief_depth_mm = 10.0
                settings.depth_contrast = 1.2
                settings.background_cutoff = 0.10
                settings.blur_kernel = 3

            case _:

                settings.slice_count = 80
                settings.relief_depth_mm = 10.0
                settings.depth_contrast = 1.2
                settings.background_cutoff = 0.08
                settings.blur_kernel = 3

        return settings