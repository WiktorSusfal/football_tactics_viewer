import uuid
import pandas as pd
import FTV_JsonData
import sys

sys.path.append('./Resources/Lib')
from Resources.Lib import ObservableObjects as OOBJ
from Resources.Lib import DLW_GUIList as GUI

DEFAULT_NEW_DATASET_NAME = 'default'
FRAMES_JSON_PATH_KEY = 'frames_json_path'
EVENTS_JSON_PATH_KEY = 'events_json_path'
LINEUPS_JSON_PATH_KEY = 'lineups_json_path'
DEFAULT_FILEPATH = 'N/A'


class FTV_GUIDataManager(OOBJ.ObservableObject):
    """
    Class for managing a set of 'FTV_JsonData.FTV_JsonDataManager' objects - to interact with application GUI.
    'FTV_JsonDataManager' object are stored in a dictionary, where keys are unique uuids.

    This class acts like a ViewModel for GUI layer of application. It inherits from 'ObservableObject' class to ensure
    event-driven notifications about its attributes' changes - for every subscriber (most likely PyQt5 GUI object).
    Read more on https://github.com/WiktorSusfal/python_observable_objects
    """

    def __init__(self):
        # dictionary of complete datasets for visualizing the tactics - objects: 'FTV_JsonData.FTV_JsonDataManager'
        self.ftv_datasets = dict()

        self._current_uuid = str()
        self._current_frame = "0"
        self.no_of_frames = "0"

        self.current_event_details = pd.DataFrame()
        self.current_players_locations = pd.DataFrame()
        self.current_teams_details = pd.DataFrame()
        self.dataframes_updated = bool()

        self.json_filepaths = {FRAMES_JSON_PATH_KEY: DEFAULT_FILEPATH, EVENTS_JSON_PATH_KEY: DEFAULT_FILEPATH,
                                LINEUPS_JSON_PATH_KEY: DEFAULT_FILEPATH}

    @property
    def current_frame(self):
        return self._current_frame

    @current_frame.setter
    def current_frame(self, new_frame):

        if self.no_of_frames == "0":
            new_frame = "0"
        elif int(new_frame) < 1 or int(new_frame) > int(self.no_of_frames):
            new_frame = "1"

        self.current_event_details = self.returnEventDetails(self.current_uuid, int(new_frame) - 1)
        self.current_players_locations = self.returnPlayersLocationsInFrame(self.current_uuid, int(new_frame) - 1)

        self._current_frame = new_frame
        self.publishPropertyChanges('current_frame')

        self.publishChangesOfDataFrames()

    @property
    def current_uuid(self):
        return self._current_uuid

    @current_uuid.setter
    def current_uuid(self, new_uuid):

        if new_uuid in self.ftv_datasets:
            self._current_uuid = new_uuid
        else:
            self._current_uuid = str()

        self.current_event_details = self.returnEventDetails(new_uuid, 0)
        self.current_players_locations = self.returnPlayersLocationsInFrame(new_uuid, 0)
        self.current_teams_details = self.returnTeamsDetails(new_uuid)
        self.publishChangesOfDataFrames()

        self.no_of_frames = str(self.returnNoOfFrames(new_uuid))
        self.publishPropertyChanges('no_of_frames')

        self.updateJsonFilepaths(new_uuid)

        self.current_frame = "0"

    def updateJsonFilepaths(self, ds_uuid: str = None):

        if not ds_uuid:
            ds_uuid = self.current_uuid

        if ds_uuid in self.ftv_datasets:
            dataset = self.ftv_datasets[ds_uuid]
            self.json_filepaths[FRAMES_JSON_PATH_KEY] = \
                dataset.frames_filepath if dataset.frames_filepath else DEFAULT_FILEPATH
            self.json_filepaths[EVENTS_JSON_PATH_KEY] = \
                dataset.events_filepath if dataset.events_filepath else DEFAULT_FILEPATH
            self.json_filepaths[LINEUPS_JSON_PATH_KEY] = \
                dataset.lineups_filepath if dataset.lineups_filepath else DEFAULT_FILEPATH
        else:
            self.json_filepaths = {FRAMES_JSON_PATH_KEY: DEFAULT_FILEPATH, EVENTS_JSON_PATH_KEY: DEFAULT_FILEPATH,
                                   LINEUPS_JSON_PATH_KEY: DEFAULT_FILEPATH}

        self.publishPropertyChanges('json_filepaths')

    def setCurrentUuid(self, new_object_selected: GUI.DLW_ListElement = None):
        if not new_object_selected:
            self.current_uuid = str()
        else:
            self.current_uuid = new_object_selected.id

    def recalculateData(self):
        if self.current_uuid not in self.ftv_datasets:
            return

        for path_type, path in self.json_filepaths.items():
            if path == DEFAULT_FILEPATH:
                return

        # read new json data for selected dataset
        for modes in FTV_JsonData.FTV_DataReadModes:
            self.ftv_datasets[self.current_uuid].readJsonData(modes.value)

        self.ftv_datasets[self.current_uuid].normalizeJsonData()

        self.current_uuid = self.current_uuid

    def publishChangesOfDataFrames(self):
        self.publishPropertyChanges('current_event_details')
        self.publishPropertyChanges('current_players_locations')
        self.publishPropertyChanges('current_teams_details')
        self.publishPropertyChanges('dataframes_updated')

    def add_new_ftv_dataset(self, dataset_name: str = DEFAULT_NEW_DATASET_NAME, dataset_uuid: str = str()) -> str:
        """
        Creates new 'FTV_JsonData.FTV_JsonDataManager' object based on parameters provided and adds it to the dictionary
        of such objects.

        :param dataset_name: Optional string friendly name of the new object.
        :param dataset_uuid: Optional string unique uuid of new dataset. If not provided, an unique uuid is generated.

        :return: The uuid of new dataset.
        """
        if not dataset_uuid:
            new_uuid = str(uuid.uuid4())
        else:
            new_uuid = dataset_uuid

        self.ftv_datasets[new_uuid] = FTV_JsonData.FTV_JsonDataManager(dataset_name)

        return new_uuid

    def delete_ftv_dataset(self, dataset_uuid: str):
        """
        Deletes given dataset object ('FTV_JsonDataManager') from dictionary.

        :param dataset_uuid: String uuid of desired dataset object.
        :return: None
        """
        if dataset_uuid in list(self.ftv_datasets.keys()):
            self.ftv_datasets.pop(dataset_uuid)
        else:
            raise Exception('Tried to delete dataset that not exists')

    def uuidInListOfDatasets(self, ds_uuid: str) -> bool:
        """
        Returns true if given dataset's uuid is a key in the dictionary of datasets.

        :param ds_uuid:  String uuid of desired dataset object.
        :return: Boolean
        """
        return ds_uuid in self.ftv_datasets

    def sourceDataComplete(self, dataset_uuid: str) -> bool:

        if self.returnNoOfFrames(dataset_uuid) \
                and self.returnNoOfEvents(dataset_uuid) \
                and self.returnNoOfTeams(dataset_uuid):
            return True

        return False

    def returnEventDetails(self, dataset_uuid: str, frame_no: int) -> pd.DataFrame:
        """
        Returns pandas DataFrame containing EVENTS data for given frame number and given dataset object
        ('FTV_JsonDataManager').

        :param dataset_uuid: String uuid of desired object from dictionary of 'FTV_JsonDataManager' objects.
        :param frame_no: Integer number of desired frame.

        :return: Pandas DataFrame containing EVENTS data.
        """
        # do this only if relevant dataframes has records
        if self.sourceDataComplete(dataset_uuid):
            ds = self.ftv_datasets[dataset_uuid]
            # get the 'event_uuid' column values which correspond to the given frame number ('frame_no')
            # column that conforms frame numbers is 'main_event_idx'. it is unique column so following
            # expression always returns one-cell dataframe
            curr_event_uuid = ds.frames_main.loc[ds.frames_main.main_event_idx == frame_no]['event_uuid']
            # convert one-cell dataframe to single string value - current event uuid
            curr_event_uuid = list(curr_event_uuid)[0]
            # get the row from events data frame with corresponding uuid
            curr_event_details = ds.events_main.loc[ds.events_main.id == curr_event_uuid]

            return curr_event_details
        else:
            return pd.DataFrame()

    def returnPlayersLocationsInFrame(self, dataset_uuid: str, frame_no: int) -> pd.DataFrame:
        """
        Returns pandas DataFrame containing data about players' locations on football pitch - for given frame number
        and given dataset object ('FTV_JsonDataManager').

        :param dataset_uuid: String uuid of desired object from dictionary of 'FTV_JsonDataManager' objects.
        :param frame_no: Integer number of desired frame.
        :return:  Pandas DataFrame.
        """
        # do this only if relevant dataframes has records
        if self.sourceDataComplete(dataset_uuid):
            ds = self.ftv_datasets[dataset_uuid]
            curr_players_locations = ds.frames_players.loc[ds.frames_players.main_event_idx == frame_no]

            return curr_players_locations
        else:
            return pd.DataFrame()

    def returnTeamsDetails(self, dataset_uuid: str) -> pd.DataFrame:
        """
        Returns pandas DataFrame containing data about teams present on the football pitch - for given dataset object
        ('FTV_JsonDataManager').

        :param dataset_uuid: String uuid of desired object from dictionary of 'FTV_JsonDataManager' objects.
        :return: Pandas DataFrame.
        """

        # do this only if relevant dataframes has records
        if self.sourceDataComplete(dataset_uuid):
            ds = self.ftv_datasets[dataset_uuid]
            return ds.lineups_main
        else:
            return pd.DataFrame()

    def returnNoOfFrames(self, dataset_uuid: str) -> int:
        """
        Returns number of rows in pandas DataFrame containing data about FRAMES - for given dataset.

        :param dataset_uuid: String uuid of dataset stored in dictionary of datasets' objects ('FTV_JsonDataManager')
        :return: Integer - number of rows or 0 if no such dataset present.
        """
        if dataset_uuid and self.uuidInListOfDatasets(dataset_uuid):
            return len(self.ftv_datasets[dataset_uuid].frames_main.index)
        else:
            return 0

    def returnNoOfEvents(self, dataset_uuid: str) -> int:
        """
        Returns number of rows in pandas DataFrame containing data about EVENTS - for given dataset.

        :param dataset_uuid: String uuid of dataset stored in dictionary of datasets' objects ('FTV_JsonDataManager')
        :return: Integer - number of rows or 0 if no such dataset present.
        """
        if dataset_uuid and self.uuidInListOfDatasets(dataset_uuid):
            return len(self.ftv_datasets[dataset_uuid].events_main.index)
        else:
            return 0

    def returnNoOfTeams(self, dataset_uuid: str) -> int:
        """
        Returns number of rows in pandas DataFrame containing data about LINEUPS - for given dataset.

        :param dataset_uuid: String uuid of dataset stored in dictionary of datasets' objects ('FTV_JsonDataManager')
        :return: Integer - number of rows or 0 if no such dataset present.
        """
        if dataset_uuid and self.uuidInListOfDatasets(dataset_uuid):
            return len(self.ftv_datasets[dataset_uuid].lineups_main.index)
        else:
            return 0
