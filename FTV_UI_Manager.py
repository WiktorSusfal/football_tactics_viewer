import pandas as pd
import numpy as np
from PyQt5 import QtWidgets as pqt
from PyQt5 import QtCore as qt
from PyQt5 import QtGui as qtg
import FTV_GUIData as ftvgd
import FTV_JsonData as ftvjs

MAIN_WINDOW_HEIGHT = 750
MAIN_WINDOW_WIDTH = 1100

SMALL_BUTTON_WIDTH = 40
SMALL_BUTTON_HEIGHT = 30
BIG_BUTTON_WIDTH = 160
SMALL_LABEL_HEIGHT = 20
SMALL_LABEL_WIDTH = 100
LIST_ITEMS_LABEL_WIDTH = 120

LIST_HEADER_LABEL_WIDTH = 4 * SMALL_BUTTON_WIDTH + LIST_ITEMS_LABEL_WIDTH
LIST_HEADER_INPUT_HEIGHT = 30
LIST_HEADER_INPUT_WIDTH = 4 * SMALL_BUTTON_WIDTH + LIST_ITEMS_LABEL_WIDTH - SMALL_BUTTON_WIDTH + 45
LIST_WIDTH = LIST_HEADER_LABEL_WIDTH + 80
LIST_HEIGHT = 700

RIGHT_PANE_WIDTH = MAIN_WINDOW_WIDTH - LIST_WIDTH
RIGHT_PANE_HEIGHT = LIST_HEIGHT

# in analyzed datasets the size of pitch is normalized to width: 120 and height: 80,
# so the ratio between width and height (which is 1.5) should remain
# following variables are the size of whole pitch image (with borders)
FOOTBALL_PITCH_HEIGHT = 446
FOOTBALL_PITCH_WIDTH = 670
# following variables are the size of borders - distance from the start of image to the borderlines of pitch
PITCH_BORDER_X = 22
PITCH_BORDER_Y = 6
PITCH_BORDER_SIZE = np.array([PITCH_BORDER_X, PITCH_BORDER_Y])
# original ranges of coordinates from datasets
ORG_X_RANGE = (0.0, 120.0)
ORG_Y_RANGE = (0.0, 80.0)

# diameters of ellipse representing player on pitch
PLAYER_SIZE = np.array([22, 22])

DATASET_DETAILS_HEIGHT = 230 + FOOTBALL_PITCH_HEIGHT
DATASET_DETAILS_WIDTH = RIGHT_PANE_WIDTH


# set of static functions used in code below - to return some pre-customized PyQt5 objects
def returnPushButton(text='N/A', tool_tip='', width=SMALL_BUTTON_WIDTH, height=SMALL_BUTTON_HEIGHT):
    push_button = pqt.QPushButton(text)
    push_button.setToolTip(tool_tip)
    push_button.setFixedSize(width, height)

    return push_button


def returnLabel(text='N/A', width=SMALL_LABEL_WIDTH, height=SMALL_LABEL_HEIGHT):
    label = pqt.QLabel()
    label.setText(text)
    label.setFixedSize(width, height)

    return label


def returnQLineEdit(text='N/A', tool_tip='', width=SMALL_LABEL_WIDTH, height=SMALL_LABEL_HEIGHT):
    input_field = pqt.QLineEdit(text)
    input_field.setToolTip(tool_tip)
    input_field.setFixedSize(width, height)

    return input_field


def returnPixmap(png_file_path: str, scaled_width: int = None, scaled_height: int = None) -> qtg.QPixmap:
    pixmap_image = qtg.QPixmap(png_file_path)

    if scaled_width and scaled_height:
        pixmap_image = pixmap_image.scaled(scaled_width, scaled_height, qt.Qt.IgnoreAspectRatio)
    elif scaled_width:
        pixmap_image = pixmap_image.scaledToWidth(scaled_width)
    elif scaled_height:
        pixmap_image = pixmap_image.scaledToHeight(scaled_height)

    return pixmap_image


def returnImageNestedInLabel(png_file_path: str, scaled_width: int = None, scaled_height: int = None) -> pqt.QLabel:
    pixmap_label = pqt.QLabel()
    pixmap_image = returnPixmap(png_file_path, scaled_width, scaled_height)
    pixmap_label.setPixmap(pixmap_image)

    return pixmap_label


# delete all widgets from given layout - to empty the list of datasets (left pane of main window)
def clearLayout(layout):
    if layout.count() > 0:
        while layout.count() > 0:
            item = layout.itemAt(0)
            widget = item.widget()
            layout.removeWidget(widget)


