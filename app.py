import sys

from PySide6.QtWidgets import QApplication

from src.ui.main_window import MainWindow
from src.ui.theme import APP_STYLE


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("ReliefForge")
    app.setStyleSheet(APP_STYLE)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()