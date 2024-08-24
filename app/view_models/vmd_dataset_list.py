from PyQt5.QtCore       import QObject, pyqtSignal

from app.view_models.vmd_dataset_list_item import VmdDatasetListItem


class VmdDatasetList(QObject):

    list_item_added   = pyqtSignal(VmdDatasetListItem)
    list_item_deleted = pyqtSignal(VmdDatasetListItem)

    def __init__(self):
        super(VmdDatasetList, self).__init__()
        self._dli_list: list[VmdDatasetListItem] = list()

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

    def _subscribe_to_list_item(self, item: VmdDatasetListItem):
        item.delete_item_order.connect(self.delete_item)

    def _unsubscribe_to_list_item(self, item: VmdDatasetListItem):
        item.delete_item_order.disconnect( self.delete_item)