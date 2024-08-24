from PyQt5.QtCore       import QObject, pyqtSignal

from app.view_models.vmd_dataset_list_item import VmdDatasetListItem


class VmdSelectionChangedData:
    
    def __init__(self, old: VmdDatasetListItem, new: VmdDatasetListItem):
        self.old = old 
        self.new = new


class VmdCurrentDataset(QObject):

    dataset_edited    = pyqtSignal(VmdDatasetListItem)
    selection_changed = pyqtSignal(VmdSelectionChangedData)
    
    def __init__(self):
        super(VmdCurrentDataset, self).__init__()
        self._current_dli: VmdDatasetListItem = None
        self.get_filepath_changed_slot = lambda: self.dataset_edited.emit(self._current_dli or VmdDatasetListItem())

    def get_current_item(self) -> VmdDatasetListItem:
        return self._current_dli
    
    def get_current_item_data(self) -> VmdDatasetListItem:
        return self._current_dli or VmdDatasetListItem()
    
    def change_current_item(self, item: VmdDatasetListItem):
        old = self._current_dli
        self._current_dli = item
        self.selection_changed.emit(VmdSelectionChangedData(old=old, new=item))

    def _subscribe_to_list_item(self, item: VmdDatasetListItem):
        item.events_filepath_changed.connect( self.get_filepath_changed_slot)
        item.frames_filepath_changed.connect( self.get_filepath_changed_slot)
        item.lineups_filepath_changed.connect(self.get_filepath_changed_slot)

    def _unsubscribe_to_list_item(self, item: VmdDatasetListItem):
        item.events_filepath_changed.disconnect( self.get_filepath_changed_slot)
        item.frames_filepath_changed.disconnect( self.get_filepath_changed_slot)
        item.lineups_filepath_changed.disconnect(self.get_filepath_changed_slot)