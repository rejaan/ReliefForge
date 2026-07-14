from __future__ import annotations

from dataclasses import dataclass

from src.engine.analyzer.detail_analyzer import DetailAnalysis


@dataclass(slots=True)
class ImageClassification:
    image_type: str
    confidence: float


class ImageClassifier:
    """
    Simple rule-based image classifier.

    Possible classes:
        - logo
        - text
        - portrait
        - landscape
        - general
    """

    @staticmethod
    def classify(
        analysis: DetailAnalysis,
    ) -> ImageClassification:

        aspect_ratio = (
            analysis.width / analysis.height
        )

        # Logo
        if (
            analysis.edge_density > 0.12
            and analysis.contrast > 60
        ):
            return ImageClassification(
                "logo",
                0.90,
            )

        # Text / Icons
        if (
            analysis.edge_density > 0.08
            and analysis.detail_score < 0.35
        ):
            return ImageClassification(
                "text",
                0.80,
            )

        # Landscape
        if (
            aspect_ratio > 1.4
            and analysis.detail_score > 0.45
        ):
            return ImageClassification(
                "landscape",
                0.75,
            )

        # Portrait
        if (
            analysis.edge_density < 0.08
            and analysis.contrast < 55
        ):
            return ImageClassification(
                "portrait",
                0.70,
            )

        return ImageClassification(
            "general",
            0.50,
        )