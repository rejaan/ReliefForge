import traceback

import trimesh
from PySide6.QtCore import QObject, Signal, Slot

from src.engine.relief_generator_v2 import ReliefGeneratorV2
from src.models.relief_settings import ReliefSettings


class MeshWorker(QObject):
    """Generates a relief mesh outside the main GUI thread."""

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
        from time import perf_counter

        try:
            start_time = perf_counter()

            mesh: trimesh.Trimesh = ReliefGeneratorV2.generate_mesh(
                image_path=self.image_path,
                settings=self.settings,
            )

            generation_time = perf_counter() - start_time

            self.finished.emit(mesh, generation_time)

        except Exception:
            self.failed.emit(traceback.format_exc())