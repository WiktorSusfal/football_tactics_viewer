import PyQt5.QtWidgets  as qtw

from app.views.components import VWBaseView
from app.view_models import VmdCurrentDataset


OBJECT_NAME = 'MAIN_DATA_TOOLBAR'
OBJECT_REFRESH_BUTTON_NAME  = 'MAIN_DATA_TOOLBAR_REFRESH_BUTTON'
OBJECT_RECALCULATE_BUTTON_NAME = 'MAIN_DATA_TOOLBAR_RECALCULATE_BUTTON'
 

class VwMainDataToolbar(VWBaseView):

    def __init__(self, model: VmdCurrentDataset = None, parent=None):
        super(VwMainDataToolbar, self).__init__(parent=parent)
        self.setObjectName(OBJECT_NAME)
        self._model = model or VmdCurrentDataset()

        self._b_refresh     = self._produce_button(tooltip='Refresh Data', button_name=OBJECT_REFRESH_BUTTON_NAME, button_label='Refresh')
        self._b_recalculate = self._produce_button(tooltip='Recalculate Data', button_name=OBJECT_RECALCULATE_BUTTON_NAME, button_label='Recalculate')

        main_layout = qtw.QHBoxLayout()
        main_layout.addWidget(self._b_refresh)
        main_layout.addWidget(self._b_recalculate)
        main_layout.addStretch()
        
        self.setLayout(main_layout)

        self._setup()
        self.show()

    def _set_value_subscriptions(self):
        pass

    def _bind_buttons_to_commands(self):
        self._b_refresh.clicked.connect(lambda: None)
        self._b_recalculate.clicked.connect(lambda: None)

    def _init_actions(self):
        pass