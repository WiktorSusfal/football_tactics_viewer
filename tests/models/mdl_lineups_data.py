from app.models import MdlLineupsData


FRAMES_JSON_FILEPATH = r'C:\Users\wikto\Rzeczy\Projekty\Python\FootballTacticsViewer\resources\tactics_data\3788757 - lineups.json'


if __name__ == '__main__':
    mdf = MdlLineupsData(j_filepath=FRAMES_JSON_FILEPATH)
    mdf.get_result_frames()