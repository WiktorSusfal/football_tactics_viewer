import uuid
import pandas as pd
import FTV_JsonData


DEFAULT_NEW_DATASET_NAME = 'default'

class FTV_GUIDataManager:
    """
    Class for managing a set of 'FTV_JsonData.FTV_JsonDataManager' objects - to interact with application GUI.
    'FTV_JsonDataManager' object are stored in a dictionary, where keys are unique uuids.
    """
    def __init__(self):
        # dictionary of complete datasets for visualizing the tactics - objects: 'FTV_JsonData.FTV_JsonDataManager'
        self.ftv_datasets = dict()

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

    def returnEventDetails(self, dataset_uuid: str, frame_no: int) -> pd.DataFrame:
        """
        Returns pandas DataFrame containing EVENTS data for given frame number and given dataset object
        ('FTV_JsonDataManager').

        :param dataset_uuid: String uuid of desired object from dictionary of 'FTV_JsonDataManager' objects.
        :param frame_no: Integer number of desired frame.

        :return: Pandas DataFrame containing EVENTS data.
        """
        # do this only if relevant dataframes has records
        if self.returnNoOfFrames(dataset_uuid) and self.returnNoOfEvents(dataset_uuid):
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
        if self.returnNoOfFrames(dataset_uuid) and self.returnNoOfEvents(dataset_uuid):
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
        if self.returnNoOfTeams(dataset_uuid):
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

