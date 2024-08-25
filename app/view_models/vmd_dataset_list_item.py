import pandas           as pd
from enum               import Enum
from PyQt5.QtWidgets    import QFileDialog
from PyQt5.QtCore       import QObject, pyqtSignal

from app.models import MdlEventsData, MdlFramesData, MdlLineupsData


DEFAULT_DATASET_NAME   = '<dataset name {no}>'
DEFAULT_FILE_PATH      = '<no data>'
FILTER_JSON_DATA_FILES = 'Json Files (*.json)'

DEFAULT_TIMESTAMP = 'N/A'
DEFAULT_CURR_FRAME = 0 
DEFAULT_FRAMES_NO  = 0


class VmdDatasetDataType(Enum):
    LINEUPS = 0
    EVENTS  = 1
    FRAMES  = 2


class VmdDatasetListItem(QObject):

    cnt = -1

    dataset_name_changed    = pyqtSignal(str)
    dataset_edited          = pyqtSignal()

    delete_item_order = pyqtSignal(int)

    def __init__(self, dataset_name: str = None):
        super(VmdDatasetListItem, self).__init__()

        VmdDatasetListItem.cnt += 1
        self._cnt = VmdDatasetListItem.cnt

        self._events_model = MdlEventsData()
        self._frames_model = MdlFramesData()
        self._lineups_model = MdlLineupsData()

        self._dataset_name: str     = None 
        self.set_dataset_name(dataset_name)
        self._frames_filepath: str  = DEFAULT_FILE_PATH
        self._events_filepath: str  = DEFAULT_FILE_PATH
        self._lineups_filepath: str = DEFAULT_FILE_PATH

        self._frames_no  = self._frames_model.get_frames_no() or DEFAULT_FRAMES_NO
        self._curr_frame = DEFAULT_CURR_FRAME 

    def get_id(self) -> int:
        return self._cnt
    
    def get_team_names(self) -> tuple[str, str]:
        return self._lineups_model.get_team_names()
    
    def get_timestamp(self) -> str:
        event_uuid = self._frames_model.get_event_uuid_by_frame(self._curr_frame)
        if not event_uuid:
            return DEFAULT_TIMESTAMP
        
        mmn, sec = self._events_model.get_timestamp_raw_by_event_uuid(event_uuid)
        if mmn is None or sec is None: 
            return DEFAULT_TIMESTAMP

        return self._format_timestamp(mmn, sec) or DEFAULT_TIMESTAMP
    
    def _format_timestamp(self, minute: int, second: int) -> str:
        return f"{str(minute).rjust(2, '0')} : {str(second).rjust(2, '0')}"
    
    def get_frames_no_data(self) -> str:
        return str(self._frames_no)
    
    def get_curr_frame_data(self) -> str:
        return str(self._curr_frame)
    
    def _get_dataset_name(self, dataset_name: str) -> str:
        return dataset_name or DEFAULT_DATASET_NAME.format(no=str(self._cnt))

    def set_dataset_name(self, value: str):
        self._dataset_name = self._get_dataset_name(value)
        self.dataset_name_changed.emit(self._dataset_name)

    def set_frames_filepath(self, value: str):
        self._frames_model.set_json_filepath(value)
        self._frames_filepath = value or DEFAULT_FILE_PATH
        self.dataset_edited.emit()

    def set_events_filepath(self, value: str):
        self._events_model.set_json_filepath(value)
        self._events_filepath = value or DEFAULT_FILE_PATH
        self.dataset_edited.emit()

    def set_lineups_filepath(self, value: str):
        self._lineups_model.set_json_filepath(value)
        self._lineups_filepath = value or DEFAULT_FILE_PATH
        self.dataset_edited.emit()
    
    def _set_frames_no(self, val: int):
        self._frames_no = val or 0
        self.dataset_edited.emit()

    def set_current_frame(self, val: int):
        self._curr_frame = min(max(1, int(val)), self._frames_no) 
        self.dataset_edited.emit()

    def previous_frame(self):
        tgt = self._curr_frame - 1
        self._curr_frame = min(max(1, tgt), self._frames_no)
        self.dataset_edited.emit()

    def next_frame(self):
        tgt = self._curr_frame + 1
        self._curr_frame = min(self._frames_no, tgt)
        self.dataset_edited.emit()

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

    def get_data(self) -> tuple[pd.DataFrame]:
        """
        :return lineups_frame, players_frame, events_frame
        """
        event_uuid = self._frames_model.get_event_uuid_by_frame(self._curr_frame)

        lineups_frame = self._lineups_model.get_lineups_frame()
        players_frame = self._frames_model.get_players_frame_by_frame(self._curr_frame)
        events_frame  = self._events_model.get_events_frame_by_event_uuid(event_uuid)

        return lineups_frame, players_frame, events_frame
        
    def refresh_data(self):
        self.set_current_frame(val=1)

    def recalculate_data(self):
        self._events_model.get_result_frames()
        self._frames_model.get_result_frames()
        self._lineups_model.get_result_frames()

        self._frames_no  = self._frames_model.get_frames_no() or DEFAULT_FRAMES_NO
        self._curr_frame = 1 if self._frames_no > 0 else DEFAULT_CURR_FRAME

        self.dataset_edited.emit()