import pandas as pd
import numpy as np

import FTV_GUIData as ftvgd
import FTV_JsonData as ftvjs

import sys

sys.path.append('./Resources/Lib')

from Resources.Lib import DLW_GUIList as GLI
from Resources.Lib import PyQT5_GUI_Builder as GBU
from Resources.Lib import ObservableObjects as OOBJ

from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qt
from PyQt5 import QtGui as qtg

from varname import *

GUI_MAIN_CNFG_FILEPATH = 'Resources/Settings/gui_cnfg_main.xml'
ADD_DATASET_FORM_LAYOUT_NAME = 'add_dataset_form'
NEW_DATASET_NAME_INPUT_FIELD = 'add_dataset_line_edit'
DATASET_LAYOUT_NAME = 'dataset_gui_list_element'
SET_FRAMES_FILEPATH_BUTTON_NAME = 'P_F'
SET_EVENTS_FILEPATH_BUTTON_NAME = 'P_E'
SET_LINEUPS_FILEPATH_BUTTON_NAME = 'P_L'
NEW_DATASET_DEFAULT_NAME_PREFIX = 'default_dataset_'

FILTER_JSON_DATA_FILES = 'Json Files (*.json)'

LIST_WIDTH = 360
LIST_HEIGHT = 700

# In analyzed datasets the size of pitch is normalized to width: 120 and height: 80, so the ratio between
# width and height (which is 1.5) should remain.
# Following variables are the size of whole pitch image (with borders).
FOOTBALL_PITCH_HEIGHT = 446
FOOTBALL_PITCH_WIDTH = 670
# Following variables are the size of borders - distance from the start of image to the borderlines of the pitch.
PITCH_BORDER_X = 22
PITCH_BORDER_Y = 6
PITCH_BORDER_SIZE = np.array([PITCH_BORDER_X, PITCH_BORDER_Y])
# Original ranges of coordinates from datasets.
ORG_X_RANGE = (0.0, 120.0)
ORG_Y_RANGE = (0.0, 80.0)
# Diameters of ellipse representing player on pitch.
PLAYER_SIZE = np.array([22, 22])


