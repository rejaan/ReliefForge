from __future__ import annotations

import cv2
import numpy as np

from .adaptive_slice_planner import SlicePlan


class PlannerVisualizer:
    """
    Creates a debug image showing
    where slices will be placed.
    """

    @staticmethod
    def draw(
        image: np.ndarray,
        plan: SlicePlan,
    ) -> np.ndarray:

        if image.ndim == 2:
            output = cv2.cvtColor(
                image,
                cv2.COLOR_GRAY2BGR,
            )
        else:
            output = image.copy()

        h, w = output.shape[:2]

        for x in plan.slice_positions:

            x = int(round(x))

            cv2.line(
                output,
                (x, 0),
                (x, h),
                (0, 255, 0),
                1,
                cv2.LINE_AA,
            )

        return output