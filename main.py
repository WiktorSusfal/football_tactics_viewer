import ___FTV_UI_Manager as ftvui
from PyQt5 import QtWidgets as pqt

if __name__ == '__main__':
    app = pqt.QApplication([])
    app_main_gui = ftvui.MainWindow()
    app.exec_()


