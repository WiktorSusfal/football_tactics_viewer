from enum import *


class PublicationArguments(Enum):
    """
    Enum class to store types of event publication arguments. Used to build dictionaries of arguments that are passed
    to some PropertyChangedEventHandler's functions. Particular enum values acts as keys for dictionaries.

    Values:

    - PUB_OBJ - key for storing publisher object reference
    - OBJ_PROP_NAME - key for storing publisher object's attribute name
    """
    PUB_OBJ = 0
    OBJ_PROP_NAME = 1


class CallbackData(Enum):
    """
    Enum class to store types of information needed during callbacks execution. Used to build dictionaries containing
    callbacks' execution parameters. Particular enum values acts as keys for dictionaries.

    Values:

    - DESTINATION_OBJECT - key for subscriber object - whose attribute is to receive new value
    - DST_PROPERTY_NAME - key for subscriber object's attribute name
    - SET_METHOD_NAME - key for the name of the setter method used to set new value to the subscriber's attribute
    - SOURCE_OBJECT -  key for publisher object - whose attribute is to produce new value
    - SRC_PROPERTY_NAME - key for publisher object's attribute name
    - GET_METHOD_NAME - key for the name of the getter method used to get new value from the publisher's attribute
    """
    DESTINATION_OBJECT = 0
    DST_PROPERTY_NAME = 1
    SET_METHOD_NAME = 2
    SOURCE_OBJECT = 3
    SRC_PROPERTY_NAME = 4
    GET_METHOD_NAME = 5


