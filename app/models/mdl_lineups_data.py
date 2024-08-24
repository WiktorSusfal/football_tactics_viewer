from enum     import Enum
import pandas as pd

from app.models.components.mdl_json_model_base import MdlJsonModelBase


class LineupsJsonAttrNames(Enum):
    """
    Contains possible names of columns for Pandas DataFrame storing lineups' data
    Compare with /resources/generated/lineups_scheme.json
    """
    TEAM_ID   = 'team_id'
    TEAM_NAME = 'team_name'


class MdlLineupsData(MdlJsonModelBase):

    EAN = LineupsJsonAttrNames

    def __init__(self, j_filepath: str = None):
        super(MdlLineupsData, self).__init__(j_filepath=j_filepath)
        self._teams_frame = self._get_empty_teams_frame()

    def _get_empty_teams_frame(self) -> pd.DataFrame:
        return pd.DataFrame(columns=[[e.value for e in self.EAN]])

    def get_result_frames(self):
        raw_df = self._get_raw_data_frame()
        self._teams_frame = raw_df[[self.EAN.TEAM_ID.value, self.EAN.TEAM_NAME.value]]

    def _reset_result_frames(self):
        self._teams_frame = self._get_empty_teams_frame()