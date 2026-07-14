from pathlib import Path

from src.engine.processors.image_processing import ImageProcessor
from src.engine.geometry.profile_generator import ProfileGenerator
from src.engine.geometry.mesh_builder import MeshBuilder
from src.engine.geometry.trimesh_builder import TrimeshBuilder
from src.engine.export import STLExporter


IMAGE = "images/testbild.png"
OUTPUT = "output/engine_v2_test.stl"


print("Loading image...")
height_map = ImageProcessor.load(IMAGE)

print("Generating profiles...")
profiles = ProfileGenerator.generate(
    height_map,
    slice_count=100,
)

print("Building mesh...")
mesh_data = MeshBuilder.build(profiles)

print("Creating trimesh...")
mesh = TrimeshBuilder.build(mesh_data)

print("Exporting STL...")
STLExporter.export(mesh, OUTPUT)

print("Done!")
print(f"Vertices: {len(mesh.vertices)}")
print(f"Faces: {len(mesh.faces)}")
print(f"Saved to: {Path(OUTPUT).resolve()}")