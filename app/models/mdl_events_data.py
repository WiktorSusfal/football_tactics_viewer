from enum     import Enum
import pandas as pd

from app.models.components.mdl_json_model_base import MdlJsonModelBase


class EventsJsonAttrNames(Enum):
    """
    Contains possible names of columns for Pandas DataFrame storing events' data
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
    Compare with /resources/generated/events_scheme.json
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
    
    def _reset_result_frames(self):
        self._events_frame = self._get_empty_events_frame()

    def get_result_frames(self, filter_id_series: pd.Series = None):
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

        # not every event has relevant data related to players' positions on pitch.
        # since this app is focused to visualize the player positions, the data frame with events data is limited
        # only to these rows where 'id' column has equivalent value in 'event_uuid' one (in frames-related data frame)
        if filter_id_series:
            raw_df = raw_df.loc[raw_df[self.EAN.ID.value].isin(filter_id_series)]
            raw_df.reset_index()

        self._events_frame = raw_df
        print(raw_df)