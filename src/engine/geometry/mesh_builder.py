from dataclasses import dataclass

import numpy as np

from src.engine.geometry.profile_generator import SliceProfile


@dataclass
class MeshData:
    vertices: np.ndarray
    faces: np.ndarray


class MeshBuilder:
    """Builds a closed relief mesh from slice profiles."""

    @staticmethod
    def build(
        profiles: list[SliceProfile],
        model_width_mm: float = 180.0,
        base_thickness_mm: float = 2.0,
        relief_depth_mm: float = 12.0,
        invert: bool = True,
    ) -> MeshData:
        if not profiles:
            return MeshData(
                vertices=np.empty((0, 3), dtype=np.float32),
                faces=np.empty((0, 3), dtype=np.int32),
            )

        column_count = len(profiles)
        row_count = len(profiles[0].heights)

        if column_count < 2 or row_count < 2:
            raise ValueError(
                "At least two profiles with two height values are required."
            )

        if any(len(profile.heights) != row_count for profile in profiles):
            raise ValueError("All slice profiles must have the same length.")

        source_width = max(
            float(profiles[-1].x - profiles[0].x),
            1.0,
        )
        source_height = float(row_count - 1)

        model_height_mm = model_width_mm * (
            source_height / source_width
        )

        x_positions = np.linspace(
            0.0,
            model_width_mm,
            column_count,
            dtype=np.float32,
        )

        y_positions = np.linspace(
            0.0,
            model_height_mm,
            row_count,
            dtype=np.float32,
        )

        vertices: list[list[float]] = []
        faces: list[list[int]] = []

        # Oberseite des Reliefs
        for column_index, profile in enumerate(profiles):
            heights = np.asarray(
                profile.heights,
                dtype=np.float32,
            )

            normalized = np.clip(heights / 255.0, 0.0, 1.0)

            if invert:
                normalized = 1.0 - normalized

            z_values = (
                base_thickness_mm
                + normalized * relief_depth_mm
            )

            for row_index, z_value in enumerate(z_values):
                vertices.append(
                    [
                        float(x_positions[column_index]),
                        float(y_positions[row_index]),
                        float(z_value),
                    ]
                )

        top_vertex_count = len(vertices)

        # Flache Unterseite
        for column_index in range(column_count):
            for row_index in range(row_count):
                vertices.append(
                    [
                        float(x_positions[column_index]),
                        float(y_positions[row_index]),
                        0.0,
                    ]
                )

        def top_index(column: int, row: int) -> int:
            return column * row_count + row

        def bottom_index(column: int, row: int) -> int:
            return top_vertex_count + column * row_count + row

        # Reliefoberfläche
        for column in range(column_count - 1):
            for row in range(row_count - 1):
                a = top_index(column, row)
                b = top_index(column, row + 1)
                c = top_index(column + 1, row)
                d = top_index(column + 1, row + 1)

                faces.append([a, c, b])
                faces.append([b, c, d])

        # Unterseite
        for column in range(column_count - 1):
            for row in range(row_count - 1):
                a = bottom_index(column, row)
                b = bottom_index(column, row + 1)
                c = bottom_index(column + 1, row)
                d = bottom_index(column + 1, row + 1)

                faces.append([a, b, c])
                faces.append([b, d, c])

        # Vorder- und Rückwand
        for column in range(column_count - 1):
            # Vorderwand, row 0
            top_left = top_index(column, 0)
            top_right = top_index(column + 1, 0)
            bottom_left = bottom_index(column, 0)
            bottom_right = bottom_index(column + 1, 0)

            faces.append([bottom_left, top_right, top_left])
            faces.append([bottom_left, bottom_right, top_right])

            # Rückwand, letzte row
            last_row = row_count - 1

            top_left = top_index(column, last_row)
            top_right = top_index(column + 1, last_row)
            bottom_left = bottom_index(column, last_row)
            bottom_right = bottom_index(column + 1, last_row)

            faces.append([bottom_left, top_left, top_right])
            faces.append([bottom_left, top_right, bottom_right])

        # Linke und rechte Seitenwand
        for row in range(row_count - 1):
            # Linke Wand, column 0
            top_lower = top_index(0, row)
            top_upper = top_index(0, row + 1)
            bottom_lower = bottom_index(0, row)
            bottom_upper = bottom_index(0, row + 1)

            faces.append([bottom_lower, top_lower, top_upper])
            faces.append([bottom_lower, top_upper, bottom_upper])

            # Rechte Wand, letzte column
            last_column = column_count - 1

            top_lower = top_index(last_column, row)
            top_upper = top_index(last_column, row + 1)
            bottom_lower = bottom_index(last_column, row)
            bottom_upper = bottom_index(last_column, row + 1)

            faces.append([bottom_lower, top_upper, top_lower])
            faces.append([bottom_lower, bottom_upper, top_upper])

        return MeshData(
            vertices=np.asarray(vertices, dtype=np.float32),
            faces=np.asarray(faces, dtype=np.int32),
        )