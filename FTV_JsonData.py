"""
Module contains definition of the class ('FTV_JsonDataManager') responsible for loading raw data from given json files,
normalizing it and exposing as Pandas' dataframes.
"""


import json
import pandas as pd
from enum import Enum







class FTV_DataReadModes(Enum):
    """
    Contains possible values of 'mode' parameter describing which kind of data is being read - LINEUPS, EVENTS or FRAMES
    """
    LINEUPS = 0
    EVENTS = 1
    FRAMES = 2








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

        
        self.frames_main = pd.DataFrame()
        
        self.frames_visible_area = pd.DataFrame()
        self.frames_players = pd.DataFrame()

        self.events_main = pd.DataFrame()


        self.lineups_main = pd.DataFrame()

    
  
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

    
    d

