import PyQt5.QtWidgets as qtw
from PyQt5.QtCore import QObject, pyqtSignal
from enum import Enum


DEFAULT_DATASET_NAME   = '<dataset name {no}>'
FILTER_JSON_DATA_FILES = 'Json Files (*.json)'


class VmdDatasetDataType(Enum):
    LINEUPS = 0
    EVENTS  = 1
    FRAMES  = 2


class VmdDatasetListItem(QObject):

    cnt = -1

    def __init__(self, dataset_name: str = None):
        super(VmdDatasetListItem, self).__init__()

        VmdDatasetListItem.cnt += 1
        self._cnt = VmdDatasetListItem.cnt

        self._dataset_name: str     = self._get_dataset_name(dataset_name)
        self._frames_filepath: str  = None
        self._events_filepath: str  = None
        self._lineups_filepath: str = None

    def _get_dataset_name(self, dataset_name: str) -> str:
        return dataset_name or DEFAULT_DATASET_NAME.format(no=str(self._cnt))
    
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

        filepath, check = qtw.QFileDialog.getOpenFileName(
                                  parent    = None
                                , caption   = f'Football Tactics Viewer - choose path to json {data_type_name} data'
                                , directory = ''
                                , filter    = FILTER_JSON_DATA_FILES)
        if check:
            if data_type_name == VmdDatasetDataType.LINEUPS.name:
                self._lineups_filepath = filepath
            if data_type_name == VmdDatasetDataType.EVENTS.name:
                self._events_filepath = filepath
            if data_type_name == VmdDatasetDataType.FRAMES.name:
                self._frames_filepath = filepath 