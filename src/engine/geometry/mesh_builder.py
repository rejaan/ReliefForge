from dataclasses import dataclass

import numpy as np

from src.engine.geometry.profile_generator import SliceProfile


@dataclass
class MeshData:
    vertices: np.ndarray
    faces: np.ndarray


class MeshBuilder:
    """Builds a mesh from slice profiles."""

    @staticmethod
    def build(profiles: list[SliceProfile]) -> MeshData:
        vertices = []
        faces = []

        if not profiles:
            return MeshData(
                vertices=np.empty((0, 3), dtype=np.float32),
                faces=np.empty((0, 3), dtype=np.int32),
            )

        for profile in profiles:
            for y, height in enumerate(profile.heights):
                vertices.append(
                    [
                        float(profile.x),
                        float(y),
                        float(height),
                    ]
                )

        width = len(profiles)
        height = len(profiles[0].heights)

        for x in range(width - 1):
            for y in range(height - 1):
                a = x * height + y
                b = a + 1
                c = (x + 1) * height + y
                d = c + 1

                faces.append([a, b, c])
                faces.append([b, d, c])

        return MeshData(
            vertices=np.asarray(vertices, dtype=np.float32),
            faces=np.asarray(faces, dtype=np.int32),
        )