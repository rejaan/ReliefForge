APP_STYLE = """
QWidget {
    background-color: #1e1f22;
    color: #f2f2f2;
    font-size: 13px;
}

QMainWindow {
    background-color: #1e1f22;
}

QLabel {
    background: transparent;
}

QPushButton {
    background-color: #2b2d31;
    border: 1px solid #3a3d43;
    border-radius: 7px;
    padding: 9px 12px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #34373d;
    border-color: #4ea8ff;
}

QPushButton:pressed {
    background-color: #25272b;
}

QPushButton:disabled {
    color: #777777;
    background-color: #24262a;
    border-color: #303238;
}

QSlider::groove:horizontal {
    height: 6px;
    background: #34373d;
    border-radius: 3px;
}

QSlider::sub-page:horizontal {
    background: #4ea8ff;
    border-radius: 3px;
}

QSlider::handle:horizontal {
    width: 18px;
    margin: -6px 0;
    border-radius: 9px;
    background: #f2f2f2;
    border: 2px solid #4ea8ff;
}

QSplitter::handle {
    background-color: #2a2c31;
    width: 2px;
}

QStatusBar {
    background-color: #18191c;
    color: #aeb3bb;
    border-top: 1px solid #2e3035;
}
"""