# function to ensure that every game timestamp is represented in form: mm:ss
def parseGameTimestamp(minute: str, second: str):
    minute = str(minute)
    second = str(second)
    if len(minute) < 2:
        for _ in range(2 - len(minute)):
            minute = '0' + minute
    if len(second) < 2:
        for _ in range(2 - len(second)):
            second = '0' + second

    return minute + ' : ' + second


# class for representing graphically one single information in form of: 'information' : 'value'
class InformationRow(pqt.QWidget):
    def __init__(self, r_name, r_value, r_height=SMALL_LABEL_HEIGHT, name_width=SMALL_LABEL_WIDTH,
                 value_width=SMALL_LABEL_WIDTH * 6):
        super().__init__()

        self.main_layout = pqt.QHBoxLayout()
        self.main_layout.setAlignment(qt.Qt.AlignLeft)

        self.row_name = returnLabel(r_name, name_width, r_height)
        self.row_value = returnLabel(': ' + r_value, value_width, r_height)

        self.main_layout.addWidget(self.row_name)
        self.main_layout.addWidget(self.row_value)
        self.main_layout.addStretch()

        self.setLayout(self.main_layout)

    def renameRow(self, r_name):
        self.row_name.setText(r_name)

    def updateValue(self, r_value):
        if not r_value:
            r_value = 'N/A'
        self.row_value.setText(': ' + r_value)
        self.row_value.setToolTip(r_value)


# class for representing single custom element of an editable list
class DataSetListElement(pqt.QWidget):

    def __init__(self, uuid, name):
        super().__init__()
        self.main_layout = pqt.QHBoxLayout()
        self.setLayout(self.main_layout)

        self.dataset_uuid = uuid
        self.dataset_name = name

        self.choose_chcbx = pqt.QCheckBox()
        self.choose_chcbx.setToolTip('Check current dataset to analyze')

        # return QLabels with given text and size
        # default size determined by: SMALL_LABEL_WIDTH, SMALL_LABEL_HEIGHT
        self.name_label = returnLabel(self.dataset_name, LIST_ITEMS_LABEL_WIDTH)

        # return QPushButtons with given text and tooltip
        # default size determined by: SMALL_BUTTON_WIDTH, SMALL_BUTTON_HEIGHT
        self.l_fpath_btn = returnPushButton('P_L', 'Choose path for lineups json file')
        self.e_fpath_btn = returnPushButton('P_E', 'Choose path for events json file')
        self.f_fpath_btn = returnPushButton('P_F', 'Choose path for frames json file')
        self.d_btn = returnPushButton('X', 'Delete dataset')

        self.main_layout.addWidget(self.choose_chcbx)
        self.main_layout.addWidget(self.name_label)
        self.main_layout.addWidget(self.l_fpath_btn)
        self.main_layout.addWidget(self.e_fpath_btn)
        self.main_layout.addWidget(self.f_fpath_btn)
        self.main_layout.addWidget(self.d_btn)


