import PyQt5.QtWidgets  as qtw

from app.views.components import VWBaseView
from app.views.vw_loading import VwLoading
from app.view_models import VmdCurrentDataset
from app.view_models import vmd_current_dataset


OBJECT_NAME = 'MAIN_DATA_TOOLBAR'
OBJECT_REFRESH_BUTTON_NAME  = 'MAIN_DATA_TOOLBAR_REFRESH_BUTTON'
OBJECT_RECALCULATE_BUTTON_NAME = 'MAIN_DATA_TOOLBAR_RECALCULATE_BUTTON'
OBJECT_TITLE_LABEL_NAME = 'OBJECT_TITLE_LABEL'

class VwMainDataToolbar(VWBaseView):

    def __init__(self, model: VmdCurrentDataset = None, parent=None):
        super(VwMainDataToolbar, self).__init__(parent=parent)
        self.setObjectName(OBJECT_NAME)
        self._model = model or vmd_current_dataset
        self._loading_dialog = VwLoading(parent=parent)

        self._l_title       = self._produce_named_label(content='Explore dataset', name=OBJECT_TITLE_LABEL_NAME)
        self._b_refresh     = self._produce_button(tooltip='Refresh Data', button_name=OBJECT_REFRESH_BUTTON_NAME, button_label='Refresh')
        self._b_recalculate = self._produce_button(tooltip='Recalculate Data', button_name=OBJECT_RECALCULATE_BUTTON_NAME, button_label='Recalculate')

        toolbar_layout = qtw.QHBoxLayout()
        toolbar_layout.addWidget(self._b_refresh)
        toolbar_layout.addWidget(self._b_recalculate)
        toolbar_layout.addStretch()

        main_layout = qtw.QVBoxLayout()
        main_layout.addWidget(self._l_title)
        main_layout.addLayout(toolbar_layout)
        
        self.setLayout(main_layout)

        self._setup()
        self.show()

    def _set_value_subscriptions(self):
        self._model.recalculation_in_progress.connect(self._manage_load_dialog)

    def _bind_buttons_to_commands(self):
        self._b_refresh.clicked.connect(self._model.refresh_data)
        self._b_recalculate.clicked.connect(self._model.recalculate_data_start)

    def _init_actions(self):
        pass

    def _manage_load_dialog(self, status):
        self._loading_dialog.manage(status)