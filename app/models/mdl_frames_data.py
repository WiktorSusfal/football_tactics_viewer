from enum     import Enum
import pandas as pd

from app.models.components.mdl_json_model_base import MdlJsonModelBase

MIN_PLAYER_X_COORD = 0
MAX_PLAYER_X_COORD = 120
MIN_PLAYER_Y_COORD = 0
MAX_PLAYER_Y_COORD = 80

class FramesJsonAttrNames(Enum):
    """
    Contains possible names of json attributes from raw json file that is a base for Pandas DataFrame storing frames' data.
    Compare with /resources/generated/frames_scheme.json
    """
    EVENT_UUID      = 'event_uuid'
    VISIBLE_AREA    = 'visible_area'
    FREEZE_FRAME    = 'freeze_frame'
    TEAMMATE        = 'teammate'
    ACTOR           = 'actor'
    KEEPER          = 'keeper'
    LOCATION        = 'location'

class FramesMainColNames(Enum):
    EVENT_UUID      = 'event_uuid'

class FramesVisibleAreaColNames(Enum):
    CORNER_NO       = 'corner_no'
    X_COORD         = 'x'
    Y_COORD         = 'y'

class FramesPlayersColNames(Enum):
    TEAMMATE        = 'teammate'
    ACTOR           = 'actor'
    KEEPER          = 'keeper'
    LOC_X           = 'loc_x'
    LOC_Y           = 'loc_y'


class MdlFramesData(MdlJsonModelBase):

    EAN = FramesJsonAttrNames
    MCN = FramesMainColNames
    VCN = FramesVisibleAreaColNames
    PCN = FramesPlayersColNames

    def __init__(self, j_filepath: str = None):
        super(MdlFramesData, self).__init__(j_filepath=j_filepath)

        self._frames_no = 0
        self._main_frame         = pd.DataFrame()
        self._visible_area_frame = pd.DataFrame()
        self._players_frame      = pd.DataFrame()

    def get_frames_no(self) -> int:
        return self._frames_no
    
    def get_event_uuid_by_frame(self, frame_no: int) -> str:
        if frame_no < 1:
            return None
        
        return self._main_frame.loc[frame_no, self.MCN.EVENT_UUID.value]
    
    def get_visible_area_frame_by_frame(self, frame_no: int) -> pd.DataFrame:
        return self._visible_area_frame.loc[self._visible_area_frame.index == frame_no]
    
    def get_players_frame_by_frame(self, frame_no: int) -> pd.DataFrame:
        return self._players_frame.loc[self._players_frame.index == frame_no]
    
    def _get_empty_main_frame(self) -> pd.DataFrame:
        return pd.DataFrame(columns=[e.value for e in self.MCN])
    
    def _get_empty_visible_area_frame(self) -> pd.DataFrame:
        return pd.DataFrame(columns=[e.value for e in self.VCN])

    def _get_empty_players_frame(self) -> pd.DataFrame:
        return pd.DataFrame(columns=[e.value for e in self.PCN])
    
    def reset_result_frames(self):
        self._frames_no          = 0
        self._main_frame         = self._get_empty_main_frame()
        self._visible_area_frame = self._get_empty_visible_area_frame()
        self._players_frame      = self._get_empty_players_frame()

    def get_result_frames(self):
        raw_df = self._get_raw_data_frame()
        self._main_frame         = self._get_main_frame(raw_df)
        self._frames_no          = len(self._main_frame.index)

        self._visible_area_frame = self._get_visible_area_frame(raw_df)
        self._players_frame      = self._get_players_frame(raw_df)

    def _get_main_frame(self, raw_src_df: pd.DataFrame) -> pd.DataFrame:
        eframe_columns =[ self.EAN.EVENT_UUID.value ]
        raw_df: pd.DataFrame = raw_src_df.copy()[eframe_columns]

        return raw_df
    
    def _get_visible_area_frame(self, raw_src_df: pd.DataFrame) -> pd.DataFrame:
        eframe_columns =[ self.EAN.EVENT_UUID.value, self.EAN.VISIBLE_AREA.value ]
        raw_df: pd.DataFrame = raw_src_df.copy()[eframe_columns]
        
        # getting data from original "visible_area" column
        # it is a list of float coordinates of polygon's corners (on 2D plane)
        # each two consecutive values create (x, y) coordinates of another corner
        # number of corners per frame polygon is variable
        # the goal is to store each corner's coordinates in separate row
        
        # step 1 - group coordinates into pairs, store that pairs in list
        raw_df[self.EAN.VISIBLE_AREA.value] = \
            raw_df[self.EAN.VISIBLE_AREA.value].apply(lambda x: [pair for pair in zip(x[::2], x[1::2])])
        
        # step 2 - explode this lists with original index - result: each pair in separate row
        raw_df = raw_df.explode(self.EAN.VISIBLE_AREA.value)

        # step 3 - add corner number for each corner - in the scope of particular frame
        raw_df[self.VCN.CORNER_NO.value] = raw_df.groupby(level = 0).cumcount()

        # step 4 - separate coords from pairs to two standalone columns
        raw_df[[
              self.VCN.X_COORD.value
            , self.VCN.Y_COORD.value
        ]] = raw_df[self.EAN.VISIBLE_AREA.value].apply(lambda x : pd.Series({ 'c1': x[0]
                                                                            , 'c2': x[1]}))
        
        # step 5 - drop the pair column
        raw_df = raw_df.drop(columns=[self.EAN.EVENT_UUID.value, self.EAN.VISIBLE_AREA.value])
        
        return raw_df
    
    def _get_players_frame(self, raw_src_df: pd.DataFrame) -> pd.DataFrame:
        eframe_columns =[ self.EAN.EVENT_UUID.value, self.EAN.FREEZE_FRAME.value ]
        raw_df: pd.DataFrame = raw_src_df.copy()[eframe_columns]

        # each row of 'freeze_frame' column contains list of dictionaries 
        # each dictionary represents single player details at a particular event
        # the goal is to parse every list of dicts into separate rows (each row for one dictionary)

        # step 1 - explode lists of dicts with original index 
        raw_df = raw_df.explode(self.EAN.FREEZE_FRAME.value)

        # step 2 - move particular dict's attributes to separate columns
        raw_df[[
              self.PCN.TEAMMATE.value
            , self.PCN.ACTOR.value 
            , self.PCN.KEEPER.value
            , self.PCN.LOC_X.value 
            , self.PCN.LOC_Y.value
        ]] = raw_df[self.EAN.FREEZE_FRAME.value].apply(lambda x: pd.Series({ 'c1': x[self.EAN.TEAMMATE.value]
                                                                            ,'c2': x[self.EAN.ACTOR.value]
                                                                            ,'c3': x[self.EAN.KEEPER.value]
                                                                            ,'c4': x[self.EAN.LOCATION.value][0]
                                                                            ,'c5': x[self.EAN.LOCATION.value][1]}))
        
        # step 3 - delete not needed columns 
        raw_df = raw_df.drop(columns=[self.EAN.EVENT_UUID.value, self.EAN.FREEZE_FRAME.value])

        return raw_df