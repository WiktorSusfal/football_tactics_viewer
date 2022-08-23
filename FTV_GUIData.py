import uuid
import pandas as pd
import FTV_JsonData


# class for managing a set of 'FTV_JsonData.FTV_JsonDataManager' objects - to interact with application GUI
class FTV_GUIDataManager:
    def __init__(self):
        # dictionary of complete datasets for visualizing the tactics - objects: 'FTV_JsonData.FTV_JsonDataManager'
        self.ftv_datasets = dict()

    def add_new_ftv_dataset(self, dataset_name='default') -> str:
        new_uuid = str(uuid.uuid4())
        self.ftv_datasets[new_uuid] = FTV_JsonData.FTV_JsonDataManager(dataset_name)

        return new_uuid

    def delete_ftv_dataset(self, dataset_uuid: str):
        if dataset_uuid in list(self.ftv_datasets.keys()):
            self.ftv_datasets.pop(dataset_uuid)
        else:
            raise Exception('Tried to delete dataset that not exists')

    def uuidInListOfDatasets(self, ds_uuid: str) -> bool:
        return ds_uuid in self.ftv_datasets

    def specify_paths_to_json_files(self, dataset_uuid: str):
        self.ftv_datasets[dataset_uuid].assignFilePaths()

    def returnEventDetails(self, dataset_uuid: str, frame_no: int) -> pd.DataFrame:
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
        # do this only if relevant dataframes has records
        if self.returnNoOfFrames(dataset_uuid) and self.returnNoOfEvents(dataset_uuid):
            ds = self.ftv_datasets[dataset_uuid]
            curr_players_locations = ds.frames_players.loc[ds.frames_players.main_event_idx == frame_no]

            return curr_players_locations
        else:
            return pd.DataFrame()

    def returnTeamsDetails(self, dataset_uuid: str) -> pd.DataFrame:
        # do this only if relevant dataframes has records
        if self.returnNoOfTeams(dataset_uuid):
            ds = self.ftv_datasets[dataset_uuid]
            return ds.lineups_main
        else:
            return pd.DataFrame()

    def returnNoOfFrames(self, dataset_uuid: str) -> int:
        if dataset_uuid and self.uuidInListOfDatasets(dataset_uuid):
            return len(self.ftv_datasets[dataset_uuid].frames_main.index)
        else:
            return 0

    def returnNoOfEvents(self, dataset_uuid: str) -> int:
        if dataset_uuid and self.uuidInListOfDatasets(dataset_uuid):
            return len(self.ftv_datasets[dataset_uuid].events_main.index)
        else:
            return 0

    def returnNoOfTeams(self, dataset_uuid: str) -> int:
        if dataset_uuid and self.uuidInListOfDatasets(dataset_uuid):
            return len(self.ftv_datasets[dataset_uuid].lineups_main.index)
        else:
            return 0

