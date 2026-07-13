from pathlib import Path

import cv2
import numpy as np
from PySide6.QtGui import QImage, QPixmap


class ReliefGenerator:
    @staticmethod
    def create_slice_preview(
        image_path: str,
        slice_count: int = 100,
        relief_height: int = 10,
    ) -> QPixmap:
        path = Path(image_path)

        if not path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        image = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)

        if image is None:
            raise ValueError("Image could not be loaded.")

        preview_width = 900
        preview_height = 650

        image = cv2.resize(
            image,
            (preview_width, preview_height),
            interpolation=cv2.INTER_AREA,
        )

        # Kontrast verbessern
        image = cv2.equalizeHist(image)

        # Heller Hintergrund
        canvas = np.full(
            (preview_height, preview_width),
            235,
            dtype=np.uint8,
        )

        slice_count = max(10, min(slice_count, preview_width))
        relief_height = max(1, min(relief_height, 30))

        slice_positions = np.linspace(
            0,
            preview_width - 1,
            slice_count,
            dtype=int,
        )

        spacing = max(1, preview_width // slice_count)
        line_width = max(1, int(spacing * 0.55))

        # Relief Height beeinflusst den Kontrast
        contrast_factor = 0.6 + (relief_height / 30.0) * 2.4

        for x in slice_positions:
            column = image[:, x].astype(np.float32)

            # Dunkle Bildbereiche werden zu dunklen Lamellen
            values = 255.0 - column
            values = np.clip(values * contrast_factor, 0, 255)

            for y, value in enumerate(values):
                shade = int(255 - value)

                cv2.line(
                    canvas,
                    (x, y),
                    (min(x + line_width, preview_width - 1), y),
                    shade,
                    1,
                )

        q_image = QImage(
            canvas.data,
            canvas.shape[1],
            canvas.shape[0],
            canvas.strides[0],
            QImage.Format_Grayscale8,
        ).copy()

        return QPixmap.fromImage(q_image)