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
        layout.setSpacing(8)

        title = QLabel("ReliefForge")
        title.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
        """)

        version = QLabel("v0.3.7 – Depth Profiles")
        version.setStyleSheet("color: #888888;")

        self.open_button = QPushButton("Open Image")

        # Slice Count
        slice_label = QLabel("Slice Count")

        self.slice_slider = QSlider(Qt.Horizontal)
        self.slice_slider.setRange(10, 180)
        self.slice_slider.setValue(80)

        self.slice_value = QLabel("80")
        self.slice_value.setAlignment(Qt.AlignRight)

        # Relief Depth
        depth_label = QLabel("Relief Depth")

        self.depth_slider = QSlider(Qt.Horizontal)
        self.depth_slider.setRange(2, 30)
        self.depth_slider.setValue(12)

        self.depth_value = QLabel("12 mm")
        self.depth_value.setAlignment(Qt.AlignRight)

        # Depth Contrast
        contrast_label = QLabel("Depth Contrast")

        self.contrast_slider = QSlider(Qt.Horizontal)
        self.contrast_slider.setRange(5, 30)
        self.contrast_slider.setValue(10)

        self.contrast_value = QLabel("1.0")
        self.contrast_value.setAlignment(Qt.AlignRight)

        # Slice Thickness
        thickness_label = QLabel("Slice Thickness")

        self.thickness_slider = QSlider(Qt.Horizontal)
        self.thickness_slider.setRange(2, 30)
        self.thickness_slider.setValue(8)

        self.thickness_value = QLabel("0.8 mm")
        self.thickness_value.setAlignment(Qt.AlignRight)

        # Slice Spacing
        spacing_label = QLabel("Slice Spacing")

        self.spacing_slider = QSlider(Qt.Horizontal)
        self.spacing_slider.setRange(0, 50)
        self.spacing_slider.setValue(10)

        self.spacing_value = QLabel("1.0 mm")
        self.spacing_value.setAlignment(Qt.AlignRight)

        self.refresh_button = QPushButton("Refresh 2D + 3D")
        self.export_button = QPushButton("Export STL")

        layout.addWidget(title)
        layout.addWidget(version)

        layout.addSpacing(12)
        layout.addWidget(self.open_button)

        layout.addSpacing(16)
        layout.addWidget(slice_label)
        layout.addWidget(self.slice_slider)
        layout.addWidget(self.slice_value)

        layout.addSpacing(6)
        layout.addWidget(depth_label)
        layout.addWidget(self.depth_slider)
        layout.addWidget(self.depth_value)

        layout.addSpacing(6)
        layout.addWidget(contrast_label)
        layout.addWidget(self.contrast_slider)
        layout.addWidget(self.contrast_value)

        layout.addSpacing(6)
        layout.addWidget(thickness_label)
        layout.addWidget(self.thickness_slider)
        layout.addWidget(self.thickness_value)

        layout.addSpacing(6)
        layout.addWidget(spacing_label)
        layout.addWidget(self.spacing_slider)
        layout.addWidget(self.spacing_value)

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

        self.contrast_slider.valueChanged.connect(
            self._on_depth_contrast_changed
        )

        self.thickness_slider.valueChanged.connect(
            self._on_slice_thickness_changed
        )

        self.spacing_slider.valueChanged.connect(
            self._on_slice_spacing_changed
        )

    def _on_slice_count_changed(self, value: int) -> None:
        self.slice_value.setText(str(value))
        self.settings_changed.emit()

    def _on_relief_depth_changed(self, value: int) -> None:
        self.depth_value.setText(f"{value} mm")
        self.settings_changed.emit()

    def _on_depth_contrast_changed(self, value: int) -> None:
        contrast = value / 10.0
        self.contrast_value.setText(f"{contrast:.1f}")
        self.settings_changed.emit()

    def _on_slice_thickness_changed(self, value: int) -> None:
        thickness = value / 10.0
        self.thickness_value.setText(f"{thickness:.1f} mm")
        self.settings_changed.emit()

    def _on_slice_spacing_changed(self, value: int) -> None:
        spacing = value / 10.0
        self.spacing_value.setText(f"{spacing:.1f} mm")
        self.settings_changed.emit()

    def settings(self) -> ReliefSettings:
        return ReliefSettings(
            slice_count=self.slice_slider.value(),
            model_width_mm=180.0,
            base_thickness_mm=2.0,
            relief_depth_mm=float(self.depth_slider.value()),
            slice_thickness_mm=self.thickness_slider.value() / 10.0,
            slice_spacing_mm=self.spacing_slider.value() / 10.0,
            depth_contrast=self.contrast_slider.value() / 10.0,
            invert=True,
            blur_kernel=3,
            equalize_histogram=True,
        )

    def slice_count(self) -> int:
        return self.slice_slider.value()

    def relief_depth(self) -> int:
        return self.depth_slider.value()

    def set_busy(self, busy: bool) -> None:
        enabled = not busy

        self.open_button.setEnabled(enabled)
        self.refresh_button.setEnabled(enabled)
        self.export_button.setEnabled(enabled)

        self.slice_slider.setEnabled(enabled)
        self.depth_slider.setEnabled(enabled)
        self.contrast_slider.setEnabled(enabled)
        self.thickness_slider.setEnabled(enabled)
        self.spacing_slider.setEnabled(enabled)

        self.refresh_button.setText(
            "Updating..." if busy else "Refresh 2D + 3D"
        )