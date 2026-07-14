from dataclasses import dataclass

import numpy as np

from src.engine.geometry.profile_generator import SliceProfile


@dataclass
class MeshData:
    """Raw vertex and face data for a 3D mesh."""

    vertices: np.ndarray
    faces: np.ndarray


class SliceMeshBuilder:
    """Builds separate printable lamellae from image slice profiles."""

    @staticmethod
    def build(
        profiles: list[SliceProfile],
        model_width_mm: float = 180.0,
        base_thickness_mm: float = 2.0,
        relief_depth_mm: float = 12.0,
        slice_thickness_mm: float = 0.8,
        slice_spacing_mm: float = 1.0,
        depth_contrast: float = 1.0,
        invert: bool = True,
    ) -> MeshData:
        if not profiles:
            return MeshData(
                vertices=np.empty((0, 3), dtype=np.float32),
                faces=np.empty((0, 3), dtype=np.int32),
            )

        slice_count = len(profiles)
        row_count = len(profiles[0].heights)

        if slice_count < 2:
            raise ValueError("At least two slice profiles are required.")

        if row_count < 2:
            raise ValueError(
                "Each profile requires at least two height values."
            )

        if any(len(profile.heights) != row_count for profile in profiles):
            raise ValueError(
                "All slice profiles must have the same length."
            )

        if model_width_mm <= 0:
            raise ValueError("Model width must be greater than zero.")

        if base_thickness_mm < 0:
            raise ValueError("Base thickness cannot be negative.")

        if relief_depth_mm <= 0:
            raise ValueError("Relief depth must be greater than zero.")

        if slice_thickness_mm <= 0:
            raise ValueError("Slice thickness must be greater than zero.")

        if slice_spacing_mm < 0:
            raise ValueError("Slice spacing cannot be negative.")

        if depth_contrast <= 0:
            raise ValueError("Depth contrast must be greater than zero.")

        source_width = max(
            float(profiles[-1].x - profiles[0].x),
            1.0,
        )
        source_height = float(row_count - 1)

        model_height_mm = (
            model_width_mm * source_height / source_width
        )

        pitch = model_width_mm / float(slice_count - 1)

        maximum_thickness = max(
            0.1,
            pitch - float(slice_spacing_mm),
        )

        actual_thickness = min(
            float(slice_thickness_mm),
            maximum_thickness,
        )

        slice_centers = np.linspace(
            0.0,
            model_width_mm,
            slice_count,
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

        for slice_index, profile in enumerate(profiles):
            grayscale = np.asarray(
                profile.heights,
                dtype=np.float32,
            )

            normalized = np.clip(
                grayscale / 255.0,
                0.0,
                1.0,
            )

            if invert:
                normalized = 1.0 - normalized

            # Contrast curve:
            # 1.0 = linear
            # above 1.0 = stronger separation
            # below 1.0 = softer depth transitions
            normalized = np.power(
                normalized,
                float(depth_contrast),
            )

            depth_values = (
                float(base_thickness_mm)
                + normalized * float(relief_depth_mm)
            )

            center_x = float(slice_centers[slice_index])
            half_thickness = actual_thickness / 2.0

            left_x = center_x - half_thickness
            right_x = center_x + half_thickness

            if slice_index == 0:
                left_x = 0.0
                right_x = actual_thickness

            elif slice_index == slice_count - 1:
                right_x = model_width_mm
                left_x = model_width_mm - actual_thickness

            vertex_offset = len(vertices)

            for row_index in range(row_count):
                y = float(y_positions[row_index])
                depth = float(depth_values[row_index])

                vertices.extend(
                    [
                        [left_x, y, 0.0],
                        [right_x, y, 0.0],
                        [left_x, y, depth],
                        [right_x, y, depth],
                    ]
                )

            def vertex_index(row: int, corner: int) -> int:
                return vertex_offset + row * 4 + corner

            for row in range(row_count - 1):
                next_row = row + 1

                left_bottom = vertex_index(row, 0)
                right_bottom = vertex_index(row, 1)
                left_top = vertex_index(row, 2)
                right_top = vertex_index(row, 3)

                next_left_bottom = vertex_index(next_row, 0)
                next_right_bottom = vertex_index(next_row, 1)
                next_left_top = vertex_index(next_row, 2)
                next_right_top = vertex_index(next_row, 3)

                # Variable-depth profile surface
                faces.append([left_top, right_top, next_left_top])
                faces.append(
                    [right_top, next_right_top, next_left_top]
                )

                # Flat underside
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

                # Left wall
                faces.append(
                    [left_bottom, left_top, next_left_bottom]
                )
                faces.append(
                    [left_top, next_left_top, next_left_bottom]
                )

                # Right wall
                faces.append(
                    [right_bottom, next_right_bottom, right_top]
                )
                faces.append(
                    [right_top, next_right_bottom, next_right_top]
                )

            # Front cap
            faces.append(
                [
                    vertex_index(0, 0),
                    vertex_index(0, 1),
                    vertex_index(0, 2),
                ]
            )
            faces.append(
                [
                    vertex_index(0, 1),
                    vertex_index(0, 3),
                    vertex_index(0, 2),
                ]
            )

            # Rear cap
            last_row = row_count - 1

            faces.append(
                [
                    vertex_index(last_row, 0),
                    vertex_index(last_row, 2),
                    vertex_index(last_row, 1),
                ]
            )
            faces.append(
                [
                    vertex_index(last_row, 1),
                    vertex_index(last_row, 2),
                    vertex_index(last_row, 3),
                ]
            )

        return MeshData(
            vertices=np.asarray(vertices, dtype=np.float32),
            faces=np.asarray(faces, dtype=np.int32),
        )