class DataSetList(qtw.QWidget, OOBJ.ObserverObject):
    """
    Class representing dynamic list of datasets which the data is visualized from.
    It inherits from 'ObserverObject' class to ensure automatic and event-driven data exchange between GUI objects
    and backed variables. Read more on https://github.com/WiktorSusfal/python_observable_objects
    It uses the 'DLW_List' class instance to simulate a dynamic list of widgets - read more on
    https://github.com/WiktorSusfal/dynamic_list_of_widgets_pyqt5
    """

    def __init__(self, gui_data_manager: ftvgd.FTV_GUIDataManager):
        qtw.QWidget.__init__(self)

        self.setFixedSize(LIST_WIDTH, LIST_HEIGHT)
        # variable for counting dataset added from the beginning of application launch
        self.no_of_datasets_added = 0
        # variable connected below to the QLineEdit object containing the name for every new dataset
        self.new_dataset_name_provided = str()

        # reference to FTV.GUIData.FTV_GUIDataManager object
        self.gdm = gui_data_manager
        # instance of DLW_List class to simulate the dynamic list of complex widgets
        self.dataset_list = GLI.DLW_List()
        # Subscribe to events of deleting list elements from the application GUI - to perform relevant backend actions
        self.dataset_list.deleted_element_handler += self.removeListElement

        # code to build GUI layout of this class
        self.main_layout = qtw.QVBoxLayout()
        # build part of the main layout using XML config file and 'PyQt5_GUI_Builder' class. Read more about this on
        # https://github.com/WiktorSusfal/pyqt5_gui_builder
        self.add_dataset_layout = GBU.PyQT5_GUI_Builder.returnGuiLayout(GUI_MAIN_CNFG_FILEPATH,
                                                                        ADD_DATASET_FORM_LAYOUT_NAME,
                                                                        self)
        # Assign QLineEdit object from the layout defined above to a class attribute
        self.dataset_name_input = self.findFirstChildWidgetRecursively(self.add_dataset_layout,
                                                                       qtw.QLineEdit,
                                                                       NEW_DATASET_NAME_INPUT_FIELD)

        # Main Layout of this class consists of form for adding new dataset and list of all datasets
        self.main_layout.addLayout(self.add_dataset_layout)
        self.main_layout.addWidget(self.dataset_list)
        self.setLayout(self.main_layout)

        self.connectGuiObjectsToVariables()

    def returnDefaultNameForNewDataset(self) -> str:
        """
        Returns default name for new dataset that appears in the one of QLineEdit PyQt5 elements on the GUI.

        :return: String default name of new dataset
        """

        return NEW_DATASET_DEFAULT_NAME_PREFIX + str(self.no_of_datasets_added)

    def connectGuiObjectsToVariables(self):
        """
        Function to make a bindings between PyQt5 GUI objects and backend variables.

        :return: None
        """
        self.dataset_name_input.textChanged.connect(lambda:
                                                    self.updateObjectFromAttribute(
                                                        dst_obj=self,
                                                        dst_property_name=nameof(self.new_dataset_name_provided),
                                                        src_property_name=nameof(self.dataset_name_input),
                                                        getter_method_name=nameof(self.dataset_name_input.text)
                                                    )
                                                    )
        self.dataset_name_input.setText(self.returnDefaultNameForNewDataset())

    def addListElement(self):
        """
        Function to add new dataset object to the application. Ensures that proper representation of new dataset
        is added to the backend 'FTV_GUIDataManager' class instance and to the frontend 'DLW_List()' class instance.
        This function is connected to the button present on the app screed (with 'Add' label).

        :return: None
        """

        self.no_of_datasets_added += 1

        # Add the proper representation of new dataset to the frontend 'DLW_List()' class instance.
        new_element_layout = GBU.PyQT5_GUI_Builder.returnGuiLayout(GUI_MAIN_CNFG_FILEPATH,
                                                                   DATASET_LAYOUT_NAME,
                                                                   self)
        self.dataset_list += new_element_layout
        new_uuid = self.dataset_list.elements[-1].id

        # Add the proper representation of new dataset to the backend 'FTV_GUIDataManager' class instance.
        self.gdm.add_new_ftv_dataset(self.new_dataset_name_provided, new_uuid)

        self.dataset_name_input.setText(self.returnDefaultNameForNewDataset())

    def findFirstChildWidgetRecursively(self, base_layout: qtw.QLayout, widget_type, widget_name: str):
        """
        Function to search the given QLayout object and find the first occurrence of object with given type and
        given 'objectName' property. Function is recursive - if base QLayout contains sub-layouts - it will search
        them too - in the order that they appear in the base layout. Function starts to search the sub-layout BEFORE
        finishing searching parent layout.

        :param base_layout: QLayout object to search
        :param widget_type: Type of the QWidget to be found - e.g. PyQt5.QtWidgets.QPushButton etc.. .
        :param widget_name: Desired value of the 'objectName' property of the destination QWidget object
        :return: First QWidget object with given type and 'objectName' property. If nothing found - returns None.
        """
        for i in range(base_layout.count()):
            widget = base_layout.itemAt(i)
            if isinstance(widget, qtw.QLayout):
                return self.findFirstChildWidgetRecursively(widget, widget_type, widget_name)
            else:
                if widget.widget().objectName() == widget_name and isinstance(widget.widget(), widget_type):
                    return widget.widget()

        return None

    def findListElementUuidByWidgetUsed(self, widget: qtw.QWidget, obj_name: str, widget_type) -> str:
        """
        Every dataset list item has a set of buttons (widgets). Buttons are assigned to functions located here
        (in class 'DataSetList'). To perform relevant action, there is a need to know which list item the button was
        pressed in.

        This function searches all list items and checks if the 'sender' object (which is the button or widget pressed)
        exists in a particular list item's ('DataSetListElement' object) layout. If yes, it returns the string uuid of
        the whole item. Function returns uuid of the first dataset list element that meets the requirements.

        Function gets also the PyQt5 object name 'obj_name' of desired widget which the sender object
        needs to be compared with.

        :param widget: Reference to the QWidget that needs to be found in layouts of dataset list elements.
        :param obj_name: PyQt5 'objectName' attribute of the widget that needs to be compared with 'widget' given.
        :param widget_type: Type of the desired widgets to be compared with the one provided in 'widget' param.

        :return: String uuid of whole data list element that contains desired widget. If none found - empty string.
        """
        uuid_of_element = str()
        for dataset_list_element in self.dataset_list.elements:
            current_widget = self.findFirstChildWidgetRecursively(dataset_list_element.main_layout, widget_type,
                                                                  obj_name)
            if widget == current_widget:
                uuid_of_element = dataset_list_element.id
                break

        return uuid_of_element

    def removeListElement(self, element_uuid: str):
        """
        Function that removes desired dataset object (instance of 'FTV_JsonDataManager' class) from instance of
        "FTV_GUIDataManager" class. The json data stored in this object (relevant to the deleted GUI dataset list
        element) is no longer stored in the application.

        :param element_uuid: String uuid of dataset (common for backend "FTV_GUIDataManager" class and frontend
            "DLW_List")
        :return: None
        """
        if not element_uuid:
            raise Exception('Tried to delete element form GUI list that does not exists')
        else:
            self.gdm.delete_ftv_dataset(element_uuid)

    def assignFramesFilePath(self):
        """
        Function connected to QPushButton object from dataset list GUI element (item from 'DLW_List' object). Opend
        QFileDialog and allows to choose the path to the relevant json file containing source data. The path is then
        updated in the relevant 'FTV_JsonDataManager' object from 'FTV_GUIDataManager' class instance.

        :return: None
        """
        filepath, check = qtw.QFileDialog.getOpenFileName(None,
                                                          'Football Tactics Viewer - choose path to json FRAMES data',
                                                          '', FILTER_JSON_DATA_FILES)
        if check:
            uuid_to_update = self.findListElementUuidByWidgetUsed(self.sender(), SET_FRAMES_FILEPATH_BUTTON_NAME,
                                                                  qtw.QPushButton)
            self.gdm.ftv_datasets[uuid_to_update].assignFilePaths(ftvjs.FTV_DataReadModes.FRAMES.value, filepath)

    def assignEventsFilePath(self):
        """
        Function connected to QPushButton object from dataset list GUI element (item from 'DLW_List' object). Opend
        QFileDialog and allows to choose the path to the relevant json file containing source data. The path is then
        updated in the relevant 'FTV_JsonDataManager' object from 'FTV_GUIDataManager' class instance.

        :return: None
        """
        filepath, check = qtw.QFileDialog.getOpenFileName(None,
                                                          'Football Tactics Viewer - choose path to json EVENTS data',
                                                          '', FILTER_JSON_DATA_FILES)
        if check:
            uuid_to_update = self.findListElementUuidByWidgetUsed(self.sender(), SET_EVENTS_FILEPATH_BUTTON_NAME,
                                                                  qtw.QPushButton)
            self.gdm.ftv_datasets[uuid_to_update].assignFilePaths(ftvjs.FTV_DataReadModes.EVENTS.value, filepath)

    def assignLineupsFilePath(self):
        """
        Function connected to QPushButton object from dataset list GUI element (item from 'DLW_List' object). Opend
        QFileDialog and allows to choose the path to the relevant json file containing source data. The path is then
        updated in the relevant 'FTV_JsonDataManager' object from 'FTV_GUIDataManager' class instance.

        :return: None
        """
        filepath, check = qtw.QFileDialog.getOpenFileName(None,
                                                          'Football Tactics Viewer - choose path to json LINEUPS data',
                                                          '', FILTER_JSON_DATA_FILES)
        if check:
            uuid_to_update = self.findListElementUuidByWidgetUsed(self.sender(), SET_LINEUPS_FILEPATH_BUTTON_NAME,
                                                                  qtw.QPushButton)
            self.gdm.ftv_datasets[uuid_to_update].assignFilePaths(ftvjs.FTV_DataReadModes.LINEUPS.value, filepath)


