from dataclasses import dataclass

import numpy as np

from src.models.lamella import Lamella


@dataclass
class MeshData:
    """Raw vertex and face data for a 3D mesh."""

    vertices: np.ndarray
    faces: np.ndarray


class MeshAssembler:
    """Creates a printable mesh from multiple lamellae."""

    @staticmethod
    def build(
        lamellas: list[Lamella],
        base_plate_enabled: bool = True,
        base_plate_thickness_mm: float = 2.0,
        base_plate_margin_mm: float = 1.0,
    ) -> MeshData:
        if not lamellas:
            return MeshData(
                vertices=np.empty((0, 3), dtype=np.float32),
                faces=np.empty((0, 3), dtype=np.int32),
            )

        vertices: list[list[float]] = []
        faces: list[list[int]] = []

        for lamella in lamellas:
            MeshAssembler._add_lamella(
                lamella=lamella,
                vertices=vertices,
                faces=faces,
            )

        if base_plate_enabled:
            MeshAssembler._add_base_plate(
                lamellas=lamellas,
                thickness_mm=base_plate_thickness_mm,
                margin_mm=base_plate_margin_mm,
                vertices=vertices,
                faces=faces,
            )

        return MeshData(
            vertices=np.asarray(vertices, dtype=np.float32),
            faces=np.asarray(faces, dtype=np.int32),
        )

    @staticmethod
    def _add_lamella(
        lamella: Lamella,
        vertices: list[list[float]],
        faces: list[list[int]],
    ) -> None:
        offset = len(vertices)

        left_x = float(lamella.left_x_mm)
        right_x = float(lamella.right_x_mm)

        for y_position, depth in zip(
            lamella.y_positions_mm,
            lamella.depth_values_mm,
        ):
            y = float(y_position)
            z = float(depth)

            vertices.extend(
                [
                    [left_x, y, 0.0],
                    [right_x, y, 0.0],
                    [left_x, y, z],
                    [right_x, y, z],
                ]
            )

        def index(row: int, corner: int) -> int:
            return offset + row * 4 + corner

        for row in range(lamella.point_count - 1):
            next_row = row + 1

            left_bottom = index(row, 0)
            right_bottom = index(row, 1)
            left_top = index(row, 2)
            right_top = index(row, 3)

            next_left_bottom = index(next_row, 0)
            next_right_bottom = index(next_row, 1)
            next_left_top = index(next_row, 2)
            next_right_top = index(next_row, 3)

            # Profiloberseite
            faces.append([left_top, right_top, next_left_top])
            faces.append(
                [right_top, next_right_top, next_left_top]
            )

            # Unterseite
            faces.append(
                [left_bottom, next_left_bottom, right_bottom]
            )
            faces.append(
                [
                    right_bottom,
                    next_left_bottom,
                    next_right_bottom,
                ]
            )

            # Linke Seitenwand
            faces.append(
                [left_bottom, left_top, next_left_bottom]
            )
            faces.append(
                [left_top, next_left_top, next_left_bottom]
            )

            # Rechte Seitenwand
            faces.append(
                [right_bottom, next_right_bottom, right_top]
            )
            faces.append(
                [right_top, next_right_bottom, next_right_top]
            )

        # Vorderseite
        faces.append(
            [
                index(0, 0),
                index(0, 1),
                index(0, 2),
            ]
        )
        faces.append(
            [
                index(0, 1),
                index(0, 3),
                index(0, 2),
            ]
        )

        # Rückseite
        last_row = lamella.point_count - 1

        faces.append(
            [
                index(last_row, 0),
                index(last_row, 2),
                index(last_row, 1),
            ]
        )
        faces.append(
            [
                index(last_row, 1),
                index(last_row, 2),
                index(last_row, 3),
            ]
        )

    @staticmethod
    def _add_base_plate(
        lamellas: list[Lamella],
        thickness_mm: float,
        margin_mm: float,
        vertices: list[list[float]],
        faces: list[list[int]],
    ) -> None:
        if thickness_mm <= 0:
            return

        margin = max(0.0, float(margin_mm))

        minimum_x = min(
            lamella.left_x_mm for lamella in lamellas
        ) - margin

        maximum_x = max(
            lamella.right_x_mm for lamella in lamellas
        ) + margin

        minimum_y = min(
            float(lamella.y_positions_mm[0])
            for lamella in lamellas
        ) - margin

        maximum_y = max(
            float(lamella.y_positions_mm[-1])
            for lamella in lamellas
        ) + margin

        bottom_z = -float(thickness_mm)
        top_z = 0.0

        offset = len(vertices)

        vertices.extend(
            [
                [minimum_x, minimum_y, bottom_z],  # 0
                [maximum_x, minimum_y, bottom_z],  # 1
                [maximum_x, maximum_y, bottom_z],  # 2
                [minimum_x, maximum_y, bottom_z],  # 3
                [minimum_x, minimum_y, top_z],     # 4
                [maximum_x, minimum_y, top_z],     # 5
                [maximum_x, maximum_y, top_z],     # 6
                [minimum_x, maximum_y, top_z],     # 7
            ]
        )

        def plate_index(value: int) -> int:
            return offset + value

        # Unterseite
        faces.append(
            [plate_index(0), plate_index(2), plate_index(1)]
        )
        faces.append(
            [plate_index(0), plate_index(3), plate_index(2)]
        )

        # Oberseite
        faces.append(
            [plate_index(4), plate_index(5), plate_index(6)]
        )
        faces.append(
            [plate_index(4), plate_index(6), plate_index(7)]
        )

        # Vorderseite
        faces.append(
            [plate_index(0), plate_index(1), plate_index(5)]
        )
        faces.append(
            [plate_index(0), plate_index(5), plate_index(4)]
        )

        # Rückseite
        faces.append(
            [plate_index(3), plate_index(7), plate_index(6)]
        )
        faces.append(
            [plate_index(3), plate_index(6), plate_index(2)]
        )

        # Linke Seite
        faces.append(
            [plate_index(0), plate_index(4), plate_index(7)]
        )
        faces.append(
            [plate_index(0), plate_index(7), plate_index(3)]
        )

        # Rechte Seite
        faces.append(
            [plate_index(1), plate_index(2), plate_index(6)]
        )
        faces.append(
            [plate_index(1), plate_index(6), plate_index(5)]
        )