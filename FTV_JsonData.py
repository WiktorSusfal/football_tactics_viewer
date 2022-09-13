"""
Module contains definition of the class ('FTV_JsonDataManager') responsible for loading raw data from given json files,
normalizing it and exposing as Pandas' dataframes.
"""


import json
import pandas as pd
from enum import Enum


def returnJsonData(filepath: str):
    """
    Returns structured json data read from file - in form of dictionary or list of dictionaries

    :param filepath: String filepath of the file containing source data.
    :return: Structured json data read from file - in form of dictionary or list of dictionaries.
    """
    with open(filepath) as json_file:
        json_data = json.load(json_file)

    return json_data


def parseJsonToTable(list_of_json_objects):
    """
    Parses structured json data to pandas dataframe. Accepts list of dictionaries (json structured data objects) or
    single dictionary.

    :param list_of_json_objects: List of dictionaries (json structured data objects) or single dictionary.
    :return: Pandas DataFrame
    """
    if not isinstance(list_of_json_objects, list):
        list_of_json_objects = [list_of_json_objects]

    for json_object in list_of_json_objects:
        if not isinstance(json_object, dict):
            raise ValueError('Invalid content of json data provided. Expected list of dictionaries (json objects)')

    return pd.read_json(json.dumps(list_of_json_objects), orient='records')


class FTV_DataReadModes(Enum):
    """
    Contains possible values of 'mode' parameter describing which kind of data is being read - LINEUPS, EVENTS or FRAMES
    """
    LINEUPS = 0
    EVENTS = 1
    FRAMES = 2


class FTV_FramesJsonAttrNames(Enum):
    """
    Contains possible names of json attributes from raw json file that is a base for Pandas DataFrame -
    "frames_main" which is the attribute of 'FTV_JsonDataManager' class.
    """
    EVENT_UUID = 'event_uuid'
    VISIBLE_AREA = 'visible_area'
    FREEZE_FRAME = 'freeze_frame'
    TEAMMATE = 'teammate'
    ACTOR = 'actor'
    KEEPER = 'keeper'
    LOCATION = 'location'


class FTV_EventsJsonAttrNames(Enum):
    """
    Contains possible names of columns for Pandas DataFrame - "events_main" that is the attribute of
    'FTV_JsonDataManager' class.
    """
    ID = 'id'
    PERIOD = 'period'
    TIMESTAMP = 'timestamp'
    MINUTE = 'minute'
    SECOND = 'second'
    TYPE = 'type'
    TYPE_ID = 'id'
    TYPE_NAME = 'name'
    EVENT_TEAM = 'team'
    EVENT_TEAM_ID = 'id'
    EVENT_TEAM_NAME = 'name'


class FTV_LineupsJsonAttrNames(Enum):
    """
    Contains possible names of columns for Pandas DataFrame - "lineups_main" that is the attribute of
    'FTV_JsonDataManager' class.
    """
    TEAM_ID = 'team_id'
    TEAM_NAME = 'team_name'