class PitchView(qtw.QWidget):
    """
    Class for football pitch visualization. Contains methods to draw players positions on the pitch based on given data.
    """

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

        self.pitch_pixmap = self.returnPixmap("Resources/TestFootballField.png",
                                              scaled_height=FOOTBALL_PITCH_HEIGHT, scaled_width=FOOTBALL_PITCH_WIDTH
                                              )

    @staticmethod
    def returnPixmap(png_file_path: str, scaled_width: int = None, scaled_height: int = None) -> qtg.QPixmap:
        """
        Returns pixmap of given png file, scaled with given width and height.

        :param png_file_path: String path to png file.
        :param scaled_width: Optional width parameter to scale pixmap.
        :param scaled_height: Optional height parameter to scale pixmap.

        :return: QPixmap object
        """

        pixmap_image = qtg.QPixmap(png_file_path)

        if scaled_width and scaled_height:
            pixmap_image = pixmap_image.scaled(scaled_width, scaled_height, qt.Qt.IgnoreAspectRatio)
        elif scaled_width:
            pixmap_image = pixmap_image.scaledToWidth(scaled_width)
        elif scaled_height:
            pixmap_image = pixmap_image.scaledToHeight(scaled_height)

        return pixmap_image

    def paintEvent(self, event):
        """
        Function to draw the football pitch image initially on screen.

        :param event: PyQt5 event.
        :return: None
        """
        painter = qtg.QPainter(self)
        painter.drawPixmap(self.rect(), self.pitch_pixmap)

    def updatePitchPlayers(self, frames_players: pd.DataFrame, events_details: pd.DataFrame,
                           teams_details: pd.DataFrame):
        """
        Draws new positions of players on the pitch, based on given data.

        :param frames_players: Pandas DataFrame containing player positions' coordinates - read from json file.
        :param events_details: Pandas DataFrame containing event details necessary to draw the players properly.
        :param teams_details: Pandas DataFrame containing lineups details necessary to draw the players properly.

        :return: None
        """

        # painter to draw pixmap itself:
        main_painter = qtg.QPainter(self)
        # reset the pitch view before drawing
        self.pitch_pixmap = self.returnPixmap("Resources/TestFootballField.png",
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

    def returnXCoordinate(self, org_x: float, event_team_idx: int, period_no: id) -> int:
        """
        Returns coordinates in pitch's dataframe based on the original json data.

        :param org_x: Original float value of the X coordinate.
        :param event_team_idx: Integer value of the id of the team that is related to current event.
        :param period_no: Integer number of the period of the football match (from the range: 1-5)

        :return: Integer calculated X coordinate - ready for drawing the player on the pitch.
        """
        # projection of the coordinates - from original range (form json data) to destination (pitch view)
        dest_x = int((org_x - ORG_X_RANGE[0]) / (ORG_X_RANGE[1] - ORG_X_RANGE[0]) \
                     * (self.pitch_x_range[1] - self.pitch_x_range[0]) + self.pitch_x_range[0])

        # if first team (with index 0) is related to event and period of game is odd, then coordinates stays the same.
        # otherwise, they need to be reversed to display the players properly
        if (event_team_idx == 0 and period_no % 2 == 0) or (event_team_idx == 1 and period_no % 2 == 1):
            # mirror the coordinate
            dest_x = self.pitch_x_range[1] - (dest_x - self.pitch_x_range[0])

        return dest_x

    def returnYCoordinate(self, org_y: float) -> int:
        """
        Returns coordinates in pitch's dataframe based on the original json data.

        :param org_y: Original float value of the Y coordinate.
        :return: Integer calculated Y coordinate - ready for drawing the player on the pitch.
        """
        # projection of the coordinates - from original range (form json data) to destination (pitch view)
        dest_y = int((org_y - ORG_Y_RANGE[0]) / (ORG_Y_RANGE[1] - ORG_Y_RANGE[0]) \
                     * (self.pitch_y_range[1] - self.pitch_y_range[0]) + self.pitch_y_range[0])

        # mirror the coordinate - pitch on GUI has reversed direction of the Y-axis
        dest_y = int(self.pitch_y_range[1] - (dest_y - self.pitch_y_range[0]))

        return dest_y

    @staticmethod
    def returnPixmapCoordinates(pitch_coordinates: np.array) -> qt.QRect:
        """
        Returns coordinates in the pitch pixmap's coordinates frame in a form readable by QPainter object
        (as a QRect object). Function considers spaces around exact pitch field and the way that the ellipse is being
        drawn - there is a need to specify top-left point of a rectangle and its width and height. Ellipse is then
        filling the rectangle specified.

        :param pitch_coordinates: Numpy array containing X and Y pitch coordinates - calculated based on raw json data.
        :return: qt.QRect object.
        """

        # add border sizes to the exact pitch coordinates
        pixmap_coordinates = pitch_coordinates + PITCH_BORDER_SIZE
        # calculate the rectangle's top-left corner coordinates
        pixmap_coordinates -= PLAYER_SIZE

        top_left_corner = qt.QPoint(int(pixmap_coordinates[0]), int(pixmap_coordinates[1]))
        size = qt.QSize(int(PLAYER_SIZE[0]), int(PLAYER_SIZE[1]))

        return qt.QRect(top_left_corner, size)

    def returnIconColor(self, event_team_idx: int, is_teammate: bool, is_keeper: bool) -> qtg.QColor:
        """
        Returns QColor object to draw specific player icon on pitch based on the data provided.

        :param event_team_idx: Int identifier of the team that is related to the current event.
        :param is_teammate: True if current player is a teammate of the team described by 'event_team_idx' param.
        :param is_keeper: True if current player is a keeper.

        :return: qtg.QColor object.
        """
        player_team_idx = event_team_idx if is_teammate else int(bool(event_team_idx - 1))
        player_type = 'keeper' if is_keeper else 'player'

        return self.icon_colors[player_team_idx][player_type]


# application main window class
class MainWindow(qtw.QMainWindow):
    def __init__(self):
        super().__init__()
        # Initialize FTV_GUIDataManager object for main window
        self.g_data_manager = ftvgd.FTV_GUIDataManager()
        # Initialize DataSetList object for main window
        self.dataset_gui_list = DataSetList(self.g_data_manager)
        self.setCentralWidget(self.dataset_gui_list)
        """
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
        """
        self.show()


if __name__ == '__main__':
    app = qtw.QApplication([])
    app_main_gui = MainWindow()
    app.exec_()
