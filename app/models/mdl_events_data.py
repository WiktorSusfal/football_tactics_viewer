from enum     import Enum
import pandas as pd

from app.models.components.mdl_json_model_base import MdlJsonModelBase


class EventsJsonAttrNames(Enum):
    """
    Contains possible names of attributes of JSON storing events' data
    Compare with /resources/generated/events_scheme.json
    """
    ID              = 'id'
    PERIOD          = 'period'
    TIMESTAMP       = 'timestamp'
    MINUTE          = 'minute'
    SECOND          = 'second'
    TYPE            = 'type'
    TYPE_ID         = 'id'
    TYPE_NAME       = 'name'
    EVENT_TEAM      = 'team'
    EVENT_TEAM_ID   = 'id'
    EVENT_TEAM_NAME = 'name'

class EventsFrameColNames(Enum):
    """
    Contains possible names of columns for Pandas DataFrame storing events' data
    """
    ID              = 'id'
    PERIOD          = 'period'
    TIMESTAMP       = 'timestamp'
    MINUTE          = 'minute'
    SECOND          = 'second'
    TYPE_ID         = 'event_type_id'
    TYPE_NAME       = 'event_name'
    EVENT_TEAM_ID   = 'event_team_id'
    EVENT_TEAM_NAME = 'event_team_name'


class MdlEventsData(MdlJsonModelBase):

    EAN = EventsJsonAttrNames
    ECN = EventsFrameColNames

    def __init__(self, j_filepath: str = None):
        super(MdlEventsData, self).__init__(j_filepath=j_filepath)
        self._events_frame = self._get_empty_events_frame()

    def _get_empty_events_frame(self) -> pd.DataFrame:
        return pd.DataFrame(columns=[e.value for e in self.ECN])
    
    def get_events_frame_by_event_uuid(self, uuid: str) -> pd.DataFrame:
        return self._events_frame.loc[self._events_frame[self.ECN.ID.value] == uuid]
    
    def reset_result_frames(self):
        self._events_frame = self._get_empty_events_frame()

    def get_timestamp_raw_by_event_uuid(self, uuid: str) -> tuple[int, int]:
        if not uuid:
            return None, None
        
        df = self._events_frame
        
        mmn = df.loc[df[self.ECN.ID.value] == uuid, self.ECN.MINUTE.value].item()
        sec = df.loc[df[self.ECN.ID.value] == uuid, self.ECN.SECOND.value].item()

        return mmn, sec

    def get_result_frames(self, func_id: str) -> tuple[str, tuple[pd.DataFrame]]:
        eframe_columns =[
            self.EAN.ID.value,
            self.EAN.PERIOD.value,
            self.EAN.TIMESTAMP.value,
            self.EAN.MINUTE.value,
            self.EAN.SECOND.value,
            self.EAN.TYPE.value,
            self.EAN.EVENT_TEAM.value
        ]
        raw_df = self._get_raw_data_frame()
        raw_df: pd.DataFrame = raw_df[eframe_columns]

        # normalize event's "type" column (which originally contains dictionary with two keys)
        # to two separate columns, assuring the order of dictionary keys
        raw_df[[
                self.ECN.TYPE_ID.value
              , self.ECN.TYPE_NAME.value]
            ] = raw_df[self.EAN.TYPE.value].apply(func = lambda x: pd.Series({ 'c1':x[self.EAN.TYPE_ID.value]
                                                                              ,'c2':x[self.EAN.TYPE_NAME.value]}))
        raw_df.drop(columns=[self.EAN.TYPE.value])

        # normalize event's "team" column
        raw_df[[
                self.ECN.EVENT_TEAM_ID.value
              , self.ECN.EVENT_TEAM_NAME.value]
            ] = raw_df[self.EAN.EVENT_TEAM.value].apply(func = lambda x: pd.Series({ 'c1':x[self.EAN.EVENT_TEAM_ID.value]
                                                                                    ,'c2':x[self.EAN.EVENT_TEAM_NAME.value]}))
        raw_df.drop(columns=[self.EAN.EVENT_TEAM.value])

        return func_id, (raw_df, )

    def set_result_frames(self, events_frame: pd.DataFrame):
        self._events_frame = events_frame