# class representing editable list for storing 'DataSetListElement' objects
class DataSetList(pqt.QWidget):

    def __init__(self, gui_data_manager: ftvgd.FTV_GUIDataManager):
        super().__init__()
        # variable for counting dataset added from the beginning of application launch
        self.no_of_datasets_added = 0
        # list of DataSetListElement objects
        self.list_elements = dict()
        # reference to FTV.GUIDaa.FTV_GUIDataManager object
        self.gdm = gui_data_manager
        # current item's uuid
        self.curr_item_uuid = str()

        # variables to represent GUI objects:
        self.main_layout = pqt.QVBoxLayout()
        self.main_layout.setAlignment(qt.Qt.AlignTop)
        self.list_items_layout = pqt.QVBoxLayout()
        self.list_items_layout.setAlignment(qt.Qt.AlignTop)
        self.setFixedSize(LIST_WIDTH, LIST_HEIGHT)

        self.add_dataset_form = pqt.QVBoxLayout()
        self.add_dataset_subform = pqt.QHBoxLayout()

        self.add_dataset_label = returnLabel('Add new dataset', LIST_HEADER_LABEL_WIDTH)
        self.add_dataset_input_field = returnQLineEdit('', 'Enter friendly name of new Dataset and press "Add"',
                                                       LIST_HEADER_INPUT_WIDTH, LIST_HEADER_INPUT_HEIGHT)

        self.add_dataset_btn = returnPushButton('Add', 'Enter friendly name of new Dataset and press "Add"')
        self.add_dataset_btn.clicked.connect(self.addListElement)

        self.add_dataset_subform.addWidget(self.add_dataset_input_field)
        self.add_dataset_subform.addWidget(self.add_dataset_btn)

        self.add_dataset_form.addWidget(self.add_dataset_label)
        self.add_dataset_form.addLayout(self.add_dataset_subform)

        self.main_layout.addLayout(self.add_dataset_form)
        self.main_layout.addLayout(self.list_items_layout)
        self.main_layout.addStretch()
        self.setLayout(self.main_layout)

        # update variable list elements
        self.updateGUIList()

    def updateGUIList(self):
        clearLayout(self.list_items_layout)

        self.add_dataset_input_field.setText('default_dataset_' + str(self.no_of_datasets_added))

        for key, element in self.list_elements.items():
            self.list_items_layout.addWidget(element)

        self.list_items_layout.addStretch()

    # update the variable that stores uuid of current list item choosen
    def updateCurrentUUID(self):
        curr_uuid_to_change = self.findListElementByButtonUsed(self.sender(), 'choose_chcbx')

        # When setting new list item as selected, clear the previous selection
        if self.curr_item_uuid and curr_uuid_to_change != self.curr_item_uuid:
            self.list_elements[self.curr_item_uuid].choose_chcbx.setChecked(0)

        # Update current uuid of selected item only if it was checked. If it was simply unchecked, clear the selection
        if self.list_elements[curr_uuid_to_change].choose_chcbx.isChecked():
            self.curr_item_uuid = curr_uuid_to_change
        else:
            self.curr_item_uuid = str()

    def addListElement(self):
        self.no_of_datasets_added += 1

        new_dataset_name = self.add_dataset_input_field.text()
        new_uuid = self.gdm.add_new_ftv_dataset(new_dataset_name)

        self.list_elements[new_uuid] = DataSetListElement(new_uuid, new_dataset_name)
        self.list_elements[new_uuid].choose_chcbx.clicked.connect(self.updateCurrentUUID)
        self.list_elements[new_uuid].d_btn.clicked.connect(self.removeListElement)
        self.list_elements[new_uuid].e_fpath_btn.clicked.connect(self.assignEventsFilePath)
        self.list_elements[new_uuid].f_fpath_btn.clicked.connect(self.assignFramesFilePath)
        self.list_elements[new_uuid].l_fpath_btn.clicked.connect(self.assignLineupsFilePath)
        self.updateGUIList()

    # every list item has a set of buttons. buttons are assigned to function located here (in class 'DataSetList')
    # to perform relevant action there is a need to know which list item a button was pressed in. this function
    # searches all list items and checks if the 'sender' object (which is the button pressed) exists in a particular
    # list item ('DataSetListElement' object). If yes, it returns the uuid of the whole item
    # function gets also the attribute name 'attr_name' of 'DataSetListElement' attribute which the sender object
    # needs to be compared with
    def findListElementByButtonUsed(self, button, attr_name):
        uuid_of_element = str()
        for uuid, list_element in self.list_elements.items():
            if button is getattr(list_element, attr_name):
                uuid_of_element = list_element.dataset_uuid
                break

        return uuid_of_element

    def removeListElement(self):
        uuid_to_delete = self.findListElementByButtonUsed(self.sender(), 'd_btn')

        if not uuid_to_delete:
            raise Exception('Tried to delete element form GUI list that does not exists')
        else:
            # When removing element that was already selected, clear the selection first
            if self.list_elements[uuid_to_delete].choose_chcbx.isChecked():
                self.curr_item_uuid = str()
            self.list_elements.pop(uuid_to_delete)

        self.gdm.delete_ftv_dataset(uuid_to_delete)
        self.updateGUIList()

    def assignFramesFilePath(self):
        filepath, check = pqt.QFileDialog.getOpenFileName(None,
                                                          'Football Tactics Viewer - choose path to json FRAMES data',
                                                          '', "Json Files (*.json)")
        if check:
            uuid_to_update = self.findListElementByButtonUsed(self.sender(), 'f_fpath_btn')
            self.gdm.ftv_datasets[uuid_to_update].assignFilePaths(ftvjs.FTV_DataReadModes.FRAMES.value, filepath)

    def assignEventsFilePath(self):
        filepath, check = pqt.QFileDialog.getOpenFileName(None,
                                                          'Football Tactics Viewer - choose path to json EVENTS data',
                                                          '', "Json Files (*.json)")
        if check:
            uuid_to_update = self.findListElementByButtonUsed(self.sender(), 'e_fpath_btn')
            self.gdm.ftv_datasets[uuid_to_update].assignFilePaths(ftvjs.FTV_DataReadModes.EVENTS.value, filepath)

    def assignLineupsFilePath(self):
        filepath, check = pqt.QFileDialog.getOpenFileName(None,
                                                          'Football Tactics Viewer - choose path to json LINEUPS data',
                                                          '', "Json Files (*.json)")
        if check:
            uuid_to_update = self.findListElementByButtonUsed(self.sender(), 'l_fpath_btn')
            self.gdm.ftv_datasets[uuid_to_update].assignFilePaths(ftvjs.FTV_DataReadModes.LINEUPS.value, filepath)


