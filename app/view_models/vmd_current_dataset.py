from PyQt5.QtCore       import QObject, pyqtSignal, QThread

from app.view_models.vmd_dataset_list_item import VmdDatasetListItem
from app.view_models.vmd_football_pitch    import VmdFootballPitch
from app.view_models                       import vmd_football_pitch


class VmdSelectionChangedData:
    
    def __init__(self, old: VmdDatasetListItem, new: VmdDatasetListItem):
        self.old = old 
        self.new = new


class VmdDataWorker(QThread):
    finished = pyqtSignal()

    def __init__(self, item: VmdDatasetListItem, *args, **kwargs):
        super(VmdDataWorker, self).__init__(*args, **kwargs)
        self._item = item

    def run(self):
        self._item.recalculate_data()
        self.finished.emit()


class VmdCurrentDataset(QObject):

    dataset_edited    = pyqtSignal(VmdDatasetListItem)
    selection_changed = pyqtSignal(VmdSelectionChangedData)

    recalculation_in_progress = pyqtSignal(bool)
    
    def __init__(self, football_pitch_vmodel: VmdFootballPitch = None):
        super(VmdCurrentDataset, self).__init__()
        self._fp_vm = football_pitch_vmodel or vmd_football_pitch

        self._current_dli: VmdDatasetListItem = None
        self.get_dataset_edited_slot = lambda: self.dataset_edited.emit(self._current_dli or VmdDatasetListItem())

    def get_current_item(self) -> VmdDatasetListItem:
        return self._current_dli
    
    def get_current_item_data(self) -> VmdDatasetListItem:
        return self._current_dli or VmdDatasetListItem()
    
    def change_current_item(self, item: VmdDatasetListItem):
        old = self._current_dli
        self._current_dli = item
        
        self._unsubscribe_to_list_item(old)
        self._subscribe_to_list_item(item)

        self.selection_changed.emit(VmdSelectionChangedData(old=old, new=item))
        self.get_data()

    def _subscribe_to_list_item(self, item: VmdDatasetListItem):
        if item:
            item.dataset_edited.connect(self.get_dataset_edited_slot)
            item.dataset_edited.connect(self.get_data)

    def _unsubscribe_to_list_item(self, item: VmdDatasetListItem):
        if item:
            item.dataset_edited.disconnect(self.get_dataset_edited_slot)
            item.dataset_edited.disconnect(self.get_data)
    
    def set_current_frame(self, val: int | str):
        if self._current_dli:
            self._current_dli.set_current_frame(int(val))

    def next_frame(self):
        if self._current_dli:
            self._current_dli.next_frame()

    def previous_frame(self):
        if self._current_dli:
            self._current_dli.previous_frame()

    def get_data(self, item: VmdDatasetListItem = None):
        if self._current_dli:
            lineups_frame, players_frame, events_frame = self._current_dli.get_data()
            self._fp_vm.get_data(players_frame, events_frame, lineups_frame)
    
    def refresh_data(self):
        if self._current_dli:
            self._current_dli.refresh_data()
    
    def recalculate_data(self):
        if self._current_dli:
            self.recalculation_in_progress.emit(True)
            self.worker  = VmdDataWorker(item=self._current_dli)
           
            self.worker.finished.connect(lambda: self.recalculation_in_progress.emit(False))
            self.worker.finished.connect(self.worker.deleteLater)

            self.worker.start()