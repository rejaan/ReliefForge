from pathlib import Path

import cv2
import numpy as np
import trimesh


class MeshGenerator:
    @staticmethod
    def create_slice_mesh(
        image_path: str,
        width_mm: float = 180.0,
        height_mm: float = 130.0,
        slice_count: int = 80,
        slice_thickness_mm: float = 0.8,
        base_depth_mm: float = 2.0,
        relief_depth_mm: float = 12.0,
        profile_samples: int = 180,
    ) -> trimesh.Trimesh:
        path = Path(image_path)

        if not path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        image = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)

        if image is None:
            raise ValueError("Image could not be loaded.")

        slice_count = max(10, int(slice_count))
        profile_samples = max(20, int(profile_samples))
        slice_thickness_mm = max(0.2, float(slice_thickness_mm))
        base_depth_mm = max(0.4, float(base_depth_mm))
        relief_depth_mm = max(0.5, float(relief_depth_mm))

        image = cv2.resize(
            image,
            (slice_count, profile_samples),
            interpolation=cv2.INTER_AREA,
        )

        image = cv2.GaussianBlur(image, (3, 3), 0)

        # Dunkle Bildbereiche erzeugen mehr Tiefe.
        depth_map = 1.0 - image.astype(np.float32) / 255.0

        x_positions = np.linspace(
            -width_mm / 2.0,
            width_mm / 2.0,
            slice_count,
        )

        y_positions = np.linspace(
            0.0,
            height_mm,
            profile_samples,
        )

        meshes: list[trimesh.Trimesh] = []

        # Gemeinsame Grundplatte
        base = trimesh.creation.box(
            extents=[
                width_mm + slice_thickness_mm,
                base_depth_mm,
                height_mm,
            ]
        )

        base.apply_translation(
            [
                0.0,
                base_depth_mm / 2.0,
                height_mm / 2.0,
            ]
        )

        meshes.append(base)

        for slice_index, x_position in enumerate(x_positions):
            profile = depth_map[:, slice_index] * relief_depth_mm

            vertices = []
            faces = []

            # Pro Höhenpunkt entstehen vier Eckpunkte:
            # vorne links/rechts und hinten links/rechts.
            for row, z_position in enumerate(y_positions):
                depth = base_depth_mm + float(profile[row])

                x_left = x_position - slice_thickness_mm / 2.0
                x_right = x_position + slice_thickness_mm / 2.0

                vertices.extend(
                    [
                        [x_left, 0.0, z_position],
                        [x_right, 0.0, z_position],
                        [x_left, depth, z_position],
                        [x_right, depth, z_position],
                    ]
                )

            for row in range(profile_samples - 1):
                current = row * 4
                nxt = (row + 1) * 4

                # Vorderseite
                faces.extend(
                    [
                        [current, nxt, current + 1],
                        [current + 1, nxt, nxt + 1],
                    ]
                )

                # Rückseite
                faces.extend(
                    [
                        [current + 2, current + 3, nxt + 2],
                        [current + 3, nxt + 3, nxt + 2],
                    ]
                )

                # Linke Seite
                faces.extend(
                    [
                        [current, current + 2, nxt],
                        [current + 2, nxt + 2, nxt],
                    ]
                )

                # Rechte Seite
                faces.extend(
                    [
                        [current + 1, nxt + 1, current + 3],
                        [current + 3, nxt + 1, nxt + 3],
                    ]
                )

            # Unterseite schließen
            faces.extend(
                [
                    [0, 1, 2],
                    [1, 3, 2],
                ]
            )

            # Oberseite schließen
            last = (profile_samples - 1) * 4
            faces.extend(
                [
                    [last, last + 2, last + 1],
                    [last + 1, last + 2, last + 3],
                ]
            )

            slice_mesh = trimesh.Trimesh(
                vertices=np.asarray(vertices),
                faces=np.asarray(faces),
                process=True,
            )

            meshes.append(slice_mesh)

        combined = trimesh.util.concatenate(meshes)

        combined.remove_unreferenced_vertices()
        combined.merge_vertices()

        return combined