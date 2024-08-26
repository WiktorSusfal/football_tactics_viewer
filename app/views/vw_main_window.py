from PyQt5              import QtGui
import PyQt5.QtWidgets  as qtw
import PyQt5.QtCore     as qtc

from app.views.vw_main_view import VwMainView
from app.views.vw_title_bar import VwTitleBar

OBJECT_NAME = 'MAIN_WINDOW'

class VwMainWindow(qtw.QMainWindow):

    def __init__(self):
        super(VwMainWindow, self).__init__()
        self.setObjectName(OBJECT_NAME)

        flags=qtc.Qt.WindowFlags(qtc.Qt.FramelessWindowHint)
        self.setWindowFlags(flags)

        self.setMenuWidget(VwTitleBar(parent=self))
        self.setCentralWidget(VwMainView(parent=self))

        # below is needed to make the window moveable
        self._old_cursor_pos = None
        
        self.show()

    def mousePressEvent(self, event):
        if event.button() == qtc.Qt.MouseButton.LeftButton:
            self._old_cursor_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        if self._old_cursor_pos is not None:
            delta = event.globalPos() - self._old_cursor_pos
            self.move(self.pos() + delta)
            self._old_cursor_pos = event.globalPos()

    def mouseReleaseEvent(self, event):
        self._old_cursor_pos = None