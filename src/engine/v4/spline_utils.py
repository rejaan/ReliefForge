from __future__ import annotations

import numpy as np


class SplineUtils:
    """
    Utility functions for smooth interpolation.
    """

    @staticmethod
    def catmull_rom(
        values: np.ndarray,
        samples_per_segment: int = 4,
    ) -> np.ndarray:
        """
        Smooth a 1D profile using Catmull-Rom interpolation.

        Parameters
        ----------
        values:
            Original profile values.

        samples_per_segment:
            Number of interpolated samples between two original points.
        """

        values = np.asarray(values, dtype=np.float32)

        if len(values) < 4:
            return values.copy()

        result = []

        pts = np.concatenate(
            (
                values[:1],
                values,
                values[-1:],
            )
        )

        for i in range(1, len(pts) - 2):

            p0 = pts[i - 1]
            p1 = pts[i]
            p2 = pts[i + 1]
            p3 = pts[i + 2]

            for t in np.linspace(
                0.0,
                1.0,
                samples_per_segment,
                endpoint=False,
            ):

                t2 = t * t
                t3 = t2 * t

                value = (
                    0.5
                    * (
                        (2.0 * p1)
                        + (-p0 + p2) * t
                        + (
                            2 * p0
                            - 5 * p1
                            + 4 * p2
                            - p3
                        )
                        * t2
                        + (
                            -p0
                            + 3 * p1
                            - 3 * p2
                            + p3
                        )
                        * t3
                    )
                )

                result.append(value)

        result.append(values[-1])

        return np.asarray(
            result,
            dtype=np.float32,
        )

    @staticmethod
    def gaussian(
        values: np.ndarray,
        radius: int = 3,
    ) -> np.ndarray:

        values = np.asarray(
            values,
            dtype=np.float32,
        )

        if radius <= 0:
            return values.copy()

        kernel_size = radius * 2 + 1

        kernel = np.ones(
            kernel_size,
            dtype=np.float32,
        )

        kernel /= kernel.sum()

        padded = np.pad(
            values,
            radius,
            mode="edge",
        )

        smoothed = np.convolve(
            padded,
            kernel,
            mode="valid",
        )

        return smoothed.astype(
            np.float32
        )