from dataclasses import dataclass

import numpy as np

from src.engine.processors.analysis_engine import AnalysisResult


@dataclass(slots=True)
class SlicePlan:
    """Selected horizontal image positions for adaptive lamella placement."""

    positions: np.ndarray
    scores: np.ndarray

    def __post_init__(self) -> None:
        self.positions = np.asarray(
            self.positions,
            dtype=np.int32,
        )
        self.scores = np.asarray(
            self.scores,
            dtype=np.float32,
        )

        if self.positions.ndim != 1:
            raise ValueError("positions must be one-dimensional.")

        if self.scores.ndim != 1:
            raise ValueError("scores must be one-dimensional.")

        if len(self.positions) != len(self.scores):
            raise ValueError(
                "positions and scores must have the same length."
            )


class AdaptiveSlicePlanner:
    """Chooses more slice positions in detailed image regions."""

    @staticmethod
    def plan(
        analysis: AnalysisResult,
        slice_count: int,
        edge_weight: float = 0.65,
        detail_weight: float = 0.35,
        minimum_spacing_px: int = 2,
    ) -> SlicePlan:
        if slice_count < 2:
            raise ValueError("slice_count must be at least 2.")

        edge_map = np.asarray(
            analysis.edge_map,
            dtype=np.float32,
        )
        detail_map = np.asarray(
            analysis.detail_map,
            dtype=np.float32,
        )

        if edge_map.ndim != 2 or detail_map.ndim != 2:
            raise ValueError(
                "AdaptiveSlicePlanner expects two-dimensional maps."
            )

        if edge_map.shape != detail_map.shape:
            raise ValueError(
                "edge_map and detail_map must have identical shapes."
            )

        image_height, image_width = edge_map.shape

        if image_width < 2:
            raise ValueError("Image width must be at least 2 pixels.")

        requested_count = min(
            int(slice_count),
            image_width,
        )

        edge_score = np.mean(edge_map, axis=0)
        detail_score = np.mean(detail_map, axis=0)

        combined_score = (
            edge_score * float(edge_weight)
            + detail_score * float(detail_weight)
        )

        combined_score = np.nan_to_num(
            combined_score,
            nan=0.0,
            posinf=0.0,
            neginf=0.0,
        )

        # Kleine Grundgewichtung verhindert, dass völlig ruhige
        # Bildbereiche gar keine Lamellen mehr erhalten.
        combined_score += 0.02

        # Erste und letzte Bildspalte immer berücksichtigen.
        selected_positions = {0, image_width - 1}

        candidate_positions = np.argsort(
            combined_score
        )[::-1]

        minimum_spacing = max(
            1,
            int(minimum_spacing_px),
        )

        for candidate in candidate_positions:
            candidate = int(candidate)

            if len(selected_positions) >= requested_count:
                break

            if all(
                abs(candidate - existing) >= minimum_spacing
                for existing in selected_positions
            ):
                selected_positions.add(candidate)

        # Falls durch den Mindestabstand noch Positionen fehlen,
        # werden gleichmäßig verteilte Positionen ergänzt.
        if len(selected_positions) < requested_count:
            fallback_positions = np.linspace(
                0,
                image_width - 1,
                requested_count,
                dtype=np.int32,
            )

            for candidate in fallback_positions:
                selected_positions.add(int(candidate))

                if len(selected_positions) >= requested_count:
                    break

        positions = np.asarray(
            sorted(selected_positions),
            dtype=np.int32,
        )

        # Falls mehr Positionen als verlangt vorhanden sind,
        # behalten wir die wichtigsten und sortieren anschließend erneut.
        if len(positions) > requested_count:
            ranked = sorted(
                positions,
                key=lambda position: combined_score[position],
                reverse=True,
            )[:requested_count]

            positions = np.asarray(
                sorted(ranked),
                dtype=np.int32,
            )

        scores = combined_score[positions]

        return SlicePlan(
            positions=positions,
            scores=scores,
        )