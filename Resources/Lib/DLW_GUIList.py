"""
Contains definition of a base class ('DLW_List') for storing and visualizing multiple complex graphic objects
('DLW_ListElement' instances) in a form of a list.
Contains definition of a base class ('DLW_ListElement') for representing single list element object -
with all necessary methods and attributes.
Two above classes inherit from PyQt5.QtWidgets.QWidget.
"""

from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc
from PyQt5 import QtWidgets as qtw
import uuid
import DLW_EventHandler as eh
from enum import *

# default opacities for list elements when selected and unselected
LIST_ITEM_NOT_SELECTED_OPACITY = 0.7
LIST_ITEM_SELECTED_OPACITY = 1.0


class DLW_Requests(Enum):
    """
    Enum for storing different request types that list items ('DLW_ListElement' objects) can send to list object
    ('DLW_List' instance) via event handler ('DLW_EventHandler.DLW_EventHandler').
    """
    SELECTION = 0
    DELETION = 1


class DLW_Event_Attributes(Enum):
    """
    Enum for storing different key values for dictionary which is sent as event argument during list usage.
    """
    EVENT_ACTOR = 0
    REQUEST_TYPE = 1


def buildEventArgs(values: list) -> dict:
    """
    Function to build dictionary of event arguments based on predefined keys and values.
     :param values: List of values provided - must conform the order of keys stored in enum 'DLW_Event_Attributes'.
     :return: Dictionary whose keys conform the values stored in enum 'DLW_Event_Attributes'.
    """

    args, i = {}, 0
    for attribute in DLW_Event_Attributes:
        args[attribute.value] = values[i]
        i += 1

    return args


class DLW_ListElement(qtw.QWidget):
    """
    Class for common representation of list element
    """

    def __init__(self, element_layout: qtw.QLayout, uid: str, s_handler: eh.DLW_EventHandler):
        """
        Constructor of list element object instance.
         :param element_layout: QLayout object that represents GUI layout of the list item.
         :param uid: Unique string id of list element.
         :param s_handler: Instance of DLW_EventHandler for communication with main list object.
        """
        super().__init__()

        # unique id of element - in the scope of current list
        self.id = uid
        # flag indicating if particular list element is already selected
        self.selected = False
        # object and method used to adjust the opacity of list element - based on its 'selected' state
        self.opacity_effect = qtw.QGraphicsOpacityEffect()
        self.setListItemOpacity()

        # add context menu to list item to allow for object deletion
        self.c_menu = qtw.QMenu(self)
        delete_action = qtw.QAction('Delete Item', self)
        delete_action.triggered.connect(self.deleteObjectFromList)
        self.c_menu.addAction(delete_action)

        # event handler object for real-time management of list elements
        self.selection_handler = s_handler
        self.selection_handler += self.itemRequestHandler

        # setting main layout of the list element based on constructor argument
        self.main_layout = element_layout
        self.setLayout(self.main_layout)

    def mouseReleaseEvent(self, event):
        """
        Function is automatically called when mouse-release event is captured on the list item. It is used here to
        send a request to main list object for changing the current selected item.
         :param event: Default event parameter common for PyQt5.
         :return: None
        """
        # relevant event is triggered only by mouse left-button
        if event.button() == qtc.Qt.LeftButton:
            # trigger the event handler object and pass created argument's dictionary
            event_arguments = buildEventArgs([self, DLW_Requests.SELECTION.value])
            self.selection_handler(event_arguments)

    def contextMenuEvent(self, event):
        """
        Function is automatically called when mouse-right-click event is captured on the list item. It is used here
        to present a context menu for each list item to allow e.g. deletion of item.
         :param event: Default event parameter common for PyQt5.
         :return: None
        """
        self.c_menu.popup(qtg.QCursor.pos())

    def deleteObjectFromList(self):
        """
        Function is bind to every item's contex menu option - for object deleting. It triggers the event handler with
        proper request type (DELETION)
         :return: None
        """
        event_arguments = buildEventArgs([self, DLW_Requests.DELETION.value])
        self.selection_handler(event_arguments)

    def unsubscribeHandler(self):
        """
        Function to unsubscribe from event handler before deleting object. It is called on the main list object level.
            :return: None
        """
        self.selection_handler -= self.itemRequestHandler

    def itemRequestHandler(self, event_arguments: dict):
        """
        Function is called when event handler object is triggered by some list item. Processes the event of list item's
        selection
            :param event_arguments: Dictionary whose keys conform the values from enum: DLW_Event_Attributes.
            :return: None
        """
        # parse event arguments
        event_actor = event_arguments[DLW_Event_Attributes.EVENT_ACTOR.value]
        request_type = event_arguments[DLW_Event_Attributes.REQUEST_TYPE.value]
        # if the request type was 'SELECTION', do the following:
        if request_type == DLW_Requests.SELECTION.value:
            # if the event handler is triggered by this list item - change the state of 'selected' flag;
            # if event handler is triggered by other list item - set 'selected' as false
            self.selected = not self.selected if event_actor.id == self.id else False
            # adjust list item opacity based on the 'selected' flag
            self.setListItemOpacity()

    def setListItemOpacity(self):
        """
        Function to adjust list item opacity based on the 'selected' flag
            :return: None
        """
        if self.selected:
            self.opacity_effect.setOpacity(LIST_ITEM_SELECTED_OPACITY)
        else:
            self.opacity_effect.setOpacity(LIST_ITEM_NOT_SELECTED_OPACITY)

        self.setGraphicsEffect(self.opacity_effect)


