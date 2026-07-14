from dataclasses import dataclass

import numpy as np

from src.models.lamella import Lamella


@dataclass
class MeshData:
    vertices: np.ndarray
    faces: np.ndarray


class MeshAssembler:
    """Creates one mesh from multiple Lamella objects."""

    @staticmethod
    def build(
        lamellas: list[Lamella],
    ) -> MeshData:

        vertices = []
        faces = []

        for lamella in lamellas:

            offset = len(vertices)

            left = lamella.left_x_mm
            right = lamella.right_x_mm

            for y, depth in zip(
                lamella.y_positions_mm,
                lamella.depth_values_mm,
            ):

                vertices.extend(
                    [
                        [left, y, 0],
                        [right, y, 0],
                        [left, y, depth],
                        [right, y, depth],
                    ]
                )

            point_count = lamella.point_count

            def index(row, corner):
                return offset + row * 4 + corner

            for row in range(point_count - 1):

                next_row = row + 1

                lb = index(row, 0)
                rb = index(row, 1)
                lt = index(row, 2)
                rt = index(row, 3)

                nlb = index(next_row, 0)
                nrb = index(next_row, 1)
                nlt = index(next_row, 2)
                nrt = index(next_row, 3)

                # Top
                faces.append([lt, rt, nlt])
                faces.append([rt, nrt, nlt])

                # Bottom
                faces.append([lb, nlb, rb])
                faces.append([rb, nlb, nrb])

                # Left
                faces.append([lb, lt, nlb])
                faces.append([lt, nlt, nlb])

                # Right
                faces.append([rb, nrb, rt])
                faces.append([rt, nrb, nrt])

            # Front cap
            faces.append([
                index(0,0),
                index(0,1),
                index(0,2)
            ])

            faces.append([
                index(0,1),
                index(0,3),
                index(0,2)
            ])

            last = point_count-1

            # Back cap
            faces.append([
                index(last,0),
                index(last,2),
                index(last,1)
            ])

            faces.append([
                index(last,1),
                index(last,2),
                index(last,3)
            ])

        return MeshData(
            vertices=np.asarray(
                vertices,
                dtype=np.float32,
            ),
            faces=np.asarray(
                faces,
                dtype=np.int32,
            ),
        )