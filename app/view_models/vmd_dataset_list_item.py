from enum               import Enum
from PyQt5.QtWidgets    import QFileDialog
from PyQt5.QtCore       import QObject, pyqtSignal


DEFAULT_DATASET_NAME   = '<dataset name {no}>'
DEFAULT_FILE_PATH      = '<no data>'
FILTER_JSON_DATA_FILES = 'Json Files (*.json)'


class VmdDatasetDataType(Enum):
    LINEUPS = 0
    EVENTS  = 1
    FRAMES  = 2


class VmdDatasetListItem(QObject):

    cnt = -1

    dataset_name_changed    = pyqtSignal(str)
    frames_filepath_changed = pyqtSignal(str)
    events_filepath_changed = pyqtSignal(str)
    lineups_filepath_changed = pyqtSignal(str)

    delete_item_order = pyqtSignal(int)

    def __init__(self, dataset_name: str = None):
        super(VmdDatasetListItem, self).__init__()

        VmdDatasetListItem.cnt += 1
        self._cnt = VmdDatasetListItem.cnt

        self._dataset_name: str     = None 
        self.set_dataset_name(dataset_name)
        self._frames_filepath: str  = DEFAULT_FILE_PATH
        self._events_filepath: str  = DEFAULT_FILE_PATH
        self._lineups_filepath: str = DEFAULT_FILE_PATH

    def get_id(self) -> int:
        return self._cnt

    def set_dataset_name(self, value: str):
        self._dataset_name = self._get_dataset_name(value)
        self.dataset_name_changed.emit(self._dataset_name)

    def set_frames_filepath(self, value: str):
        self._frames_filepath = value or DEFAULT_FILE_PATH
        self.frames_filepath_changed.emit(self._frames_filepath)

    def set_events_filepath(self, value: str):
        self._events_filepath = value or DEFAULT_FILE_PATH
        self.events_filepath_changed.emit(self._events_filepath)

    def set_lineups_filepath(self, value: str):
        self._lineups_filepath = value or DEFAULT_FILE_PATH
        self.lineups_filepath_changed.emit(self._lineups_filepath)

    def _get_dataset_name(self, dataset_name: str) -> str:
        return dataset_name or DEFAULT_DATASET_NAME.format(no=str(self._cnt))
    
    def delete_item(self):
        self.delete_item_order.emit(self._cnt)
    
    def assign_data_filepath(self, data_type: int):
        """
        Function connected to QPushButton object from dataset list GUI element. Opens
        QFileDialog and allows to choose the path to the relevant json file containing source data. 

        :return: None
        """

        try:
            data_type_name = VmdDatasetDataType(data_type).name
        except:
            raise Exception(f'{self.__class__.__name__}: invalid data type provided')

        filepath, check = QFileDialog.getOpenFileName(
                                  parent    = None
                                , caption   = f'Football Tactics Viewer - choose path to json {data_type_name} data'
                                , directory = ''
                                , filter    = FILTER_JSON_DATA_FILES)
        if check:
            if data_type_name == VmdDatasetDataType.LINEUPS.name:
                self.set_lineups_filepath(filepath)
            if data_type_name == VmdDatasetDataType.EVENTS.name:
                self.set_events_filepath(filepath)
            if data_type_name == VmdDatasetDataType.FRAMES.name:
                self.set_frames_filepath(filepath) 