def clearLayout(layout):
    """
    Delete all widgets from given layout - used to empty the list of widgets
        :param layout: QLayout object which all the component layouts should be deleted from.
        :return: None
    """
    while layout.count() > 0:
        item = layout.takeAt(0)
        widget = item.widget()
        layout.removeWidget(widget)


class DLW_List(qtw.QWidget):
    """
    Class for representation of dynamic list
    """
    def __init__(self):
        super().__init__()

        # array of all elements stored in the list ('DLW_ListElement' objects)
        self.elements = []
        # current selected element - by the mouse-release event
        self.selected_element = None
        # event handler object for real-time management of list elements
        self.selection_handler = eh.DLW_EventHandler()
        self.selection_handler += self.requestHandler

        # event handler object to communicate about new list item selected to subscribers
        self.selected_element_changed_handler = eh.DLW_EventHandler()
        # event handler object to communicate about list element deleted
        self.deleted_element_handler = eh.DLW_EventHandler()

        # setting main layout of the list
        self.main_layout = qtw.QVBoxLayout()
        self.setLayout(self.main_layout)

    def __iadd__(self, element: qtw.QLayout):
        """
        Overload of '+=' operator to add elements to list. Operator accepts 'QLayout' object types and creates
        'DLW_ListElement' objects based on them internally. This way it is easier to assign proper event handler for
        every list item (in the constructor of list item).
            :param element: QLayout object that represents GUI of list item.
            :return: None
        """
        element_id = str(uuid.uuid4())
        self.elements.append(DLW_ListElement(element, element_id, self.selection_handler))
        # update the gui of the list - clear all the widgets and add them once again
        self.updateListGUI()

        return self

    def __isub__(self, element):
        """
        Overload of '-=' operator to remove elements from list. Support for removing items by item object reference or
        tem string uuid.
            :param element: 'DLW_ListElement' object or string uuid of list element to remove.
            :return: None
        """
        element_to_remove = None
        if isinstance(element, str):
            for list_element in self.elements:
                if list_element.id == element:
                    element_to_remove = list_element
                    break
        elif isinstance(element, DLW_ListElement):
            element_to_remove = element

        # remove the list item safely
        self.safeListItemRemoval(element_to_remove)

        # update the gui of the list - clear all the widgets and add them once again
        self.updateListGUI()

        return self

    def safeListItemRemoval(self, element_to_remove: DLW_ListElement):
        """
        Function to safely remove element from list - considering unsubscribing event handler, updating selected item
        reference etc...
            :param element_to_remove: 'DLW_ListElement' object to remove
            :return: None
        """
        if element_to_remove is not None:

            self.deleted_element_handler(element_to_remove.id)

            # if object that is being deleted is currently selected, reset the class attribute
            if element_to_remove == self.selected_element:
                self.selected_element = None
                # Publish information about change of the current selected element
                self.selected_element_changed_handler()

            element_to_remove.unsubscribeHandler()
            self.elements.remove(element_to_remove)
        else:
            raise ValueError('Cannot remove element from list. Element is None.')

    def updateListGUI(self):
        """
        Function to clear and draw all list items once again.
            :return: None
        """
        clearLayout(self.main_layout)
        for element in self.elements:
            self.main_layout.addWidget(element)

        self.main_layout.addStretch()

    def requestHandler(self, event_arguments: dict):
        """
        This function is called when event handler object is triggered by some list item.
        Event handler stores callback functions in a python list, so they are called always in the adding order. This
        function is called always before callbacks from list items.
        Perform relevant action based on the value of request type sent from list item.
            :param event_arguments: Dictionary whose keys conform the values from 'DLW_Event_Attributes' enum.
            :return: None
        """
        # parse event arguments
        event_actor = event_arguments[DLW_Event_Attributes.EVENT_ACTOR.value]
        request_type = event_arguments[DLW_Event_Attributes.REQUEST_TYPE.value]

        if request_type == DLW_Requests.SELECTION.value:
            # update the reference to the current selected item
            self.updateSelectedItem(event_actor)
            # Publish information about change of the current selected element
            self.selected_element_changed_handler(event_actor)
        elif request_type == DLW_Requests.DELETION.value:
            # delete element from list
            self -= event_actor

    def updateSelectedItem(self, event_actor: DLW_ListElement):
        """
        Method to update the reference to the current selected item.
            :param event_actor: DLW_ListElement to update.
            :return: None
        """
        # if the list item, which the mouse event was captured on, wasn't selected before, it is the selected item now
        # if the list item was selected before, it is unchecked now and there is no selected item
        if not event_actor.selected:
            self.selected_element = event_actor
        else:
            self.selected_element = None
