from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QFrame,
    QLabel,
    QSlider,
    QVBoxLayout,
)


class ImageGroup(QFrame):
    """Image-processing controls for ReliefForge."""

    settings_changed = Signal()

    def __init__(self):
        super().__init__()

        self.setObjectName("imageGroup")

        self.setStyleSheet(
            """
            QFrame#imageGroup {
                background-color: #25262a;
                border: 1px solid #34373d;
                border-radius: 8px;
            }
            """
        )

        self._build_interface()
        self._connect_signals()

    def _build_interface(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(7)

        title = QLabel("Image Processing")
        title.setStyleSheet(
            """
            font-size: 16px;
            font-weight: bold;
            """
        )

        cutoff_label = QLabel("Background Cutoff")

        self.cutoff_slider = QSlider(Qt.Horizontal)
        self.cutoff_slider.setRange(0, 30)
        self.cutoff_slider.setValue(8)

        self.cutoff_value = QLabel("0.08")
        self.cutoff_value.setAlignment(Qt.AlignRight)

        blur_label = QLabel("Blur")

        self.blur_slider = QSlider(Qt.Horizontal)
        self.blur_slider.setRange(0, 4)
        self.blur_slider.setValue(1)

        self.blur_value = QLabel("3")
        self.blur_value.setAlignment(Qt.AlignRight)

        self.equalize_checkbox = QCheckBox(
            "Histogram Equalization"
        )
        self.equalize_checkbox.setChecked(True)

        self.invert_checkbox = QCheckBox("Invert Relief")
        self.invert_checkbox.setChecked(True)

        layout.addWidget(title)
        layout.addSpacing(4)

        layout.addWidget(cutoff_label)
        layout.addWidget(self.cutoff_slider)
        layout.addWidget(self.cutoff_value)

        layout.addSpacing(5)
        layout.addWidget(blur_label)
        layout.addWidget(self.blur_slider)
        layout.addWidget(self.blur_value)

        layout.addSpacing(5)
        layout.addWidget(self.equalize_checkbox)
        layout.addWidget(self.invert_checkbox)

    def _connect_signals(self) -> None:
        self.cutoff_slider.valueChanged.connect(
            self._on_cutoff_changed
        )

        self.blur_slider.valueChanged.connect(
            self._on_blur_changed
        )

        self.equalize_checkbox.toggled.connect(
            lambda _checked: self.settings_changed.emit()
        )

        self.invert_checkbox.toggled.connect(
            lambda _checked: self.settings_changed.emit()
        )

    def _on_cutoff_changed(self, value: int) -> None:
        self.cutoff_value.setText(
            f"{value / 100.0:.2f}"
        )
        self.settings_changed.emit()

    def _on_blur_changed(self, value: int) -> None:
        self.blur_value.setText(
            str(self._blur_kernel(value))
        )
        self.settings_changed.emit()

    @staticmethod
    def _blur_kernel(value: int) -> int:
        kernels = (1, 3, 5, 7, 9)
        return kernels[value]

    def background_cutoff(self) -> float:
        return self.cutoff_slider.value() / 100.0

    def blur_kernel(self) -> int:
        return self._blur_kernel(
            self.blur_slider.value()
        )

    def equalize_histogram(self) -> bool:
        return self.equalize_checkbox.isChecked()

    def invert(self) -> bool:
        return self.invert_checkbox.isChecked()

    def set_busy(self, busy: bool) -> None:
        enabled = not busy

        self.cutoff_slider.setEnabled(enabled)
        self.blur_slider.setEnabled(enabled)
        self.equalize_checkbox.setEnabled(enabled)
        self.invert_checkbox.setEnabled(enabled)