import sys

import PyQt5
from PyQt5 import QtCore as Qt
sys.path.append('./Resources/Lib')

from Resources.Lib import DLW_GUIList as GLI
from Resources.Lib import PyQT5_GUI_Builder as GBU

from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qt
from PyQt5 import QtGui as qtg
import FTV_GUIData as ftvgd
import FTV_JsonData as ftvjs
import pandas as pd
import numpy as np

NEW_DATASET_NAME_INPUT_FIELD = 'add_dataset_line_edit'
LIST_WIDTH = 360
LIST_HEIGHT = 700


class DataSetList(qtw.QWidget):
    """
    Class representing dynamic list of datasets which the data is visualized from.
    It uses the 'DLW_List' class instance to simulate a dynamic list of widgets - read more on
    https://github.com/WiktorSusfal/dynamic_list_of_widgets_pyqt5
    """
    def __init__(self, gui_data_manager: ftvgd.FTV_GUIDataManager):
        super().__init__()

        self.setFixedSize(LIST_WIDTH, LIST_HEIGHT)
        # variable for counting dataset added from the beginning of application launch
        self.no_of_datasets_added = 0

        # reference to FTV.GUIData.FTV_GUIDataManager object
        self.gdm = gui_data_manager
        # instance of DLW_List class to simulate the dynamic list of complex widgets
        self.dataset_list = GLI.DLW_List()

        # code to build GUI layout of this class
        self.main_layout = qtw.QVBoxLayout()
        # build part of the main layout using XML config file and 'PyQt5_GUI_Builder' class. Read more about this on
        # https://github.com/WiktorSusfal/pyqt5_gui_builder
        self.add_dataset_layout = GBU.PyQT5_GUI_Builder.returnGuiLayout('Resources/Settings/gui_cnfg_main.xml',
                                                                        "add_dataset_form",
                                                                       self)

        self.main_layout.addLayout(self.add_dataset_layout)
        self.main_layout.addWidget(self.dataset_list)
        self.setLayout(self.main_layout)

    def addListElement(self):
        self.no_of_datasets_added += 1

        dataset_name_input = self.findFirstChildWidgetRecursively(self.add_dataset_layout,
                                                                  qtw.QLineEdit,
                                                                  NEW_DATASET_NAME_INPUT_FIELD)
        new_dataset_name = dataset_name_input.objectName()
        new_element_layout = GBU.PyQT5_GUI_Builder.returnGuiLayout('Resources/Settings/gui_cnfg_main.xml',
                                                                    "add_dataset_form",
                                                                    self)
        self.dataset_list += new_element_layout
        new_uuid = self.dataset_list.elements[-1].id

        self.gdm.add_new_ftv_dataset(new_dataset_name, new_uuid)

        '''
        self.list_elements[new_uuid] = DataSetListElement(new_uuid, new_dataset_name)
        self.list_elements[new_uuid].choose_chcbx.clicked.connect(self.updateCurrentUUID)
        self.list_elements[new_uuid].d_btn.clicked.connect(self.removeListElement)
        self.list_elements[new_uuid].e_fpath_btn.clicked.connect(self.assignEventsFilePath)
        self.list_elements[new_uuid].f_fpath_btn.clicked.connect(self.assignFramesFilePath)
        self.list_elements[new_uuid].l_fpath_btn.clicked.connect(self.assignLineupsFilePath)
        self.updateGUIList()
        '''

    def findFirstChildWidgetRecursively(self, base_layout: qtw.QLayout, widget_type, widget_name: str):

        for i in range(base_layout.count()):
            widget = base_layout.itemAt(i)
            if isinstance(widget, qtw.QLayout):
                return self.findFirstChildWidgetRecursively(widget, widget_type, widget_name)
            else:
                if widget.widget().objectName() == widget_name and isinstance(widget.widget(), widget_type):
                    return widget.widget()

        return None


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
