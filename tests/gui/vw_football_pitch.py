import os
import pandas as pd

from app.views import VwFootballPitch
from tests.gui._base import visual_test_preview


PKL_FRAMES_BASE     = r'.\resources\generated\dataframes'
PKL_TEST_DATA       = 'players_pitch_data_frame_0_example.pkl'


if __name__ == '__main__':
    view = VwFootballPitch()
    view.setStyleSheet("background-color: #2f3b52;")

    test_data: pd.DataFrame = pd.read_pickle(os.path.join(PKL_FRAMES_BASE, PKL_TEST_DATA))
    print(test_data)
    view._update_view(test_data)

    visual_test_preview(view)