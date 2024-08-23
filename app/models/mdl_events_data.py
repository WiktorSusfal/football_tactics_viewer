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


class MdlEventsData(MdlJsonModelBase):

    EAN = EventsJsonAttrNames

    def __init__(self, j_filepath: str = None):
        super(MdlEventsData, self).__init__(j_filepath=j_filepath)

    def get_result_frames(self):
        pass