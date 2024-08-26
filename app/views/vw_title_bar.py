import PyQt5.QtWidgets as qtw
import PyQt5.QtCore as qtc

from app.views.components import VWBaseView


OBJECT_NAME = 'TITLE_BAR'
OBJECT_ICON_LABEL_NAME = 'TITLE_BAR_ICON_LABEL'
OBJECT_TITLE_LABEL_NAME = 'TITLE_BAR_TITLE_LABEL'
OBJECT_BAR_BUTTON_NAME = 'TITLE BAR BUTTON'

TITLE = 'Football tactics viewer'
MAIN_ICON_REL_PATH      = r'tactics_icon.png'
CLOSE_ICON_REL_PATH     = r'close.png'
MINIMIZE_ICON_REL_PATH  = r'minimize.png'


class VwTitleBar(VWBaseView):
    def __init__(self, parent=None):
        super(VwTitleBar, self).__init__(parent=parent)
        self.setObjectName(OBJECT_NAME)

        self._app_icon = self._produce_icon_label(MAIN_ICON_REL_PATH, 24, 24, label_name=OBJECT_ICON_LABEL_NAME)
        self._title_label = self._produce_named_label(TITLE, name=OBJECT_TITLE_LABEL_NAME)
     
        self._minimize_button = self._produce_button(icon_rel_path=MINIMIZE_ICON_REL_PATH, icon_size=24, button_name=OBJECT_BAR_BUTTON_NAME)
        self._close_button = self._produce_button(icon_rel_path=CLOSE_ICON_REL_PATH, icon_size=24, button_name=OBJECT_BAR_BUTTON_NAME)

        self._main_layout = qtw.QHBoxLayout()
        self._main_layout.addWidget(self._app_icon, alignment=qtc.Qt.AlignLeft | qtc.Qt.AlignVCenter, stretch=0)
        self._main_layout.addWidget(self._title_label, alignment=qtc.Qt.AlignLeft | qtc.Qt.AlignVCenter, stretch=0)
        self._main_layout.addStretch()
        self._main_layout.addWidget(self._minimize_button, alignment=qtc.Qt.AlignRight | qtc.Qt.AlignVCenter, stretch=0)
        self._main_layout.addWidget(self._close_button, alignment=qtc.Qt.AlignRight | qtc.Qt.AlignVCenter, stretch=0)
        
        self.setLayout(self._main_layout)
        self._setup()

    def _minimize_window(self):
        if self.parentWidget().isMaximized():
            self.parentWidget().showNormal()
        self.parentWidget().showMinimized()

    def _close_window(self):
        self.parentWidget().close()

    def _set_value_subscriptions(self):
        pass

    def _bind_buttons_to_commands(self):
        self._minimize_button.clicked.connect(self._minimize_window)
        self._close_button.clicked.connect(self._close_window)

    def _init_actions(self):
        pass