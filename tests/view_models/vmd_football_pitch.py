import os
import pandas as pd 
from app.view_models import VmdFootballPitch

PKL_FRAMES_BASE     = r'.\resources\generated\dataframes'
PKL_MAIN_FRAME      = 'main_frame_0_example.pkl'
PKL_PLAYERS_FRAME   = 'players_frame_0_example.pkl'
PKL_VAREA_FRAME     = 'visible_area_frame_0_example.pkl'
PKL_LINEUPS_FRAME   = 'lineups_frame_0_example.pkl'
PKL_EVENTS_FRAME    = 'events_frame_0_example.pkl'


if __name__ == '__main__':
    main_frame: pd.DataFrame            = pd.read_pickle(os.path.join(PKL_FRAMES_BASE, PKL_MAIN_FRAME))
    players_frame: pd.DataFrame         = pd.read_pickle(os.path.join(PKL_FRAMES_BASE, PKL_PLAYERS_FRAME))
    visible_area_frame: pd.DataFrame    = pd.read_pickle(os.path.join(PKL_FRAMES_BASE, PKL_VAREA_FRAME))
    lineups_frame: pd.DataFrame         = pd.read_pickle(os.path.join(PKL_FRAMES_BASE, PKL_LINEUPS_FRAME))
    events_frame: pd.DataFrame          = pd.read_pickle(os.path.join(PKL_FRAMES_BASE, PKL_EVENTS_FRAME))
    
    vfp = VmdFootballPitch()
    vfp.get_data(players_frame, events_frame, lineups_frame)

    print(vfp._last_data)