class PropertyChangedEventHandler:
    """
    Class to manage the event-driven callback mechanism for exchanging attributes' values between objects.
    Whole process is as follows:
    - subscriber objects needs to SUBSCRIBE to particular attribute
    - publisher object need to PUBLISH changes of its attribute (by calling proper handler's method) - so
    PropertyChangedEventHandler can spread the new value to every relevant subscribers' attributes.
    """
    callbacks = dict()

    @classmethod
    def subscribeToAttribute(cls, callback_data: dict):
        """
        Creates subscription to given attribute's changes. Since subscription creation, there will be always relevant
        callback performed when there is a property change event triggered for subscribed attribute.

        :param callback_data: Dictionary of arguments used to subscribe to particular attribute's changes and
            to perform relevant callback actions. Build e.g. with 'returnSubscriptionCallbackData' method from this
            class. Contains keys that conform 'CallbackData' enum values.
        :return: None
        """
        dst_obj, dst_attr, setter_method_ame, src_obj, src_attr, getter_method_name = \
            cls.extractSubscriptionCallbackData(callback_data)

        # Register observed variable (source of property changed events) if not registered yet
        cls._registerObservedVariable(src_obj, src_attr)
        # Add given callback data to the callback's list assigned to the given attribute
        cls.callbacks[src_obj][src_attr].append(callback_data)

    @classmethod
    def _registerObservedVariable(cls, pub_obj, obj_property_name: str):
        """
        Method to register new attribute to let other objects to subscribe to its changes. Creates new entry in
        'PropertyChangedEventHandler.callbacks' dictionary being a central database of whole event mechanism.

        The 'callbacks' dictionary has the following structure:

        {
            publisher_object_reference_1 :  {
                publisher_object_attribute_name_1 : [ <list of callbacks data dictionaries > ],

                publisher_object_attribute_name_2 : [ <list of callbacks data dictionaries > ],

                ...
            },

            publisher_object_reference_2 : { ... },

            ...
        }

        :param pub_obj: Reference to the object containing attribute that the property changed event is triggered for.
        :param obj_property_name: Name of the changing attribute.
        :return: None
        """

        if pub_obj is None:
            raise ValueError('Cannot register None object in the property changed event handler!')
        elif obj_property_name is None:
            raise ValueError('Cannot register property without name in the property changed event handler!')

        if pub_obj not in cls.callbacks:
            cls.callbacks[pub_obj] = {obj_property_name: list()}
        elif obj_property_name not in cls.callbacks[pub_obj]:
            cls.callbacks[pub_obj][obj_property_name] = list()

    @classmethod
    def _unregisterObservedVariable(cls, pub_obj, obj_property_name: str):
        """
        Method to unregister given attribute from PropertyChangedEventHandler. After calling this method, triggering
        property changed event for the given attribute will not start any callback action.

        Deletes entry in the 'PropertyChangedEventHandler.callbacks' dictionary, related to the specified attribute .

        :param pub_obj: Reference to the object containing attribute that the property changed event is triggered for.
        :param obj_property_name: Name of the changing attribute.
        :return: None
        """

        if pub_obj in cls.callbacks and obj_property_name in cls.callbacks[pub_obj]:
            del cls.callbacks[pub_obj][obj_property_name]

        if pub_obj in cls.callbacks and not any(cls.callbacks[pub_obj]):
            del cls.callbacks[pub_obj]

    @classmethod
    def triggerBindingUpdate(cls, prop_changed_event_pub_args: dict):
        """
        Method to trigger the property changed event for particular registered attribute
        - starting the process of spreading given attribute's new value to every subscriber.

        :param prop_changed_event_pub_args: Dictionary of arguments. Build e.g. with 'returnPropChangedEventPubArgs'
            method from this class. Contains keys that conform 'PublicationArguments' enum values.
        :return: None
        """
        pub_obj, obj_property_name = cls.extractPropChangedEventPubArgs(prop_changed_event_pub_args)

        if pub_obj in cls.callbacks and obj_property_name in cls.callbacks[pub_obj]:
            cls._updateBindingsOnProperty(pub_obj, obj_property_name)

    @classmethod
    def updateAllBindings(cls):
        """
        Method to send current values of all registered attributes to all relevant subscribers. Can be used e.g.
        at the end of the main window's constructor in PyQt5 GUI application.

        :return: None
        """
        for pub_obj in cls.callbacks:
            for property_name in cls.callbacks[pub_obj]:
                cls._updateBindingsOnProperty(pub_obj, property_name)

    @classmethod
    def _updateBindingsOnProperty(cls, pub_obj, obj_property_name: str):
        """
        Method that performs relevant callback operations to transfer new value of registered attribute, which triggered
        property change event, to all attribute's subscribers.

        :param pub_obj: Reference to parent object of the registered attribute.
        :param obj_property_name: Name of the registered attribute.
        :return: None
        """

        for callback_data in cls.callbacks[pub_obj][obj_property_name]:
            # For every subscriber in a list, extract data necessary to perform callback operation.
            # Initially, data comes in the form of dictionary, whose keys conform the values of 'CallbackData' enum.
            dst_obj, dst_attr, setter_method_name, src_obj, src_attr, getter_method_name = \
                cls.extractSubscriptionCallbackData(callback_data)

            # Try to call the function which performs the exact tasks needed to transfer the value to subscriber
            try:
                cls.updateSubscriberObject(dst_obj, dst_attr, setter_method_name,
                                           src_obj, src_attr, getter_method_name)
            except Exception as E:
                raise ('Cannot complete variable -> gui binding due to some error!' + str(E))

    @staticmethod
    def updateSubscriberObject(dst_obj=None, dst_property_name: str = None, setter_method_name: str = None,
                               src_obj=None, src_property_name: str = None, getter_method_name: str = None):
        """
        Rewrites value from source to the destination object/attribute specified using given setter and getter methods.

        :param dst_obj: Object containing attribute that needs to be updated based on source value.
        :param dst_property_name: Name of the destination attribute to be updated.
        :param setter_method_name: Name of the method used to set the value of specified attribute (by default,
            the method is considered as a property of the attribute specified by 'dst_property_name' parameter).
            If the method is a property of 'dst_obj', pass 'None' for 'dst_property_name' parameter.
            When 'setter_method_name' is 'None', then 'setattr' method is used.
        :param src_obj: Object containing an attribute with a source value to be passed to the destination.
        :param src_property_name: Name of the source attribute containing the value to be passed to the destination.
        :param getter_method_name: Name of the method used to get the value of specified source attribute
            (by default, the method is considered as a property of the attribute specified by 'src_property_name').
            If the method is a property of 'src_obj', pass 'None' for 'src_property_name' parameter.
            When 'getter_method_name' is 'None' then 'getattr' method is used.
        :return: None
        """

        # If destination or source objects are None, return exception error
        if dst_obj is None or src_obj is None:
            raise ValueError('Destination and source objects cannot be None!')

        # STAGE 1 - Get the new value from source

        # When getter method is a 'getattr'
        if getter_method_name is None:
            new_value = getattr(src_obj, src_property_name)
        # When getter method is custom
        else:
            # STAGE 1.1 - get the getter method - from source object or object's attribute
            getter_method_owner = src_obj if src_property_name is None else getattr(src_obj, src_property_name)
            getter_method = getattr(getter_method_owner, getter_method_name)

            # STAGE 1.2 - get the value to be passed to the destination
            new_value = getter_method()

        # STAGE 2 - pass the new value to the destination

        # When setter method is a 'setattr'
        if setter_method_name is None:
            setattr(dst_obj, dst_property_name, new_value)
        # When setter method is custom
        else:
            # STAGE 2.1 - get the setter method - from source object or object's attribute
            setter_method_owner = dst_obj if dst_property_name is None else getattr(dst_obj, dst_property_name)
            setter_method = getattr(setter_method_owner, setter_method_name)

            # STAGE 2.2 - set the value using setter method
            setter_method(new_value)

    @staticmethod
    def returnPropChangedEventPubArgs(pub_obj, obj_property_name: str) -> dict:
        """
        Method to build dictionary of arguments used for triggering property changed event for particular
        registered attribute.

        Keys of the result dictionary conform the values from 'PublicationArguments' enum class.

        :param pub_obj: Reference to object which contains attribute to register/unregister/trigger event for.
        :param obj_property_name: Name of the attribute to register/unregister/trigger event for.
        :return: dict( < keys conform the values from 'PublicationArguments' enum class > )
        """
        return {PublicationArguments.PUB_OBJ.value: pub_obj,
                PublicationArguments.OBJ_PROP_NAME.value: obj_property_name}

    @staticmethod
    def extractPropChangedEventPubArgs(prop_changed_event_pub_args: dict) -> tuple:
        """
        Method to extract the values from dictionary built with 'returnPropChangedEventPubArgs' method.

        :param prop_changed_event_pub_args: Dictionary of values built with 'returnPropChangedEventPubArgs' method.
        :return: Tuple of values from dict parameter whose keys correspond to 'PublicationArguments' enum values.
        """
        return prop_changed_event_pub_args[PublicationArguments.PUB_OBJ.value], \
               prop_changed_event_pub_args[PublicationArguments.OBJ_PROP_NAME.value]

    @staticmethod
    def returnSubscriptionCallbackData(dst_obj, dst_property_name: str, setter_method_name: str,
                                       src_obj, src_property_name: str, getter_method_name: str) -> dict:
        """
        Method to build dictionary of arguments used for:

        - subscribing to particular attribute registered in PropertyChangedEventHandler class,
        - performing relevant callback operations after triggering property changed event for given attribute.

        Keys of the result dictionary conform the values from 'CallbackData' enum class.

        :param dst_obj: Reference to object containing attribute to receive new value.
        :param dst_property_name: Name of the attribute to receive new value.
        :param setter_method_name: Name of the method to set the value to the attribute.
        :param src_obj: Reference to object containing attribute that produces new value.
        :param src_property_name: Name of the attribute that produces new value.
        :param getter_method_name: Name of the method to get the value from the source attribute.
        :return: dict( < keys conform the values from 'CallbackData' enum class > )
        """
        return {
            CallbackData.DESTINATION_OBJECT.value: dst_obj,
            CallbackData.DST_PROPERTY_NAME.value: dst_property_name,
            CallbackData.SET_METHOD_NAME.value: setter_method_name,
            CallbackData.SOURCE_OBJECT.value: src_obj,
            CallbackData.SRC_PROPERTY_NAME.value: src_property_name,
            CallbackData.GET_METHOD_NAME.value: getter_method_name
        }

    @staticmethod
    def extractSubscriptionCallbackData(subscription_callback_data: dict) -> tuple:
        """
        Method to extract the values from dictionary built with 'returnSubscriptionCallbackData' method.

        :param subscription_callback_data: Dictionary of values built with 'returnSubscriptionCallbackData' method.
        :return: Tuple of values from dict parameter whose keys correspond to 'CallbackData' enum values.
        """
        return subscription_callback_data[CallbackData.DESTINATION_OBJECT.value], \
               subscription_callback_data[CallbackData.DST_PROPERTY_NAME.value], \
               subscription_callback_data[CallbackData.SET_METHOD_NAME.value], \
               subscription_callback_data[CallbackData.SOURCE_OBJECT.value], \
               subscription_callback_data[CallbackData.SRC_PROPERTY_NAME.value], \
               subscription_callback_data[CallbackData.GET_METHOD_NAME.value]
