
class DLW_EventHandler:
    """
    Event handler class to provide:

    - internal communication between list elements and the list object itself,

    - external communication between list object and other objects in the program.
    """
    def __init__(self):
        # list of callback functions to call every time the event handler object is triggered
        self.callbacks = []

    def __iadd__(self, callback):
        """
        Overloading of += operator to allow adding new callback functions to event handler.

        :param callback: Function that needs to be called when event occurs.
        :return: DLW_InternalEventHandler
        """
        self.callbacks.append(callback)

        return self

    def __isub__(self, callback):
        """
        Overloading of -= operator to allow deleting existing callback functions from event handler.

        :param callback: Function that needs to be deleted from callbacks list.
        :return: DLW_InternalEventHandler
        """
        self.callbacks.remove(callback)

        return self

    def __call__(self, *args, **kwargs):
        """
        Overloading of () operator to allow triggering the event on event handler object. Calls every callback function
        that is currently on a list.

        :param args: Optional arguments.
        :param kwargs: Optional named arguments.
        :return: None
        """
        for callback in self.callbacks:
            callback(*args, **kwargs)
