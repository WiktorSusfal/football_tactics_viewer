from app.models import MdlFramesData


FRAMES_JSON_FILEPATH = r'C:\Users\wikto\Rzeczy\Projekty\Python\FootballTacticsViewer\resources\tactics_data\3788757 - frames.json'


if __name__ == '__main__':
    mdf = MdlFramesData(j_filepath=FRAMES_JSON_FILEPATH)
    mdf.get_result_frames()