from PyQt5.QtWidgets    import QDialog, QVBoxLayout, QLabel
from PyQt5.QtGui        import QMovie
import PyQt5.QtCore     as qtc

DIALOG_NAME = "Please Wait"
LOAD_GIF_REL_PATH = r"resources\img\loading_big.gif"


class VwLoading(QDialog):

    def __init__(self, parent=None):
        super(VwLoading, self).__init__(parent=parent)

        self.setWindowTitle(DIALOG_NAME)
        self.setWindowModality(qtc.Qt.ApplicationModal)
        self.setFixedSize(200, 200)

        self.setWindowFlags(qtc.Qt.FramelessWindowHint | qtc.Qt.Dialog)

        layout = QVBoxLayout(self)
        self._label = QLabel(self)
        self._label.setAlignment(qtc.Qt.AlignCenter)
        layout.addWidget(self._label)

        self._load_gif = QMovie(LOAD_GIF_REL_PATH)
        self._load_gif.setScaledSize(self._load_gif.scaledSize().scaled(200, 200, qtc.Qt.KeepAspectRatio))
        self._label.setMovie(self._load_gif)
    
        self.setLayout(layout)
        
        self._bind_buttons_to_commands()
    
    def _bind_buttons_to_commands(self):
        pass

    def manage(self, status: bool):
        if status:
            self._load_gif.start()
            self.show()
        else:
            self.close()
            self._load_gif.stop()