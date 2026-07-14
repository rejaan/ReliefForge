from __future__ import annotations

from dataclasses import dataclass

import cv2

from src.engine.analyzer.detail_analyzer import (
    DetailAnalysis,
    DetailAnalyzer,
)
from src.engine.analyzer.image_classifier import (
    ImageClassification,
    ImageClassifier,
)
from src.engine.analyzer.preset_generator import (
    PresetGenerator,
)
from src.models.relief_settings import ReliefSettings


@dataclass(slots=True)
class AnalysisResult:
    analysis: DetailAnalysis
    classification: ImageClassification
    settings: ReliefSettings


class AnalysisEngine:
    """
    Complete automatic image analysis pipeline.
    """

    @staticmethod
    def analyze(
        image_path: str,
    ) -> AnalysisResult:

        image = cv2.imread(image_path)

        if image is None:
            raise FileNotFoundError(image_path)

        analysis = DetailAnalyzer.analyze(image)

        classification = ImageClassifier.classify(
            analysis
        )

        settings = PresetGenerator.generate(
            classification
        )

        return AnalysisResult(
            analysis=analysis,
            classification=classification,
            settings=settings,
        )