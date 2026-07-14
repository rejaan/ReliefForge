from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(slots=True)
class AdaptiveProfile:
    """
    A profile together with its adaptive position.
    """

    x_pixel: float
    x_mm: float
    heights: np.ndarray