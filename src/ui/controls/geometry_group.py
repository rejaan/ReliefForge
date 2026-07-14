from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QFrame,
    QLabel,
    QSlider,
    QVBoxLayout,
)


class GeometryGroup(QFrame):
    """Geometry and base-plate controls."""

    settings_changed = Signal()

    def __init__(self):
        super().__init__()

        self.setObjectName("geometryGroup")
        self.setStyleSheet(
            """
            QFrame#geometryGroup {
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

        title = QLabel("Geometry")
        title.setStyleSheet(
            """
            font-size: 16px;
            font-weight: bold;
            """
        )

        layout.addWidget(title)
        layout.addSpacing(4)

        self.model_width_slider, self.model_width_value = (
            self._create_slider(
                layout=layout,
                label_text="Model Width",
                minimum=50,
                maximum=300,
                value=180,
            )
        )

        self.slice_slider, self.slice_value = self._create_slider(
            layout=layout,
            label_text="Slice Count",
            minimum=10,
            maximum=180,
            value=80,
        )

        self.depth_slider, self.depth_value = self._create_slider(
            layout=layout,
            label_text="Relief Depth",
            minimum=2,
            maximum=30,
            value=12,
        )

        self.contrast_slider, self.contrast_value = (
            self._create_slider(
                layout=layout,
                label_text="Depth Contrast",
                minimum=5,
                maximum=30,
                value=10,
            )
        )

        self.thickness_slider, self.thickness_value = (
            self._create_slider(
                layout=layout,
                label_text="Slice Thickness",
                minimum=2,
                maximum=30,
                value=8,
            )
        )

        self.spacing_slider, self.spacing_value = (
            self._create_slider(
                layout=layout,
                label_text="Slice Spacing",
                minimum=0,
                maximum=50,
                value=10,
            )
        )

        layout.addSpacing(10)

        base_title = QLabel("Base Plate")
        base_title.setStyleSheet(
            """
            font-size: 14px;
            font-weight: bold;
            """
        )

        self.base_enabled_checkbox = QCheckBox(
            "Enable Base Plate"
        )
        self.base_enabled_checkbox.setChecked(True)

        self.base_thickness_slider, self.base_thickness_value = (
            self._create_slider(
                layout=layout,
                label_text="Base Thickness",
                minimum=5,
                maximum=50,
                value=20,
            )
        )

        self.base_margin_slider, self.base_margin_value = (
            self._create_slider(
                layout=layout,
                label_text="Base Margin",
                minimum=0,
                maximum=50,
                value=10,
            )
        )

        layout.insertWidget(
            layout.indexOf(self.base_thickness_slider) - 1,
            base_title,
        )
        layout.insertWidget(
            layout.indexOf(self.base_thickness_slider) - 1,
            self.base_enabled_checkbox,
        )

        self._update_value_labels()
        self._update_base_controls()

    def _create_slider(
        self,
        layout: QVBoxLayout,
        label_text: str,
        minimum: int,
        maximum: int,
        value: int,
    ) -> tuple[QSlider, QLabel]:
        label = QLabel(label_text)

        slider = QSlider(Qt.Horizontal)
        slider.setRange(minimum, maximum)
        slider.setValue(value)

        value_label = QLabel()
        value_label.setAlignment(Qt.AlignRight)

        layout.addWidget(label)
        layout.addWidget(slider)
        layout.addWidget(value_label)

        return slider, value_label

    def _connect_signals(self) -> None:
        sliders = (
            self.model_width_slider,
            self.slice_slider,
            self.depth_slider,
            self.contrast_slider,
            self.thickness_slider,
            self.spacing_slider,
            self.base_thickness_slider,
            self.base_margin_slider,
        )

        for slider in sliders:
            slider.valueChanged.connect(
                self._on_settings_changed
            )

        self.base_enabled_checkbox.toggled.connect(
            self._on_base_enabled_changed
        )

    def _on_settings_changed(self, _value: int) -> None:
        self._update_value_labels()
        self.settings_changed.emit()

    def _on_base_enabled_changed(
        self,
        _checked: bool,
    ) -> None:
        self._update_base_controls()
        self.settings_changed.emit()

    def _update_value_labels(self) -> None:
        self.model_width_value.setText(
            f"{self.model_width_slider.value()} mm"
        )

        self.slice_value.setText(
            str(self.slice_slider.value())
        )

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

        self.base_thickness_value.setText(
            f"{self.base_thickness_slider.value() / 10.0:.1f} mm"
        )

        self.base_margin_value.setText(
            f"{self.base_margin_slider.value() / 10.0:.1f} mm"
        )

    def _update_base_controls(self) -> None:
        enabled = self.base_enabled_checkbox.isChecked()

        self.base_thickness_slider.setEnabled(enabled)
        self.base_margin_slider.setEnabled(enabled)

    def model_width(self) -> float:
        return float(
            self.model_width_slider.value()
        )

    def slice_count(self) -> int:
        return self.slice_slider.value()

    def relief_depth(self) -> float:
        return float(
            self.depth_slider.value()
        )

    def depth_contrast(self) -> float:
        return (
            self.contrast_slider.value()
            / 10.0
        )

    def slice_thickness(self) -> float:
        return (
            self.thickness_slider.value()
            / 10.0
        )

    def slice_spacing(self) -> float:
        return (
            self.spacing_slider.value()
            / 10.0
        )

    def base_plate_enabled(self) -> bool:
        return self.base_enabled_checkbox.isChecked()

    def base_plate_thickness(self) -> float:
        return (
            self.base_thickness_slider.value()
            / 10.0
        )

    def base_plate_margin(self) -> float:
        return (
            self.base_margin_slider.value()
            / 10.0
        )

    def set_busy(self, busy: bool) -> None:
        enabled = not busy

        self.model_width_slider.setEnabled(enabled)
        self.slice_slider.setEnabled(enabled)
        self.depth_slider.setEnabled(enabled)
        self.contrast_slider.setEnabled(enabled)
        self.thickness_slider.setEnabled(enabled)
        self.spacing_slider.setEnabled(enabled)
        self.base_enabled_checkbox.setEnabled(enabled)

        base_controls_enabled = (
            enabled
            and self.base_enabled_checkbox.isChecked()
        )

        self.base_thickness_slider.setEnabled(
            base_controls_enabled
        )
        self.base_margin_slider.setEnabled(
            base_controls_enabled
        )