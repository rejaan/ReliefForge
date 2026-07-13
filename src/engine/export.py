from pathlib import Path

import trimesh


class STLExporter:
    @staticmethod
    def export(mesh: trimesh.Trimesh, output_path: str) -> None:
        path = Path(output_path)

        if path.suffix.lower() != ".stl":
            path = path.with_suffix(".stl")

        path.parent.mkdir(parents=True, exist_ok=True)

        mesh.export(path)