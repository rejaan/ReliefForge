from dataclasses import dataclass

import numpy as np


@dataclass
class HeightMap:
    """Speichert die Helligkeitswerte eines Bildes."""

    data: np.ndarray

    @property
    def width(self) -> int:
        return self.data.shape[1]

    @property
    def height(self) -> int:
        return self.data.shape[0]

    def normalized(self) -> np.ndarray:
        """Gibt Werte zwischen 0.0 und 1.0 zurück."""
        return self.data.astype(np.float32) / 255.0

    def inverted(self) -> "HeightMap":
        """Invertiert die HeightMap."""
        return HeightMap(255 - self.data)

    def copy(self) -> "HeightMap":
        return HeightMap(self.data.copy())