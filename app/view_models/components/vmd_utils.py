"""Contains class which provides some basic and universal functionalities for other modules."""

from PyQt5.QtCore import pyqtSignal
from threading import Thread


class VmdUtils:
    """Class which provides some basic and universal functionalities for other modules."""

    @staticmethod
    def observable_property(property_name: str, signal_name: str):
            def decorator(func):
                def wrapper(*args, **kwargs):
                    target_object, setter_value = args[0], args[1]
                    target_property = getattr(target_object, property_name)
                    
                    if setter_value != target_property:
                        func(*args, **kwargs)
                        target_signal: pyqtSignal = getattr(target_object, signal_name)
                        target_signal.emit(setter_value)
                
                return wrapper
            return decorator
    
    @staticmethod
    def run_in_thread(func):
        """
        Creates new daemon Thread object and runs it with decorated method.
        """
        def wrapper(*args, **kwargs):
            t = Thread(target=func, args=args, kwargs=kwargs, daemon=True)
            t.start()
        return wrapper