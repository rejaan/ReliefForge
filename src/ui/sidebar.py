from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QLabel,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from src.models.relief_settings import ReliefSettings


class Sidebar(QWidget):
    """Sidebar containing the main ReliefForge controls."""

    open_image_requested = Signal()
    refresh_requested = Signal()
    export_requested = Signal()
    settings_changed = Signal()

    def __init__(self):
        super().__init__()

        self.setFixedWidth(350)

        self._build_interface()
        self._connect_signals()

    def _build_interface(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        title = QLabel("ReliefForge")
        title.setStyleSheet(
            """
            font-size: 28px;
            font-weight: bold;
            """
        )

        version = QLabel("v0.3.4 – Background Processing")
        version.setStyleSheet("color: #888888;")

        self.open_button = QPushButton("Open Image")

        slice_label = QLabel("Slice Count")

        self.slice_slider = QSlider(Qt.Horizontal)
        self.slice_slider.setRange(20, 180)
        self.slice_slider.setValue(80)

        self.slice_value = QLabel("80")
        self.slice_value.setAlignment(Qt.AlignRight)

        depth_label = QLabel("Relief Depth")

        self.depth_slider = QSlider(Qt.Horizontal)
        self.depth_slider.setRange(2, 30)
        self.depth_slider.setValue(12)

        self.depth_value = QLabel("12 mm")
        self.depth_value.setAlignment(Qt.AlignRight)

        self.refresh_button = QPushButton("Refresh 2D + 3D")
        self.export_button = QPushButton("Export STL")

        layout.addWidget(title)
        layout.addWidget(version)

        layout.addSpacing(15)
        layout.addWidget(self.open_button)

        layout.addSpacing(20)
        layout.addWidget(slice_label)
        layout.addWidget(self.slice_slider)
        layout.addWidget(self.slice_value)

        layout.addSpacing(10)
        layout.addWidget(depth_label)
        layout.addWidget(self.depth_slider)
        layout.addWidget(self.depth_value)

        layout.addStretch()

        layout.addWidget(self.refresh_button)
        layout.addWidget(self.export_button)

    def _connect_signals(self) -> None:
        self.open_button.clicked.connect(
            self.open_image_requested.emit
        )

        self.refresh_button.clicked.connect(
            self.refresh_requested.emit
        )

        self.export_button.clicked.connect(
            self.export_requested.emit
        )

        self.slice_slider.valueChanged.connect(
            self._on_slice_count_changed
        )

        self.depth_slider.valueChanged.connect(
            self._on_relief_depth_changed
        )

    def _on_slice_count_changed(self, value: int) -> None:
        self.slice_value.setText(str(value))
        self.settings_changed.emit()

    def _on_relief_depth_changed(self, value: int) -> None:
        self.depth_value.setText(f"{value} mm")
        self.settings_changed.emit()

    def settings(self) -> ReliefSettings:
        """Returns the current relief settings."""

        return ReliefSettings(
            slice_count=self.slice_slider.value(),
            model_width_mm=180.0,
            base_thickness_mm=2.0,
            relief_depth_mm=float(self.depth_slider.value()),
            invert=True,
            blur_kernel=3,
            equalize_histogram=True,
        )

    def slice_count(self) -> int:
        return self.slice_slider.value()

    def relief_depth(self) -> int:
        return self.depth_slider.value()

    def set_busy(self, busy: bool) -> None:
        """Enables or disables controls during processing."""

        enabled = not busy

        self.open_button.setEnabled(enabled)
        self.refresh_button.setEnabled(enabled)
        self.export_button.setEnabled(enabled)
        self.slice_slider.setEnabled(enabled)
        self.depth_slider.setEnabled(enabled)

        self.refresh_button.setText(
            "Updating..." if busy else "Refresh 2D + 3D"
        )