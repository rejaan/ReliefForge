import trimesh

from src.engine.geometry.mesh_builder import MeshData


class TrimeshBuilder:
    """Converts MeshData into a trimesh mesh."""

    @staticmethod
    def build(mesh_data: MeshData) -> trimesh.Trimesh:
        mesh = trimesh.Trimesh(
            vertices=mesh_data.vertices,
            faces=mesh_data.faces,
            process=True,
        )

        mesh.remove_unreferenced_vertices()
        mesh.merge_vertices()

        return mesh