class FTV_JsonDataManager:
    """
    Class responsible for reading raw json data from given files, parse the data, normalize and store in relevant
    pandas DataFrames. This data is then visualized on application GUI - from 'FTV_UI_Manager' module.
    """

    def __init__(self, obj_name='default'):
        # friendly name of object
        self.object_name = obj_name

        # string file patch for relevant json files containing data to analyze
        self.frames_filepath = str()
        self.events_filepath = str()
        self.lineups_filepath = str()

        # raw json read from file by json.load function
        self.frames_raw_json = list()
        self.events_raw_json = list()
        self.lineups_raw_json = list()

        # raw dataframes with columns that conform the json file structures. created by 'pandas.read_json' function
        self.frames_raw_dataframe = pd.DataFrame()
        self.events_raw_dataframe = pd.DataFrame()
        self.lineups_raw_dataframe = pd.DataFrame()

        # set of normalized dataframes containing data related to player positions. given columns are present after
        # calling 'normalizeJsonData' function
        # ########################################################################
        # 'frames_main' is a main dataframe that connects data from other 'frames_...' dataframes and 'events_main' one
        # 'frames_main' contain columns: ['main_event_idx', 'event_uuid']
        # main_event_idx    - unique integer index for joining other 'frames_...' dataframes
        # event_uuid        - unique string uuid of event - key for joining 'events_main' dataframe
        self.frames_main = pd.DataFrame()
        # following dataframe contains data about visible area where the current event takes place (visible
        # area recorded by video cameras during football game)
        # columns : ['main_event_idx', 'corner_no', 'x', 'y']
        # main_event_idx    - integer - key for joining data from 'frames_main'
        # corner_no         - integer - number of polygon corner (the polygon which determines the visible area)
        # x                 - x coordinate originally normalized to range [0, 120]
        # y                 - y coordinate originally normalized to range [0, 80]
        self.frames_visible_area = pd.DataFrame()
        # following dataframe contains data about i.e. players positions in current dataframe
        # columns : ['main_event_idx teammate', 'actor', 'keeper', 'loc_x', 'loc_y']
        # main_event_idx    - integer - references 'frames_main' dataframe
        # teammate          - boolean - True if the player is a member of team related to current event
        # actor             - boolean - True if the player is a performer of the current event
        # keeper            - boolean - True if the player is the keeper
        # loc_x             - float - x coordinate of player position (when player is a member of team related to
        #                    current event,then 0 is a beginning of his half of pitch, 120 is the end of whole pitch).
        #                    originally normalized to range [0, 120]
        # loc_y             - float - y coordinate of player position, originally normalized to range [0, 80]
        self.frames_players = pd.DataFrame()

        # set of normalized pandas' dataframes containing data related to events. given columns are present after
        # calling 'normalizeJsonData' function
        # ######################################################################
        # column names are stored in enum class 'FTV_EventsJsonAttrNames', conform the following enum class attributes:
        # [ID, PERIOD, TIMESTAMP, MINUTE, SECOND, TYPE_ID, TYPE_NAME]
        # ID                - unique event string uuid - key for joining 'self.frames_main' dataframe
        # PERIOD            - number of the period of football match (int)
        # TIMESTAMP         - string containing current match timestamp (hh:mm:ss.fff)
        # MINUTE            - minute of game (int)
        # SECOND            - second of game (int)
        # 'event_type_id'   - event type numeric id (int) - it needed to be assigned manually: this column is a result
        #                   of the normalization process (of the TYPE column) and its original name (TYPE_ID in Enum
        #                   mentioned above) created a conflict with first column of this dataframe (ID)
        # 'event_name'      - event name (str) - the same case as for 'event_type_id' column. original name created
        #                   conflicts with other columns - it had to be reassigned manually
        # 'event_team_id',   - integer id of the team related to current event. it is needed to players'
        #                   positions visualization, since the location coordinates from the 'frames_players' dataframe
        #                   are given in a following way:
        #                         - the 0 on the X-axis is the beginning of actor team's pitch half
        #                         - the 120 in the X-axis is the end of the opponent's pitch half.
        #                   as mentioned for 'event_type_id' - column name also had to be assigned manually
        # 'event_team_name   - string - name of team that currently is in possession of ball
        self.events_main = pd.DataFrame()

        # set of normalized pandas' dataframes containing data related to lineups. given columns are present after
        # calling 'normalizeJsonData' function
        # ######################################################################
        # column names are stored in enum class 'FTV_LineupsJsonAttrNames', conform the following enum class attributes:
        # [TEAM_ID, TEAM_NAME]
        # TEAM_ID   - integer - id of team
        # TEAM_NAME - string - name of team
        self.lineups_main = pd.DataFrame()

    def assignFilePaths(self, mode: int, path: str):
        """
        Function for assigning relevant file paths. Updates class attributes, doesn't return anything.
        'mode' parameter determines what data is read. Possible values for this param provided in 'FTV_DataReadModes'
        enum class.

        :param mode: Integer that determines what kind of data is read (EVENTS, LINEUPS or FRAMES).
        :param path: String variable representing path of the file containing data.
        """

        match mode:
            case FTV_DataReadModes.LINEUPS.value:
                self.lineups_filepath = path
            case FTV_DataReadModes.EVENTS.value:
                self.events_filepath = path
            case FTV_DataReadModes.FRAMES.value:
                self.frames_filepath = path
            case _:
                raise ValueError('Invalid value for data read mode provided in "assignFilePaths" function')

    def readJsonData(self, mode: int):
        """
        Function for reading data from particular Json file. Updates class attributes, doesn't return anything.

        :param mode: Integer that determines what data is read - EVENTS, LINEUPS or FRAMES. Possible values provided in
            'FTV_DataReadModes' class
        :return: None
        """
        match mode:
            case FTV_DataReadModes.LINEUPS.value:
                if self.lineups_filepath:
                    self.lineups_raw_json = returnJsonData(self.lineups_filepath)
                    self.lineups_raw_dataframe = parseJsonToTable(self.lineups_raw_json)
            case FTV_DataReadModes.EVENTS.value:
                if self.events_filepath:
                    self.events_raw_json = returnJsonData(self.events_filepath)
                    self.events_raw_dataframe = parseJsonToTable(self.events_raw_json)
            case FTV_DataReadModes.FRAMES.value:
                if self.frames_filepath:
                    self.frames_raw_json = returnJsonData(self.frames_filepath)
                    self.frames_raw_dataframe = parseJsonToTable(self.frames_raw_json)
            case _:
                raise ValueError('Invalid value for data read mode provided in "readJsonData" function')

    def normalizeJsonData(self):
        """
        High-level normalization function - manages the data normalization process for all json file types.

        Normalization is about extracting structured data stored in dataframe columns (list, dictionaries) and
        transferring it to another dataframes (one list/dict value by column) with relevant key column that references
        original table.

        If structured data has always the same length, it is being "unpacked" to new columns in existing original
        dataframe.

        :return: None
        """
        if len(self.frames_raw_dataframe.index) > 0:
            self.normalizeFramesData()
        if len(self.events_raw_dataframe.index) > 0:
            self.normalizeEventsData()
        if len(self.lineups_raw_dataframe.index) > 0:
            self.normalizeLineupsData()

    def normalizeFramesData(self):
        self.normalizeFD_visibleAreaColumn()
        self.normalizeFD_freezeFrameColumn()

        # create new simple named index for main frames table
        index_column = [i for i in range(0, len(self.frames_raw_dataframe[FTV_FramesJsonAttrNames.EVENT_UUID.value]))]
        index_series = pd.Series(index_column, name='main_event_idx')
        # create main frames table
        self.frames_main = pd.concat([index_series, self.frames_raw_dataframe], axis=1)

        self.frames_raw_dataframe = pd.DataFrame()

    def normalizeFD_visibleAreaColumn(self):
        """
        Sub-function for normalization the data from 'visible_area' column (data read from 'visible_area' json objects).

        :return: None
        """
        visible_area_column_list = ['main_event_idx', 'corner_no', 'x', 'y']
        visible_area_series = self.frames_raw_dataframe[FTV_FramesJsonAttrNames.VISIBLE_AREA.value]
        self.frames_visible_area = pd.DataFrame(columns=visible_area_column_list)

        for idx, coordinates_list in visible_area_series.items():
            # 'visible_area' is a polygon, so it has variable number of corners. Coordinates must be stored
            # in pairs with additional column which is current number of polygon's corner
            corner_no = 0
            while len(coordinates_list) > 0:
                if len(coordinates_list) == 1:
                    raise ValueError('Incorrect length of "visible_area" coordinates list. Must be even')

                coord_pair = coordinates_list[:2]
                coordinates_list = coordinates_list[2:]

                value_row = [idx, corner_no]
                value_row.extend(coord_pair)

                self.frames_visible_area = pd.concat([self.frames_visible_area,
                                                      pd.DataFrame([value_row], columns=visible_area_column_list)],
                                                     ignore_index=True
                                                     )
                corner_no += 1

        del self.frames_raw_dataframe[FTV_FramesJsonAttrNames.VISIBLE_AREA.value]

    def normalizeFD_freezeFrameColumn(self):
        """
        Sub-function for normalization the data from 'freeze_frames' column (data read from 'freeze_frames' json objects)

        :return: None
        """
        freeze_frame_series = self.frames_raw_dataframe[FTV_FramesJsonAttrNames.FREEZE_FRAME.value]
        # the attribute names of nested json object
        freeze_frame_column_list = ['main_event_idx', 'teammate', 'actor', 'keeper', 'loc_x', 'loc_y']
        self.frames_players = pd.DataFrame(columns=freeze_frame_column_list)

        # 'player_detail_list' is a copy of a single cell from original column 'freeze_frame' which contains
        # list of dictionaries that represent single player details at particular event. This loop is to
        # parse every list of dicts into separate rows (each row for one json object (dictionary)) with additional
        # column 'main_event_idx' that references to relevant event uid in main table
        for idx, player_detail_list in freeze_frame_series.items():
            # add column 'main_event_idx' to every dictionary in the list (every json object in array) to be able to
            # reference the main and other tables. split list of location coordinates into 2 separate attributes
            for dictionary in player_detail_list:
                dictionary['main_event_idx'] = idx
                dictionary['loc_x'] = dictionary[FTV_FramesJsonAttrNames.LOCATION.value][0]
                dictionary['loc_y'] = dictionary[FTV_FramesJsonAttrNames.LOCATION.value][1]
                del dictionary[FTV_FramesJsonAttrNames.LOCATION.value]

            self.frames_players = pd.concat([self.frames_players,
                                             pd.DataFrame.from_records(player_detail_list)],
                                            ignore_index=True
                                            )

        del self.frames_raw_dataframe[FTV_FramesJsonAttrNames.FREEZE_FRAME.value]

    def normalizeEventsData(self):
        # so far only single attributes of main json objects are used,
        # so 'events_main' dataframe is a subset of original raw one
        self.events_main = self.events_raw_dataframe[[
            FTV_EventsJsonAttrNames.ID.value,
            FTV_EventsJsonAttrNames.PERIOD.value,
            FTV_EventsJsonAttrNames.TIMESTAMP.value,
            FTV_EventsJsonAttrNames.MINUTE.value,
            FTV_EventsJsonAttrNames.SECOND.value,
            FTV_EventsJsonAttrNames.TYPE.value,
            FTV_EventsJsonAttrNames.EVENT_TEAM.value
        ]]
        self.events_raw_dataframe = pd.DataFrame()

        # normalize 'event_type' column
        event_details_rows = []
        for idx, row in self.events_main.iterrows():
            # 'event_type' is a list where values from a dictionary (with two keys: 'id' and 'name') are copied.
            # code below is to normalize this original data and append to main table as new columns
            event_type = [
                row[FTV_EventsJsonAttrNames.TYPE.value][FTV_EventsJsonAttrNames.TYPE_ID.value],
                row[FTV_EventsJsonAttrNames.TYPE.value][FTV_EventsJsonAttrNames.TYPE_NAME.value]
            ]
            event_details_rows.append(event_type)

        # create new dataframe that contains newly created columns (results of the normalization)
        event_details_dataframe = pd.DataFrame(event_details_rows, columns=['event_type_id', 'event_name'])
        # add new columns from dataframe created above to main dataframe and delete non-normalized original column
        self.events_main = pd.concat([self.events_main, event_details_dataframe], axis=1)
        del self.events_main[FTV_EventsJsonAttrNames.TYPE.value]

        # normalize 'possession_team' column
        possession_team_rows = []
        for idx, row in self.events_main.iterrows():
            # 'EVENT_TEAM_details' is a list where values from a dictionary (with two keys: 'id' and 'name') are copied.
            # the dictionary mentioned above is stored in a column 'row[FTV_EventsJsonAttrNames.EVENT_TEAM.value]'
            event_team_details = [
                row[FTV_EventsJsonAttrNames.EVENT_TEAM.value][FTV_EventsJsonAttrNames.EVENT_TEAM_ID.value],
                row[FTV_EventsJsonAttrNames.EVENT_TEAM.value][FTV_EventsJsonAttrNames.EVENT_TEAM_NAME.value]
            ]
            possession_team_rows.append(event_team_details)

        # create new dataframe that contains newly created columns (results of the normalization)
        event_team_details_dataframe = pd.DataFrame(possession_team_rows, columns=['event_team_id', 'event_team_name'])
        # add new columns from dataframe created above to main dataframe and delete non-normalized original column
        self.events_main = pd.concat([self.events_main, event_team_details_dataframe], axis=1)
        del self.events_main[FTV_EventsJsonAttrNames.EVENT_TEAM.value]

        # not every event has relevant data related to player positions on pitch
        # since this app is focused to visualize the player positions, the dataframe with events data is limited
        # only to these rows where 'id' column has equivalent value in 'event_uuid' one (in frames dataframe)
        self.events_main = self.events_main.loc[self.events_main.id.isin(self.frames_main.event_uuid)]
        self.events_main.reset_index()

    def normalizeLineupsData(self):
        # only team IDs and team names are read, so result dataframe is a 2x2 matrix (2 teams taking part in game)
        self.lineups_main = self.lineups_raw_dataframe[[FTV_LineupsJsonAttrNames.TEAM_ID.value,
                                                        FTV_LineupsJsonAttrNames.TEAM_NAME.value]]

        self.lineups_raw_dataframe = pd.DataFrame()
