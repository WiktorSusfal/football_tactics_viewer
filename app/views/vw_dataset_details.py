import PyQt5.QtWidgets  as qtw

from app.views.components import VWBaseView
from app.view_models import VmdDatasetListItem, VmdDatasetList, DEFAULT_FILE_PATH


OBJECT_NAME = 'DATASET_DETAILS_VIEW'
OBJECT_FORM_LABEL_NAME  = 'DATASET_DETAILS_VIEW_FORM_LABEL'
OBJECT_FORM_LABEL_VALUE = 'DATASET_DETAILS_VIEW_FORM_VALUE'
 

class VwDatasetDetails(VWBaseView):

    def __init__(self, model: VmdDatasetList = None, parent=None):
        super(VwDatasetDetails, self).__init__(parent=parent)
        self.setObjectName(OBJECT_NAME)
        self._model = model or VmdDatasetList()
        self._tmp_data_model: VmdDatasetListItem = self._model.get_current_item() or None

        self._l_lineups = self._produce_named_label(self._tmp_data_model._lineups_filepath if self._tmp_data_model else DEFAULT_FILE_PATH, OBJECT_FORM_LABEL_VALUE)  
        self._l_events  = self._produce_named_label(self._tmp_data_model._events_filepath  if self._tmp_data_model else DEFAULT_FILE_PATH, OBJECT_FORM_LABEL_VALUE)  
        self._l_frames  = self._produce_named_label(self._tmp_data_model._frames_filepath  if self._tmp_data_model else DEFAULT_FILE_PATH, OBJECT_FORM_LABEL_VALUE)  
        
        self._data_form = qtw.QFormLayout()
        self._data_form.addRow(
            self._produce_named_label("Lineups path: ", OBJECT_FORM_LABEL_NAME)  
            ,self._l_lineups)
        self._data_form.addRow(
            self._produce_named_label("Events path: ", OBJECT_FORM_LABEL_NAME)
            ,self._l_events)
        self._data_form.addRow(
            self._produce_named_label("Frames path: ", OBJECT_FORM_LABEL_NAME)
            ,self._l_frames)
        
        main_layout = qtw.QVBoxLayout()
        main_layout.addLayout(self._data_form)
        self.setLayout(main_layout)

        self._setup()
        self.show()

    def _set_value_subscriptions(self):
        self._model.current_selection_changed.connect(self._selection_changed)
        self._model.list_item_changed.connect(self._data_changed)

    def _bind_buttons_to_commands(self):
        pass

    def _init_actions(self):
        pass

    def _data_changed(self, *args):
        item = self._model.get_current_item()
        self._selection_changed(item)

    def _selection_changed(self, item: VmdDatasetListItem):
        if self._tmp_data_model:
            self._tmp_data_model.events_filepath_changed.disconnect( self._l_events.setText)
            self._tmp_data_model.lineups_filepath_changed.disconnect(self._l_lineups.setText)
            self._tmp_data_model.frames_filepath_changed.disconnect( self._l_frames.setText)

        self._tmp_data_model = item
        if self._tmp_data_model:
            self._tmp_data_model.events_filepath_changed.connect( self._l_events.setText)
            self._tmp_data_model.lineups_filepath_changed.connect(self._l_lineups.setText)
            self._tmp_data_model.frames_filepath_changed.connect( self._l_frames.setText)

        self._l_lineups.setText(item._lineups_filepath if item else DEFAULT_FILE_PATH)
        self._l_events.setText( item._events_filepath  if item else DEFAULT_FILE_PATH) 
        self._l_frames.setText( item._frames_filepath  if item else DEFAULT_FILE_PATH) 