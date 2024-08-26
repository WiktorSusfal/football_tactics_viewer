from app import VwMainWindow
from app.helpers import get_styles_code
from PyQt5.QtWidgets import QApplication

if __name__ == '__main__':
    app = QApplication([])
    app.setStyleSheet(get_styles_code())
    app_main_gui = VwMainWindow()
    app.exec_()