# class for football pitch visualization
class PitchView(pqt.QWidget):
    def __init__(self):
        super().__init__()
        # define ranges (in pixels) of exact pitch rectangle (excluding borders on the pitch image)
        self.pitch_x_range = (float(PITCH_BORDER_X), float(FOOTBALL_PITCH_WIDTH - PITCH_BORDER_X))
        self.pitch_y_range = (float(PITCH_BORDER_Y), float(FOOTBALL_PITCH_HEIGHT - PITCH_BORDER_Y))

        # define color sets for icons representing players on pitch; main keys are integer indexes of teams from the
        # 'FTV_JsonData.FTV_JsonDataManager.lineups_main' pandas dataframe
        self.icon_colors = {
            0: {'keeper': qtg.QColor(255, 165, 0), 'player': qtg.QColor(255, 0, 0)},
            1: {'keeper': qtg.QColor(255, 165, 0), 'player': qtg.QColor(0, 0, 255)}
        }

        self.setFixedSize(FOOTBALL_PITCH_WIDTH, FOOTBALL_PITCH_HEIGHT)

        self.pitch_pixmap = returnPixmap("Resources/TestFootballField.png",
                                         scaled_height=FOOTBALL_PITCH_HEIGHT, scaled_width=FOOTBALL_PITCH_WIDTH
                                         )

        self.first_team_player = returnPixmap("Resources/first_team_player.png")
        self.first_team_keeper = returnPixmap("Resources/first_team_keeper.png")
        self.second_team_player = returnPixmap("Resources/second_team_player.png")
        self.second_team_keeper = returnPixmap("Resources/second_team_keeper.png")

    def paintEvent(self, event):
        painter = qtg.QPainter(self)
        painter.drawPixmap(self.rect(), self.pitch_pixmap)

    def updatePitchPlayers(self, frames_players: pd.DataFrame, events_details: pd.DataFrame,
                           teams_details: pd.DataFrame):

        # painter to draw pixmap itself:
        main_painter = qtg.QPainter(self)
        # reset the pitch view before drawing
        self.pitch_pixmap = returnPixmap("Resources/TestFootballField.png",
                                         scaled_height=FOOTBALL_PITCH_HEIGHT, scaled_width=FOOTBALL_PITCH_WIDTH
                                         )
        main_painter.drawPixmap(self.rect(), self.pitch_pixmap)

        if any(frames_players) and any(events_details) and any(teams_details):
            # get IDs of the first and the second team (first is a team in 0 row of 'lineups_details' dataframe)
            # first team has assigned red color for players, the second team - blue
            f_team_id = int(teams_details.loc[0][ftvjs.FTV_LineupsJsonAttrNames.TEAM_ID.value])
            s_team_id = int(teams_details.loc[1][ftvjs.FTV_LineupsJsonAttrNames.TEAM_ID.value])
            # get ID of team that is related to current event and the number of period of game
            e_team_id = int(list(events_details['event_team_id'])[0])
            period_no = int(list(events_details[ftvjs.FTV_EventsJsonAttrNames.PERIOD.value])[0])
            # below variable indicates, which (first or second?) team is the team related to the current event
            event_team_idx = 0 if f_team_id == e_team_id else 1

            # painter to draw on pixmap
            pixmap_painter = qtg.QPainter(self.pitch_pixmap)

            for idx, row in frames_players.iterrows():
                # calculate coordinates in pitch's coordinate system
                original_coordinates = np.array([row['loc_x'], row['loc_y']])
                pitch_coordinates = np.array([
                    self.returnXCoordinate(original_coordinates[0], event_team_idx, period_no),
                    self.returnYCoordinate(original_coordinates[1])
                ])
                # calculate coordinates in pixmap's coordinate system - ready to draw an object
                pixmap_coordinates = self.returnPixmapCoordinates(pitch_coordinates)

                # check if current player is a teammate of team related to current event an if he is a keeper
                is_teammate = row['teammate']
                is_keeper = row['keeper']

                # choose proper color and paint next player
                icon_color = self.returnIconColor(event_team_idx, is_teammate, is_keeper)
                pixmap_painter.setBrush(qtg.QBrush(icon_color))
                pixmap_painter.drawEllipse(pixmap_coordinates)

                self.update()

        self.update()

    # return coordinates in pitch's dataframe based on original data
    def returnXCoordinate(self, org_x: float, event_team_idx: int, period_no: id) -> int:
        # projection of the coordinates - from original range (form json data) to destination (pitch view)
        dest_x = int((org_x - ORG_X_RANGE[0]) / (ORG_X_RANGE[1] - ORG_X_RANGE[0]) \
                     * (self.pitch_x_range[1] - self.pitch_x_range[0]) + self.pitch_x_range[0])

        # if first team (with index 0) is related to event and period of game is odd, then coordinates stays the same.
        # otherwise, they need to be reversed to display the players properly
        if (event_team_idx == 0 and period_no % 2 == 0) or (event_team_idx == 1 and period_no % 2 == 1):
            # mirror the coordinate
            dest_x = self.pitch_x_range[1] - (dest_x - self.pitch_x_range[0])

        return dest_x

    # return coordinates in pitch's coordinates frame based on original data
    def returnYCoordinate(self, org_y: float) -> int:
        # projection of the coordinates - from original range (form json data) to destination (pitch view)
        dest_y = int((org_y - ORG_Y_RANGE[0]) / (ORG_Y_RANGE[1] - ORG_Y_RANGE[0]) \
                     * (self.pitch_y_range[1] - self.pitch_y_range[0]) + self.pitch_y_range[0])

        # mirror the coordinate - pitch on GUI has reversed direction of the Y-axis
        dest_y = int(self.pitch_y_range[1] - (dest_y - self.pitch_y_range[0]))

        return dest_y

    # return coordinates in pitch pixmap's coordinates frame in form readable by QPainter object (as a QRect object).
    # consider spaces around exact pitch field and the way that the ellipse is being drawn -
    # there is a need to specify top-left point of a rectangle and its width and height.
    # ellipse is then filling the rectangle specified
    def returnPixmapCoordinates(self, pitch_coordinates: np.array) -> qt.QRect:
        # add border sizes to the exact pitch coordinates
        pixmap_coordinates = pitch_coordinates + PITCH_BORDER_SIZE
        # calculate the rectangle's top-left corner coordinates
        pixmap_coordinates -= PLAYER_SIZE

        top_left_corner = qt.QPoint(int(pixmap_coordinates[0]), int(pixmap_coordinates[1]))
        size = qt.QSize(int(PLAYER_SIZE[0]), int(PLAYER_SIZE[1]))

        return qt.QRect(top_left_corner, size)

    # return QColor object to draw specific player icon on pitch
    def returnIconColor(self, event_team_idx: int, is_teammate: bool, is_keeper: bool) -> qtg.QColor:
        player_team_idx = event_team_idx if is_teammate else int(bool(event_team_idx - 1))
        player_type = 'keeper' if is_keeper else 'player'

        return self.icon_colors[player_team_idx][player_type]


