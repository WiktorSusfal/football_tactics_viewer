from enum     import Enum
import pandas as pd

from app.models.components.mdl_json_model_base import MdlJsonModelBase


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


class MdlFramesData(MdlJsonModelBase):

    EAN = FramesJsonAttrNames

    def __init__(self, j_filepath: str = None):
        super(MdlFramesData, self).__init__(j_filepath=j_filepath)

    def get_result_frames(self):
        pass