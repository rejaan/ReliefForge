from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QSlider,
    QVBoxLayout,
)


class GeometryGroup(QFrame):
    """Geometry controls."""

    settings_changed = Signal()

    def __init__(self):
        super().__init__()

        self.setObjectName("geometryGroup")

        self.setStyleSheet("""
        QFrame#geometryGroup{
            background:#25262a;
            border:1px solid #34373d;
            border-radius:8px;
        }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14,14,14,14)
        layout.setSpacing(7)

        title = QLabel("Geometry")
        title.setStyleSheet("""
        font-size:16px;
        font-weight:bold;
        """)

        layout.addWidget(title)

        self._add_slice(layout)
        self._add_depth(layout)
        self._add_contrast(layout)
        self._add_thickness(layout)
        self._add_spacing(layout)

    def _make_slider(
        self,
        layout,
        text,
        minimum,
        maximum,
        value,
        callback,
    ):

        label = QLabel(text)

        slider = QSlider(Qt.Horizontal)
        slider.setRange(minimum, maximum)
        slider.setValue(value)

        value_label = QLabel()
        value_label.setAlignment(Qt.AlignRight)

        slider.valueChanged.connect(callback)

        layout.addWidget(label)
        layout.addWidget(slider)
        layout.addWidget(value_label)

        return slider, value_label

    def _add_slice(self, layout):

        self.slice_slider, self.slice_value = self._make_slider(
            layout,
            "Slice Count",
            10,
            180,
            80,
            self._slice_changed,
        )

        self._slice_changed(80)

    def _add_depth(self, layout):

        self.depth_slider, self.depth_value = self._make_slider(
            layout,
            "Relief Depth",
            2,
            30,
            12,
            self._depth_changed,
        )

        self._depth_changed(12)

    def _add_contrast(self, layout):

        self.contrast_slider, self.contrast_value = self._make_slider(
            layout,
            "Depth Contrast",
            5,
            30,
            10,
            self._contrast_changed,
        )

        self._contrast_changed(10)

    def _add_thickness(self, layout):

        self.thickness_slider, self.thickness_value = self._make_slider(
            layout,
            "Slice Thickness",
            2,
            30,
            8,
            self._thickness_changed,
        )

        self._thickness_changed(8)

    def _add_spacing(self, layout):

        self.spacing_slider, self.spacing_value = self._make_slider(
            layout,
            "Slice Spacing",
            0,
            50,
            10,
            self._spacing_changed,
        )

        self._spacing_changed(10)

    def _slice_changed(self, value):
        self.slice_value.setText(str(value))
        self.settings_changed.emit()

    def _depth_changed(self, value):
        self.depth_value.setText(f"{value} mm")
        self.settings_changed.emit()

    def _contrast_changed(self, value):
        self.contrast_value.setText(f"{value/10:.1f}")
        self.settings_changed.emit()

    def _thickness_changed(self, value):
        self.thickness_value.setText(f"{value/10:.1f} mm")
        self.settings_changed.emit()

    def _spacing_changed(self, value):
        self.spacing_value.setText(f"{value/10:.1f} mm")
        self.settings_changed.emit()

    def slice_count(self):
        return self.slice_slider.value()

    def relief_depth(self):
        return self.depth_slider.value()

    def depth_contrast(self):
        return self.contrast_slider.value()/10

    def slice_thickness(self):
        return self.thickness_slider.value()/10

    def slice_spacing(self):
        return self.spacing_slider.value()/10

    def set_busy(self, busy):

        enabled = not busy

        self.slice_slider.setEnabled(enabled)
        self.depth_slider.setEnabled(enabled)
        self.contrast_slider.setEnabled(enabled)
        self.thickness_slider.setEnabled(enabled)
        self.spacing_slider.setEnabled(enabled)