from PyQt6.QtWidgets import QApplication
from qt_material import apply_stylesheet
import sys

from app.ui.main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    apply_stylesheet(app, theme='dark_pink.xml')
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
