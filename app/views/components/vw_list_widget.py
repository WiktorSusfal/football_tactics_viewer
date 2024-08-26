import PyQt5.QtWidgets as qtw
import PyQt5.QtCore as qtc


HINT_LABEL_CONTENT  = 'No connections added'
HINT_LABEL_NAME     = 'LIST_WIDGET_HINT_LABEL'

class VwListWidget(qtw.QListWidget):
    def __init__(self):
        super(VwListWidget, self).__init__()

        self.caption_label = qtw.QLabel(HINT_LABEL_CONTENT, self)
        self.caption_label.setAlignment(qtc.Qt.AlignTop | qtc.Qt.AlignHCenter)
        self.caption_label.setObjectName(HINT_LABEL_NAME)
        self.caption_label.hide()

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.count() == 0:
            self.caption_label.setGeometry(self.rect())
            self.caption_label.show()
        else:
            self.caption_label.hide()