from PyQt5 import QtWidgets as qtw
from importlib import *


class test(qtw.QWidget):

    def __init__(self):
        super().__init__()
        self.layout = qtw.QVBoxLayout()
        self.setLayout(self.layout)

        self.pb = qtw.QPushButton('Some basic text')
        self.pb.setFixedSize(200, 200)
        clicked = getattr(self.pb, 'clicked')
        connect = getattr(clicked, 'connect')
        connect(self.print_something)

        self.layout.addWidget(self.pb)


    @staticmethod
    def print_something():
        module = import_module('PyQt5.QtWidgets')
        print(getattr(module, 'QPushButton'))




class MainWindow(qtw.QMainWindow):
    def __init__(self):
        super().__init__()
        # Initialize FTV_GUIDataManager object for main window

        self.setWindowTitle('Football Tactics Viewer')
        self.setFixedSize(600, 600)
        self.central_widget = test()
        self.setCentralWidget(self.central_widget)

        self.show()


if __name__ == '__main__':
    print(globals())
    app = qtw.QApplication([])
    app_main_gui = MainWindow()
    app.exec_()

