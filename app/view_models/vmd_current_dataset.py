from PyQt5.QtCore       import QObject, pyqtSignal

from app.view_models.vmd_dataset_list_item import VmdDatasetListItem


class VmdSelectionChangedData:
    
    def __init__(self, old: VmdDatasetListItem, new: VmdDatasetListItem):
        self.old = old 
        self.new = new


class VmdCurrentDataset(QObject):

    dataset_edited    = pyqtSignal(VmdDatasetListItem)
    selection_changed = pyqtSignal(VmdSelectionChangedData)

    disable_prev_frame_btn = pyqtSignal(bool)
    disable_next_frame_btn = pyqtSignal(bool)
    disable_read_frame_btn = pyqtSignal(bool)
    
    def __init__(self):
        super(VmdCurrentDataset, self).__init__()
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

    def _subscribe_to_list_item(self, item: VmdDatasetListItem):
        item.dataset_edited.connect(self.get_dataset_edited_slot)
        item.dataset_edited.connect(self.check_curr_frame_no)

    def _unsubscribe_to_list_item(self, item: VmdDatasetListItem):
        if item:
            item.dataset_edited.disconnect(self.get_dataset_edited_slot)
            item.dataset_edited.disconnect(self.check_curr_frame_no)

    def check_curr_frame_no(self, item: VmdDatasetListItem = None):   
        disable_read_btn = False
        disable_prev_frame_btn = False
        disable_next_frame_btn = False

        if item is None or item._frames_no == 0:
            disable_prev_frame_btn = True
            disable_next_frame_btn = True
            disable_read_btn = True
        elif not (item._curr_frame < item._frames_no and item._curr_frame > 1):
            if item._frames_no == item._curr_frame:
                disable_next_frame_btn = True
            if item._curr_frame == 1:
                disable_prev_frame_btn = True
        
        self.disable_next_frame_btn.emit(disable_next_frame_btn)
        self.disable_prev_frame_btn.emit(disable_prev_frame_btn)
        self.disable_read_frame_btn.emit(disable_read_btn)
    
    def set_current_frame(self, val: int | str):
        if self._current_dli:
            self._current_dli.set_current_frame(int(val))

    def next_frame(self):
        if self._current_dli:
            self._current_dli.next_frame()

    def previous_frame(self):
        if self._current_dli:
            self._current_dli.previous_frame()

    def get_data(self):
        if self._current_dli:
            return self._current_dli.get_data()
    
    def refresh_data(self):
        if self._current_dli:
            self._current_dli.refresh_data()
    
    def recalculate_data(self):
        if self._current_dli:
            self._current_dli.recalculate_data()