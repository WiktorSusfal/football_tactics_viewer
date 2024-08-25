from PyQt5              import QtGui
import PyQt5.QtWidgets  as qtw
import PyQt5.QtCore     as qtc

from app.views.vw_main_view import VwMainView

OBJECT_NAME = 'MAIN_WINDOW'

class VwMainWindow(qtw.QMainWindow):

    def __init__(self):
        super(VwMainWindow, self).__init__()
        self.setObjectName(OBJECT_NAME)
        self.setCentralWidget(VwMainView(parent=self))
        self.show()