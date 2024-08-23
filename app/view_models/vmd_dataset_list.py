from PyQt5.QtCore       import QObject, pyqtSignal

from app.view_models.vmd_dataset_list_item import VmdDatasetListItem


class VmdDatasetList(QObject):

    list_item_added   = pyqtSignal(VmdDatasetListItem)
    list_item_deleted = pyqtSignal(VmdDatasetListItem)
    list_item_changed  = pyqtSignal(VmdDatasetListItem)
    current_selection_changed = pyqtSignal(VmdDatasetListItem)


    def __init__(self):
        super(VmdDatasetList, self).__init__()

        self._current_dli: VmdDatasetListItem       = None
        self._dli_list   : list[VmdDatasetListItem] = list()

        self.get_filepath_changed_slot =  lambda: self.list_item_changed.emit(self._current_dli)

    def get_current_item(self) -> VmdDatasetListItem:
        return self._current_dli

    def add_item(self, name: str):
        dli = VmdDatasetListItem(name)
        self._dli_list.append(dli)

        self._subscribe_to_list_item(dli)
        self.list_item_added.emit(dli)

    def delete_item(self, item_id: int):
        idx = len(self._dli_list) - 1 
        while idx >= 0:
            if self._dli_list[idx].get_id() == item_id:
                dli = self._dli_list.pop(idx)
                self._unsubscribe_to_list_item(dli)

                self.list_item_deleted.emit(dli)

                break
            idx -= 1

    def change_current_item(self, item: VmdDatasetListItem):
        self._current_dli = item
        self.current_selection_changed.emit(self._current_dli)

    def _subscribe_to_list_item(self, item: VmdDatasetListItem):
        item.events_filepath_changed.connect( self.get_filepath_changed_slot)
        item.frames_filepath_changed.connect( self.get_filepath_changed_slot)
        item.lineups_filepath_changed.connect(self.get_filepath_changed_slot)
        item.delete_item_order.connect(self.delete_item)

    def _unsubscribe_to_list_item(self, item: VmdDatasetListItem):
        item.events_filepath_changed.disconnect( self.get_filepath_changed_slot)
        item.frames_filepath_changed.disconnect( self.get_filepath_changed_slot)
        item.lineups_filepath_changed.disconnect(self.get_filepath_changed_slot)
        item.delete_item_order.disconnect( self.delete_item)