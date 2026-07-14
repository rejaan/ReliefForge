import traceback
from time import perf_counter

import trimesh
from PySide6.QtCore import QObject, Signal, Slot

from src.engine.relief_generator_v3 import ReliefGeneratorV3
from src.engine.v4.relief_generator_v4 import ReliefGeneratorV4
from src.engine.v5.relief_generator_v5 import ReliefGeneratorV5
from src.models.relief_settings import ReliefSettings


class MeshWorker(QObject):
    """Generates the selected relief engine outside the GUI thread."""

    finished = Signal(object, float)
    failed = Signal(str)

    def __init__(
        self,
        image_path: str,
        settings: ReliefSettings,
    ):
        super().__init__()

        self.image_path = image_path
        self.settings = settings

    @Slot()
    def run(self) -> None:
        try:
            start_time = perf_counter()

            engine = self.settings.engine_version

            print(f"Generating with engine: {engine}")

            if engine == "v5":
                mesh: trimesh.Trimesh = (
                    ReliefGeneratorV5.generate_mesh(
                        image_path=self.image_path,
                        settings=self.settings,
                    )
                )

            elif engine == "v4":
                mesh = ReliefGeneratorV4.generate_mesh(
                    image_path=self.image_path,
                    settings=self.settings,
                    samples_per_segment=2,
                    smoothing_radius=0,
                )

            else:
                mesh = ReliefGeneratorV3.generate_mesh(
                    image_path=self.image_path,
                    settings=self.settings,
                )

            generation_time = perf_counter() - start_time

            print(
                f"Finished {engine}: "
                f"{len(mesh.vertices)} vertices, "
                f"{len(mesh.faces)} faces"
            )

            self.finished.emit(
                mesh,
                generation_time,
            )

        except Exception:
            self.failed.emit(
                traceback.format_exc()
            )