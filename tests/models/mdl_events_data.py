from app.models import MdlEventsData


EVENTS_JSON_FILEPATH = r'C:\Users\wikto\Rzeczy\Projekty\Python\FootballTacticsViewer\resources\tactics_data\3788757 - events.json'


if __name__ == '__main__':
    mdf = MdlEventsData(j_filepath=EVENTS_JSON_FILEPATH)
    mdf.get_result_frames()