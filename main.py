import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from main_window import MainWindow,resource_path

if __name__ == "__main__":
    app = QApplication(sys.argv)

    app.setWindowIcon(QIcon(resource_path("icon.png")))
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