# class for representing json dataset details
class DatasetGUIDetails(pqt.QWidget):
    def __init__(self, gui_dm: ftvgd.FTV_GUIDataManager):
        super().__init__()
        # object responsible for football pitch visualization
        self.pitch_view = PitchView()
        # local reference to FTV_GUIData.FTV_GUIDataManager object
        self.gui_data_manager = gui_dm
        # current dataset uuid, which details are being visualized from
        self.current_dataset_uuid = str()
        # pandas dataframe regarding current lineups data
        self.teams_details = pd.DataFrame()
        # pandas dataframe regarding current events data
        self.event_details = pd.DataFrame()

        self.setFixedSize(DATASET_DETAILS_WIDTH, DATASET_DETAILS_HEIGHT)
        self.main_layout = pqt.QVBoxLayout()
        self.main_layout.setAlignment(qt.Qt.AlignTop)

        # define horizontal layouts for pitch legend and frame control panel
        self.pitch_legend_layout = pqt.QHBoxLayout()
        self.pitch_legend_layout.setAlignment(qt.Qt.AlignLeft)
        self.frame_control_layout = pqt.QHBoxLayout()
        self.frame_control_layout.setAlignment(qt.Qt.AlignLeft)

        # add gui items for football pitch legend visualization
        self.first_team_legend_rect = returnImageNestedInLabel('Resources/red_rect.png')
        self.second_team_legend_rect = returnImageNestedInLabel('Resources/blue_rect.png')
        self.first_team_legend_label = returnLabel('None')
        self.second_team_legend_label = returnLabel('None')
        # build pitch legend layout
        self.pitch_legend_layout.addWidget(self.first_team_legend_rect)
        self.pitch_legend_layout.addWidget(self.first_team_legend_label)
        self.pitch_legend_layout.addWidget(self.second_team_legend_rect)
        self.pitch_legend_layout.addWidget(self.second_team_legend_label)
        self.pitch_legend_layout.addStretch()

        # add gui items for football control frames visualization
        self.previous_btn = returnPushButton('<', 'Get previous frame')
        self.previous_btn.clicked.connect(self.getPrevEventDetails)
        self.next_btn = returnPushButton('>', 'Get next frame')
        self.next_btn.clicked.connect(self.getNextEventDetails)
        self.go_to_frame_btn = returnPushButton('GO', 'Go to specified frame')
        self.go_to_frame_btn.clicked.connect(self.getGivenEventDetails)
        self.timestamp_name_label = returnLabel('Timestamp: ', int(SMALL_LABEL_WIDTH / 1.2))
        self.timestamp_value = returnLabel('N/A', int(SMALL_LABEL_WIDTH / 1.2))
        self.no_of_frames = returnLabel(str(0), int(SMALL_LABEL_WIDTH / 2))
        self.division_label = returnLabel('/', int(SMALL_LABEL_WIDTH / 6))
        self.current_frame_with_input = returnQLineEdit(str(0), 'You can enter desired frame number and press "GO"',
                                                        int(SMALL_LABEL_WIDTH / 2))
        # build frame control panel layout
        self.frame_control_layout.addWidget(self.previous_btn)
        self.frame_control_layout.addWidget(self.timestamp_name_label)
        self.frame_control_layout.addWidget(self.timestamp_value)
        self.frame_control_layout.addWidget(self.next_btn)
        self.frame_control_layout.addSpacerItem(pqt.QSpacerItem(20, 20, pqt.QSizePolicy.Fixed))
        self.frame_control_layout.addWidget(self.current_frame_with_input)
        self.frame_control_layout.addWidget(self.division_label)
        self.frame_control_layout.addWidget(self.no_of_frames)
        self.frame_control_layout.addWidget(self.go_to_frame_btn)
        self.frame_control_layout.addStretch()

        # the rest of details in form of 'detail name' : 'detail value'
        self.l_fpath_info = InformationRow('Lineups json path', 'N/A')
        self.e_fpath_info = InformationRow('Events json path', 'N/A')
        self.f_fpath_info = InformationRow('Frames json path', 'N/A')

        # merge all parts of main layout
        self.main_layout.addWidget(self.pitch_view)
        self.main_layout.addLayout(self.pitch_legend_layout)
        self.main_layout.addLayout(self.frame_control_layout)
        self.main_layout.addWidget(self.l_fpath_info)
        self.main_layout.addWidget(self.e_fpath_info)
        self.main_layout.addWidget(self.f_fpath_info)
        self.main_layout.addStretch()
        self.setLayout(self.main_layout)

    # updates all gui data
    def updateGUIData(self, dataset_uuid: str):
        self.current_dataset_uuid = dataset_uuid
        self.updateInformationRows()
        self.updateEventDetails(dict())
        self.updatePitchLegendDetails()
        self.updatePitchView(dict())

    # update values of all relevant 'InfromationRow' objects present on this class' attributes list
    # get the dictionary of data, where keys are 'InformationRow' attributes' names and values are values for
    # these attributes to set
    def updateInformationRows(self):
        dataset_uuid = self.current_dataset_uuid
        if not dataset_uuid:
            l_fpath, e_fpath, f_fpath = 'N/A', 'N/A', 'N/A'
        else:
            l_fpath = self.gui_data_manager.ftv_datasets[dataset_uuid].lineups_filepath
            e_fpath = self.gui_data_manager.ftv_datasets[dataset_uuid].events_filepath
            f_fpath = self.gui_data_manager.ftv_datasets[dataset_uuid].frames_filepath

        for name, value in {'l_fpath_info': l_fpath, 'e_fpath_info': e_fpath, 'f_fpath_info': f_fpath}.items():
            getattr(self, name).updateValue(value)

    def getNextEventDetails(self):
        if self.current_dataset_uuid:
            curr_frame_no = int(self.current_frame_with_input.text())
            no_of_frames = int(self.no_of_frames.text())

            if curr_frame_no < no_of_frames:
                event_details_dict = self.getEventDetails(curr_frame_no)
                self.updateEventDetails(event_details_dict)
                self.updatePitchView(event_details_dict)

    def getPrevEventDetails(self):
        if self.current_dataset_uuid:
            curr_frame_no = int(self.current_frame_with_input.text())

            if curr_frame_no > 1:
                curr_frame_no -= 1
                event_details_dict = self.getEventDetails(curr_frame_no - 1)
                self.updateEventDetails(event_details_dict)
                self.updatePitchView(event_details_dict)

    def getGivenEventDetails(self):
        if self.current_dataset_uuid:
            curr_frame_no = int(self.current_frame_with_input.text())
            no_of_frames = int(self.no_of_frames.text())

            if not (0 < curr_frame_no <= no_of_frames):
                curr_frame_no = 1

            # users specify no of frame starting from 1, but in pandas dataframe it starts from 0
            event_details_dict = self.getEventDetails(curr_frame_no - 1)
            self.updateEventDetails(event_details_dict)
            self.updatePitchView(event_details_dict)
        else:
            self.updateEventDetails(dict())
            self.updatePitchView(dict())

    # returns dictionary: {'curr_frame_no': frame_no, 'no_of_frames': int, 'event_details': pandas.DataFrame)
    # 'curr_frame_no' is an integer describing number of current frame from dataset
    # 'no_of_frames' is an integer describing number of data frames available for given dataset
    # 'event_details' is a one-row DataFrame with columns as for 'FTV_JsonData.FTV_JsonDataManager.events_main'
    def getEventDetails(self, frame_no=None):
        # if 'frame_no' not specified, return details about current event and frame
        if not (frame_no is None):
            # following expression returns one-row dataframe which describes current event with all columns stored
            # in 'FTV_JsonData.FTV_JsonDataManager.events_main' dataframe. go to mentioned .py module to see description
            self.event_details = self.gui_data_manager.returnEventDetails(self.current_dataset_uuid, frame_no)
            # later there is a need to return user-friendly 'frame_no' (starting from 1). Above function accepts
            # frame numbers starting from 0
            frame_no += 1
        else:
            frame_no = int(self.current_frame_with_input.text())

        if any(self.event_details):
            no_of_frames = self.gui_data_manager.returnNoOfFrames(self.current_dataset_uuid)
            return {'curr_frame_no': frame_no, 'no_of_frames': no_of_frames, 'event_details': self.event_details}
        else:
            return dict()

    def updateEventDetails(self, event_details_dict):
        # if current dataset uuid stored in this class no longer exists in list of datasets,
        # reinitialize it to empty string
        if not self.gui_data_manager.uuidInListOfDatasets(self.current_dataset_uuid):
            self.current_dataset_uuid = str()

        # if existing dict of values passed - update GUI based on it
        if any(event_details_dict):
            self.current_frame_with_input.setText(str(int(event_details_dict['curr_frame_no'])))
            self.no_of_frames.setText(str(event_details_dict['no_of_frames']))
            # get the minute of math from dataframe column
            minute_of_game = list(event_details_dict['event_details'][ftvjs.FTV_EventsJsonAttrNames.MINUTE.value])[0]
            second_of_game = list(event_details_dict['event_details'][ftvjs.FTV_EventsJsonAttrNames.SECOND.value])[0]
            game_timestamp = parseGameTimestamp(minute_of_game, second_of_game)
            self.timestamp_value.setText(game_timestamp)
        else:
            # get number of rows in relevant dataset's dataframes
            frames_rows = self.gui_data_manager.returnNoOfFrames(self.current_dataset_uuid)
            events_rows = self.gui_data_manager.returnNoOfEvents(self.current_dataset_uuid)
            # if no dict of values passed, but current dataset uuid exists and relevant dataset's dataframes
            # are not empty, view first frame of dataset
            if self.current_dataset_uuid and frames_rows and events_rows:
                first_event_details_dict = self.getEventDetails(0)
                self.updateEventDetails(first_event_details_dict)
            # else - zero the values of this GUI
            else:
                self.current_frame_with_input.setText('0')
                self.no_of_frames.setText(str(0))
                self.timestamp_value.setText('N/A')

    def updatePitchLegendDetails(self):
        self.teams_details = self.gui_data_manager.returnTeamsDetails(self.current_dataset_uuid)

        if any(self.teams_details):
            first_team = self.teams_details.loc[0][ftvjs.FTV_LineupsJsonAttrNames.TEAM_NAME.value]
            second_team = self.teams_details.loc[1][ftvjs.FTV_LineupsJsonAttrNames.TEAM_NAME.value]
            self.updateTeamNames(first_team, second_team)
        else:
            self.updateTeamNames('None', 'None')

    def updateTeamNames(self, first_name: str, second_name: str):
        self.first_team_legend_label.setText(first_name)
        self.second_team_legend_label.setText(second_name)

    def updatePitchView(self, event_details_dict: dict):
        frame_no = event_details_dict['curr_frame_no'] - 1 if any(event_details_dict) else 0

        players_in_frame = self.gui_data_manager.returnPlayersLocationsInFrame(self.current_dataset_uuid, frame_no)
        self.pitch_view.updatePitchPlayers(players_in_frame, self.event_details, self.teams_details)


