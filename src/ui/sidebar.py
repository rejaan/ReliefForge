from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
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
    apply_smart_requested = Signal()
    settings_changed = Signal()

    def __init__(self):
        super().__init__()

        self.setFixedWidth(350)
        self._smart_settings_available = False

        self._build_interface()
        self._connect_signals()

    def _build_interface(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(8)

        title = QLabel("ReliefForge")
        title.setStyleSheet(
            """
            font-size: 28px;
            font-weight: bold;
            """
        )

        version = QLabel("Smart Analysis")
        version.setStyleSheet("color: #888888;")

        self.open_button = QPushButton("Open Image")

        engine_label = QLabel("Engine")

        self.engine_combo = QComboBox()
        self.engine_combo.addItems(
            [
                "Classic (V3)",
                "Smooth (V4)",
                "Adaptive (V5)",
            ]
        )
        self.engine_combo.setCurrentIndex(0)

        slice_label = QLabel("Slice Count")

        self.slice_slider = QSlider(Qt.Horizontal)
        self.slice_slider.setRange(10, 180)
        self.slice_slider.setValue(80)

        self.slice_value = QLabel("80")
        self.slice_value.setAlignment(Qt.AlignRight)

        depth_label = QLabel("Relief Depth")

        self.depth_slider = QSlider(Qt.Horizontal)
        self.depth_slider.setRange(2, 30)
        self.depth_slider.setValue(12)

        self.depth_value = QLabel("12 mm")
        self.depth_value.setAlignment(Qt.AlignRight)

        contrast_label = QLabel("Depth Contrast")

        self.contrast_slider = QSlider(Qt.Horizontal)
        self.contrast_slider.setRange(5, 30)
        self.contrast_slider.setValue(10)

        self.contrast_value = QLabel("1.0")
        self.contrast_value.setAlignment(Qt.AlignRight)

        thickness_label = QLabel("Slice Thickness")

        self.thickness_slider = QSlider(Qt.Horizontal)
        self.thickness_slider.setRange(2, 30)
        self.thickness_slider.setValue(8)

        self.thickness_value = QLabel("0.8 mm")
        self.thickness_value.setAlignment(Qt.AlignRight)

        spacing_label = QLabel("Slice Spacing")

        self.spacing_slider = QSlider(Qt.Horizontal)
        self.spacing_slider.setRange(0, 50)
        self.spacing_slider.setValue(10)

        self.spacing_value = QLabel("1.0 mm")
        self.spacing_value.setAlignment(Qt.AlignRight)

        self.apply_smart_button = QPushButton(
            "🧠 Apply Suggested Settings"
        )
        self.apply_smart_button.setEnabled(False)

        self.refresh_button = QPushButton("Refresh 2D + 3D")
        self.export_button = QPushButton("Export STL")

        layout.addWidget(title)
        layout.addWidget(version)

        layout.addSpacing(12)
        layout.addWidget(self.open_button)

        layout.addSpacing(12)
        layout.addWidget(engine_label)
        layout.addWidget(self.engine_combo)

        layout.addSpacing(12)
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
        layout.addWidget(self.apply_smart_button)
        layout.addSpacing(8)
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
        self.apply_smart_button.clicked.connect(
            self.apply_smart_requested.emit
        )

        self.engine_combo.currentIndexChanged.connect(
            lambda _index: self.settings_changed.emit()
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
        index = self.engine_combo.currentIndex()

        if index == 0:
            engine_version = "v3"
        elif index == 1:
            engine_version = "v4"
        else:
            engine_version = "v5"

        return ReliefSettings(
            slice_count=self.slice_slider.value(),
            model_width_mm=180.0,
            base_thickness_mm=2.0,
            relief_depth_mm=float(self.depth_slider.value()),
            slice_thickness_mm=(
                self.thickness_slider.value() / 10.0
            ),
            slice_spacing_mm=(
                self.spacing_slider.value() / 10.0
            ),
            depth_contrast=(
                self.contrast_slider.value() / 10.0
            ),
            base_plate_enabled=True,
            base_plate_thickness_mm=2.0,
            base_plate_margin_mm=1.0,
            mirror_horizontal=True,
            background_cutoff=0.08,
            invert=True,
            blur_kernel=3,
            equalize_histogram=True,
            engine_version=engine_version,
        )

    def apply_settings(self, settings: ReliefSettings) -> None:
        widgets = (
            self.engine_combo,
            self.slice_slider,
            self.depth_slider,
            self.contrast_slider,
            self.thickness_slider,
            self.spacing_slider,
        )

        for widget in widgets:
            widget.blockSignals(True)

        try:
            engine_indices = {
                "v3": 0,
                "v4": 1,
                "v5": 2,
            }
            self.engine_combo.setCurrentIndex(
                engine_indices.get(settings.engine_version, 0)
            )
            self.slice_slider.setValue(int(settings.slice_count))
            self.depth_slider.setValue(
                int(round(settings.relief_depth_mm))
            )
            self.contrast_slider.setValue(
                int(round(settings.depth_contrast * 10.0))
            )
            self.thickness_slider.setValue(
                int(round(settings.slice_thickness_mm * 10.0))
            )
            self.spacing_slider.setValue(
                int(round(settings.slice_spacing_mm * 10.0))
            )
        finally:
            for widget in widgets:
                widget.blockSignals(False)

        self.slice_value.setText(str(self.slice_slider.value()))
        self.depth_value.setText(
            f"{self.depth_slider.value()} mm"
        )
        self.contrast_value.setText(
            f"{self.contrast_slider.value() / 10.0:.1f}"
        )
        self.thickness_value.setText(
            f"{self.thickness_slider.value() / 10.0:.1f} mm"
        )
        self.spacing_value.setText(
            f"{self.spacing_slider.value() / 10.0:.1f} mm"
        )

        self.settings_changed.emit()

    def enable_smart_apply(self, enabled: bool) -> None:
        self._smart_settings_available = enabled
        self.apply_smart_button.setEnabled(enabled)

    def slice_count(self) -> int:
        return self.slice_slider.value()

    def relief_depth(self) -> int:
        return self.depth_slider.value()

    def set_busy(self, busy: bool) -> None:
        enabled = not busy

        self.open_button.setEnabled(enabled)
        self.refresh_button.setEnabled(enabled)
        self.export_button.setEnabled(enabled)
        self.engine_combo.setEnabled(enabled)

        self.apply_smart_button.setEnabled(
            enabled and self._smart_settings_available
        )

        self.slice_slider.setEnabled(enabled)
        self.depth_slider.setEnabled(enabled)
        self.contrast_slider.setEnabled(enabled)
        self.thickness_slider.setEnabled(enabled)
        self.spacing_slider.setEnabled(enabled)

        self.refresh_button.setText(
            "Updating..." if busy else "Refresh 2D + 3D"
        )