import PyQt5.QtWidgets  as qtw

from app.views.components import VWBaseView
from app.view_models import vmd_current_dataset
from app.view_models import VmdDatasetListItem, VmdCurrentDataset, VmdSelectionChangedData


OBJECT_NAME = 'DATASET_DETAILS_VIEW'
OBJECT_FORM_LABEL_NAME  = 'DATASET_DETAILS_VIEW_FORM_LABEL'
OBJECT_FORM_LABEL_VALUE = 'DATASET_DETAILS_VIEW_FORM_VALUE'
 

class VwDatasetDetails(VWBaseView):

    def __init__(self, model: VmdCurrentDataset = None, parent=None):
        super(VwDatasetDetails, self).__init__(parent=parent)
        self.setObjectName(OBJECT_NAME)
        self._model = model or vmd_current_dataset

        _tmp_data_model = self._model.get_current_item_data()
        self._l_lineups = self._produce_named_label(_tmp_data_model._lineups_filepath, OBJECT_FORM_LABEL_VALUE)  
        self._l_events  = self._produce_named_label(_tmp_data_model._events_filepath, OBJECT_FORM_LABEL_VALUE)  
        self._l_frames  = self._produce_named_label(_tmp_data_model._frames_filepath, OBJECT_FORM_LABEL_VALUE)  
        
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
        self._model.selection_changed.connect(self._selection_changed)
        self._model.dataset_edited.connect(self._dataset_edited)

    def _bind_buttons_to_commands(self):
        pass

    def _init_actions(self):
        pass

    def _dataset_edited(self, item: VmdDatasetListItem):
        self._l_lineups.setText(item._lineups_filepath)
        self._l_events.setText( item._events_filepath) 
        self._l_frames.setText( item._frames_filepath)

    def _selection_changed(self, info: VmdSelectionChangedData):
        old, new = info.old, info.new
        self._dataset_edited(new)