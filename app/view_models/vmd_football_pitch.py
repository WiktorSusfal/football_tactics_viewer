import pandas as pd
from PyQt5.QtCore       import QObject, pyqtSignal
from PyQt5.QtGui        import QColor

from app.models import LineupsFrameColNames, EventsFrameColNames, FramesPlayersColNames
from app.models import MAX_PLAYER_X_COORD, MAX_PLAYER_Y_COORD


KEEPER_ACTOR_NAME = 'keeper'
PLAYER_ACTOR_NAME = 'player'
#color sets for icons representing players on pitch
# main keys are integer indexes of teams from the lineups' pandas data frame
ICON_COLORS =  {
            0: {  KEEPER_ACTOR_NAME: QColor(255, 165, 0)
                , PLAYER_ACTOR_NAME: QColor(255, 0, 0)},
            1: {  KEEPER_ACTOR_NAME: QColor(255, 165, 0)
                , PLAYER_ACTOR_NAME: QColor(0, 0, 255)}
        }


class VmdPitchPlayersData:
    
    def __init__(self, x_coord: int, y_coord: int, color: QColor):
        self.x_coord = x_coord 
        self.y_coord = y_coord
        self.color   = color


class VmdFootballPitch(QObject):

    IC = ICON_COLORS
    LFCN = LineupsFrameColNames
    EFCN = EventsFrameColNames
    FPCN = FramesPlayersColNames

    player_pitch_data_changed = pyqtSignal(object)

    def __init__(self):
        super(VmdFootballPitch, self).__init__()
        self._last_data: pd.Series[VmdPitchPlayersData] = pd.Series()

    def get_paint_data(self) -> pd.Series:
        """
        :return: pd.Series of VmdPitchPlayersData objects
        """
        return self._last_data

    def get_data(self, frames_frame: pd.DataFrame, events_frame: pd.DataFrame, lineups_frame: pd.DataFrame):
        fdf, edf, ldf = frames_frame, events_frame, lineups_frame
        
        if fdf.empty or edf.empty or ldf.empty:
            self._last_data = pd.Series()
            self.player_pitch_data_changed.emit(self._last_data)
            return

        # get IDs of the first and the second team (first is a team in 0 row of lineups details data frame)
        f_team_id = int(ldf.loc[1][self.LFCN.TEAM_ID.value])
        s_team_id = int(ldf.loc[2][self.LFCN.TEAM_ID.value])

        # get:
        # - ID of team that is related to current event
        # - the number of period of game
        e_team_id = int(list(edf[self.EFCN.EVENT_TEAM_ID.value])[0])
        period_no = int(list(edf[self.EFCN.PERIOD.value])[0])
        # below variable indicates, which (first or second) team is the team related to the current event
        first_team_event = True if f_team_id == e_team_id else False
        event_team_idx    = 0 if first_team_event else 1

        ppd = fdf.apply(  axis=1
                        , func=lambda x: VmdPitchPlayersData(
                              x_coord=self._conditional_x_mirror(x[self.FPCN.LOC_X.value], first_team_event, period_no)
                            , y_coord=self._conditional_y_mirror(x[self.FPCN.LOC_Y.value])
                            , color  =self._return_icon_color(event_team_idx, x[self.FPCN.TEAMMATE.value], x[self.FPCN.KEEPER.value])
                        ))
        
        self._last_data = ppd
        self.player_pitch_data_changed.emit(self._last_data)
        
    def _conditional_x_mirror(self, org_x: float, first_team_event: bool, period_no = int) -> int:
        # if first team (with index 0) is related to event and period of game is odd, then coordinates stays the same.
        # otherwise, they need to be reversed to display the players properly
        if (first_team_event and period_no % 2 == 0) or (not first_team_event and period_no % 2 == 1):
            # mirror the coordinate
            org_x = MAX_PLAYER_X_COORD - org_x
        return int(org_x)
    
    def _conditional_y_mirror(self, org_y: float) -> int:
        # mirror the coordinate - pitch on GUI has reversed direction of the Y-axis
        return int(MAX_PLAYER_Y_COORD - org_y)
    
    def _return_icon_color(self, event_team_idx: int, is_teammate: bool, is_keeper: bool) -> QColor:
        """
        Returns QColor object to draw specific player icon on pitch based on the data provided.

        :param event_team_idx: Int identifier of the team that is related to the current event.
        :param is_teammate: True if current player is a teammate of the team described by 'event_team_idx' param.
        :param is_keeper: True if current player is a keeper.

        :return: qtg.QColor object.
        """
        player_team_idx = event_team_idx if is_teammate else int(bool(event_team_idx - 1))
        player_type = KEEPER_ACTOR_NAME if is_keeper else PLAYER_ACTOR_NAME

        return self.IC[player_team_idx][player_type]