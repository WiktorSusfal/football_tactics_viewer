import PyQt5.QtWidgets  as qtw
import PyQt5.QtCore     as qtc

from app.views.components import VWBaseView
from app.view_models import VmdDatasetListItem, VmdDatasetDataType


OBJECT_NAME = 'DATASET_LIST_ITEM'
OBJECT_LABEL_NAME = 'DATASET_LIST_ITEM_LABEL_NAME'
OBJECT_LOAD_BUTTON_NAME = 'DATASET_LIST_ITEM_LOAD_BUTTON'
 

class VwDatasetListItem(VWBaseView):

    def __init__(self, dataset_name: str = None, model: VmdDatasetListItem = None, parent=None):
        super(VwDatasetListItem, self).__init__(parent=parent)
        self.setObjectName(OBJECT_NAME)

        self._model: VmdDatasetListItem = model or VmdDatasetListItem(dataset_name=dataset_name)

        self._l_name = self._produce_named_label(self._model._dataset_name, OBJECT_LABEL_NAME)
        self._b_load_lineups = self._produce_button(tooltip='Choose lineups data file', button_name=OBJECT_LOAD_BUTTON_NAME, icon_rel_path=r'human64.png', icon_size=24)
        self._b_load_events  = self._produce_button(tooltip='Choose events data file', button_name=OBJECT_LOAD_BUTTON_NAME , icon_rel_path=r'event64.png', icon_size=24)
        self._b_load_frames  = self._produce_button(tooltip='Choose frames data file', button_name=OBJECT_LOAD_BUTTON_NAME , icon_rel_path=r'frame64.png', icon_size=24)

        self._main_layout = qtw.QHBoxLayout()
        self._main_layout.addWidget(self._l_name)
        self._main_layout.addWidget(self._b_load_lineups)
        self._main_layout.addWidget(self._b_load_events)
        self._main_layout.addWidget(self._b_load_frames)
        self._main_layout.setSpacing(2)

        self.setLayout(self._main_layout)

        self._setup()
        self.show()

    def _bind_buttons_to_commands(self):
        self._b_load_lineups.clicked.connect(lambda: self._model.assign_data_filepath(VmdDatasetDataType.LINEUPS.value))
        self._b_load_events.clicked.connect( lambda: self._model.assign_data_filepath(VmdDatasetDataType.EVENTS.value))
        self._b_load_frames.clicked.connect( lambda: self._model.assign_data_filepath(VmdDatasetDataType.FRAMES.value))
    
    def _init_actions(self):
        pass

    def _set_value_subscriptions(self):
        self._model.dataset_name_changed.connect(self._l_name.setText)

    def contextMenuEvent(self, event):
        contextMenu = qtw.QMenu(self)
        
        action1 = qtw.QAction("Delete", self)
        action1.triggered.connect(lambda: self._model.delete_item())
        contextMenu.addAction(action1)
        
        contextMenu.exec_(event.globalPos())