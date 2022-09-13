"""
Contains base classes definitions that ensure easy way for setting up event-driven synchronization of given attribute's
values between chosen objects. It is a way of implementing the 'observable and observer object' pattern that can be
used e.g. during GUI apps development.
"""

from OO_EH_Utilities import PropertyChangedEventHandler as uPCEventHandler


class ObservableObject(object):
    """
    Class for creating python objects that will be able to send notifications about their properties' changes.
    The main aim is to communicate with other objects using event-driven callback mechanism.
    Methods implemented:

    - publishPropertyChanges
    Accepts the name of given object's attribute and triggers the 'PropertyChangedEventHandler' class to spread this
    attribute's new value to all subscribers - by invoking relevant methods on subscriber's objects specified during
    subscriptions creations.
    """

    def publishPropertyChanges(self, property_name: str):
        """
        Triggers the 'PropertyChangedEventHandler' class to spread new value of the attribute specified to subscribers.

        :param property_name: Name of the object's attribute which the callbacks will be invoked for.
        :return: None
        """
        event_args = uPCEventHandler.returnPropChangedEventPubArgs(self, property_name)
        uPCEventHandler.triggerBindingUpdate(event_args)


class ObserverObject(object):
    """
    Class for creating objects that are able to subscribe to given attribute's changes.
    Once subscription is done, the object specified is updated with source attribute's value using given method name.
    Methods implemented:

    - subscribeToVariable
    Creates subscription to changes of specified attribute for given subscriber's attribute object.

    - updateObjectFromAttribute
    Updates value of specified variable based on the source attribute given, using getter and setter methods specified.
    Can be used e.g. inside PyQt5 signal slots, e.g.:
    someQLineEdit.textChanged.connect(lambda: self.updateVariableBasedOnObject(param1, ...)).
    """

    def subscribeToVariable(self, dst_property_name: str = None, setter_method_name: str = None,
                            src_obj=None, src_property_name: str = None, getter_method_name: str = None):
        """
        Creates subscription to changes of specified attribute for given subscriber's attribute object.

        :param dst_property_name: Name of attribute that needs to keep track of source's values.
        :param setter_method_name: Name of the method used to set the value of desired attribute (by default, the method
            is considered as a property of the attribute itself). If this is a property of whole object pass 'None' for
            'dst_property_name' parameter.
            If the method should be 'setattr', then pass 'None' for this parameter.
        :param src_obj: Object containing attribute that the subscription is made for.
        :param src_property_name: Name of the attribute from 'src_obj' used as a source for subscription.
        :param getter_method_name: Name of the method used to get the value from source attribute. By default, this
            method is considered as a property of the attribute itself. Only if there is no such method assigned to this
            attribute, function tries to get the method directly from source main object (specified by 'src_obj'
            parameter).
            If the method should be 'getattr', then pass 'None' for this parameter.
        :return: None
        """

        callback_data = uPCEventHandler.returnSubscriptionCallbackData(self, dst_property_name, setter_method_name,
                                                                       src_obj, src_property_name, getter_method_name)
        uPCEventHandler.subscribeToAttribute(callback_data)

    def updateObjectFromAttribute(self, dst_obj=None, dst_property_name: str = None, setter_method_name: str = None,
                                  src_property_name: str = None, getter_method_name: str = None):
        """
        Method for one-time value rewriting - from given source attribute to given destination with the use of setter
        and getter methods specified. Used e.g. inside PyQt5 signal slots, e.g.:
        someQLineEdit.textChanged.connect(lambda: self.updateVariableBasedOnObject(param1, ...)).

        :param dst_obj: Object that contains attribute to receive new value.
        :param dst_property_name: Destination attribute name - to receive new value.
        :param setter_method_name: Setter method name. If this is a property of whole 'dst_obj' object (not the
            destination attribute), then pass 'None' for 'dst_property_name'.
            If the method should be 'setattr', then pass 'None' for this parameter.
        :param src_property_name: Name of the attribute of this object that acts as a source of the value to rewrite.
        :param getter_method_name: Name of the getter method to get the source value. If this is a property of this
            whole object, pass 'None' for 'src_property_name'.
            If the method should be 'getattr', then pass 'None' for this parameter.
        :return: None
        """
        uPCEventHandler.updateSubscriberObject(dst_obj, dst_property_name, setter_method_name,
                                               self, src_property_name, getter_method_name)
