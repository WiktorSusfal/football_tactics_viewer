import json
import pandas as pd
from typing   import Any
from abc      import ABC, abstractmethod
from io       import StringIO


class MdlJsonModelBase(ABC):

    def __init__(self, j_filepath: str = None):
        super(MdlJsonModelBase, self).__init__()

        self._j_filepath: str = j_filepath or None

    def set_json_filepath(self, j_filepath: str):
        self._j_filepath = j_filepath
        self.reset_result_frames()

    def _read_json_data(self) -> Any:
        """
        Returns structured json data read from file - in form of dictionary or list of dictionaries

        :param filepath: String filepath of the file containing source data.
        :return: Structured json data read from file - in form of dictionary or list of dictionaries.
        """
        if not self._j_filepath:
            raise Exception(f'{self.__class__.__name__}: JSON filepath not set!')

        with open(self._j_filepath) as json_file:
            json_data = json.load(json_file)

        return json_data
    
    def _parse_json_table(self, j_objects: Any) -> pd.DataFrame:
        """
        Parses structured json data to pandas DataFrame. Accepts list of dictionaries (json structured data objects) or
        single dictionary.

        :param j_objects: List of dictionaries (json structured data objects) or single dictionary.
        :return: Pandas DataFrame
        """
        if not isinstance(j_objects, list):
            j_objects = [j_objects]

        for j_object in j_objects:
            if not isinstance(j_object, dict):
                raise ValueError('Invalid content of json data provided. Expected list of dictionaries (json objects)')

        raw_df = pd.read_json(StringIO(json.dumps(j_objects)), orient='records')
        raw_df.index += 1 

        return raw_df
    
    def _get_raw_data_frame(self) -> pd.DataFrame:
        raw_json_obj = self._read_json_data()
        return self._parse_json_table(raw_json_obj)
    
    @abstractmethod
    def get_result_frames(self):
        pass

    @abstractmethod
    def reset_result_frames(self):
        pass