# application main window class
class MainWindow(pqt.QMainWindow):
    def __init__(self):
        super().__init__()
        # Initialize FTV_GUIDataManager object for main window
        self.g_data_manager = ftvgd.FTV_GUIDataManager()
        # Initialize DataSetList object for main window
        self.dataset_gui_list = DataSetList(self.g_data_manager)
        # Initialize DatasetGUIDetails object responsible for dataset details visualization
        self.dataset_gui_details = DatasetGUIDetails(self.g_data_manager)

        self.setWindowTitle('Football Tactics Viewer')
        self.central_widget = pqt.QWidget()
        self.setCentralWidget(self.central_widget)
        self.setFixedSize(MAIN_WINDOW_WIDTH, MAIN_WINDOW_HEIGHT)

        # Divide main window into 2 parts (two vertical panels)
        self.left_panel = pqt.QWidget()
        self.right_panel = pqt.QWidget()

        self.lay = pqt.QGridLayout(self.central_widget)

        for panel, (row, column) in zip(
                (self.left_panel, self.right_panel),
                ((0, 0), (0, 1)),
        ):
            self.lay.addWidget(panel, row, column)
        for column in range(2):
            self.lay.setColumnStretch(column, 1)

        # Add all elements to the left panel. In this case this is 'DataSetList' object
        self.lay = pqt.QVBoxLayout(self.left_panel)
        self.lay.addWidget(self.dataset_gui_list)

        # Create high-level objects for right panel
        self.refresh_data_btn = returnPushButton('Refresh Data', 'Refresh data on screen', BIG_BUTTON_WIDTH)
        self.refresh_data_btn.clicked.connect(self.refreshData)
        self.recalc_data_btn = returnPushButton('Recalculate Data', 'Recalculate data from selected dataset',
                                                BIG_BUTTON_WIDTH)
        self.recalc_data_btn.clicked.connect(self.recalculateData)

        self.right_panel_options = pqt.QHBoxLayout()
        self.right_panel_options.setAlignment(qt.Qt.AlignLeft)
        self.right_panel_options.addWidget(self.refresh_data_btn)
        self.right_panel_options.addWidget(self.recalc_data_btn)
        self.right_panel_options.addStretch()

        # Add high-level objects to the right panel
        self.lay = pqt.QVBoxLayout(self.right_panel)
        self.lay.setAlignment(qt.Qt.AlignTop)
        self.lay.addLayout(self.right_panel_options)
        self.lay.addWidget(self.dataset_gui_details)
        self.lay.addStretch()

        self.show()

    def recalculateData(self):
        curr_dataset_uuid = self.dataset_gui_list.curr_item_uuid
        if not curr_dataset_uuid:
            return

        # read new json data for selected dataset
        for modes in ftvjs.FTV_DataReadModes:
            self.g_data_manager.ftv_datasets[curr_dataset_uuid].readJsonData(modes.value)

        self.g_data_manager.ftv_datasets[curr_dataset_uuid].normalizeJsonData()

    def refreshData(self):
        # get the current string id of dataset selected on the list (left pane of the main window)
        curr_dataset_uuid = self.dataset_gui_list.curr_item_uuid
        # invoke method from 'dataset_gui_details' object (right pane of the window - with details) to refresh the data
        self.dataset_gui_details.updateGUIData(curr_dataset_uuid)