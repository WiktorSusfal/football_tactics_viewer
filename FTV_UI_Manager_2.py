import sys

import PyQt5
from PyQt5 import QtCore as Qt

sys.path.append('./Resources/Lib')

from Resources.Lib import DLW_GUIList as GLI
from Resources.Lib import PyQT5_GUI_Builder as GBU
from Resources.Lib import ObservableObjects as OOBJ

from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qt
from PyQt5 import QtGui as qtg
import FTV_GUIData as ftvgd
import FTV_JsonData as ftvjs
import pandas as pd
import numpy as np
from varname import *

NEW_DATASET_NAME_INPUT_FIELD = 'add_dataset_line_edit'
LIST_WIDTH = 360
LIST_HEIGHT = 700


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

        self.connectGuiObjectsToVariables()

    def connectGuiObjectsToVariables(self):
        """
        Function to make a bindings between PyQt5 GUI objects and backend variables.

        :return: None
        """
        self.dataset_name_input = self.findFirstChildWidgetRecursively(self.add_dataset_layout,
                                                                       qtw.QLineEdit,
                                                                       NEW_DATASET_NAME_INPUT_FIELD)
        self.dataset_name_input.textChanged.connect(lambda:
                                                    self.updateObjectFromAttribute(
                                                        dst_obj=self,
                                                        dst_property_name=nameof(self.new_dataset_name_provided),
                                                        src_property_name=nameof(self.dataset_name_input),
                                                        getter_method_name=nameof(self.dataset_name_input.text)
                                                    )
                                                    )
        self.dataset_name_input.setText('default_dataset_' + str(self.no_of_datasets_added))

    def addListElement(self):
        """
        Function to add new dataset object to the application. Ensures that proper representation of new dataset
        is added to the backend 'FTV_GUIDataManager' class instance and to the frontend 'DLW_List()' class instance.
        This function is connected to the button present on the app screed (with 'Add' label).

        :return: None
        """

        self.no_of_datasets_added += 1

        # Add the proper representation of new dataset to the frontend 'DLW_List()' class instance.
        new_element_layout = GBU.PyQT5_GUI_Builder.returnGuiLayout('Resources/Settings/gui_cnfg_main.xml',
                                                                   "dataset_gui_list_element",
                                                                   self)
        self.dataset_list += new_element_layout
        new_uuid = self.dataset_list.elements[-1].id

        # Add the proper representation of new dataset to the backend 'FTV_GUIDataManager' class instance.
        self.gdm.add_new_ftv_dataset(self.new_dataset_name_provided, new_uuid)

        self.dataset_name_input.setText('default_dataset_' + str(self.no_of_datasets_added))

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
