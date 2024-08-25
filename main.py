from PyQt5.QtWidgets import QApplication

from app import VwMainWindow


if __name__ == '__main__':
    app = QApplication([])
    app_main_gui = VwMainWindow()
    app.exec_()