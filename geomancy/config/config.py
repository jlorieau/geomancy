"""An instance-wide configuration"""
import typing as t
from threading import Lock


class Config:
    """A thread-safe Config manager to get and set configuration parameters.

    Notes
    -----
    The base class is deliberately modified dynamically with descriptors. This
    is because the Config was designed to be configured on the fly.
    """
    # The root singleton instance
    _instance: t.Optional['Config'] = None

    # The thread lock
    _lock: Lock = Lock()

    def __new__(cls, initial: t.Optional[dict] = None, **kwargs):
        # Create the singleton instance if it hasn't been created
        if cls._instance is None:
            # Lock the thread
            with cls._lock:
                # Prevent another thread from creating the instance in the
                # interim
                if cls._instance is None:
                    cls._instance = super().__new__(cls)

        if initial is not None:
            # If an initial dict was specified--i.e. a sub-dict of the
            # singleton--then return a Config object with its dict replaced
            # with that dict
            obj = super().__new__(cls)
            obj.__dict__ = initial
            return obj
        else:
            # Otherwise return the singleton
            return cls._instance

    def __init__(self, initial: t.Optional[dict] = None, **kwargs):
        # Set the specified parameters
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __getattribute__(self, key):
        """Get attributes Config with support for attribute nesting"""

        try:
            return super().__getattribute__(key)
        except AttributeError:
            # Create a dict by default for a missing attribute
            # This allows nested attribute access
            self.__dict__[key] = Config(initial=dict())
            return super().__getattribute__(key)

    def __setattr__(self, key, value):
        """Set attributes in the Config"""
        super().__setattr__(key, value)

    def __len__(self):
        """The number of items in this Config"""
        return len(self.__dict__)

class Parameter:
    """A descriptor for a Config parameter.

    Notes
    -----
    This is a descriptor. Its value can be accessed or modified from an
    instance. However, its value can only be access from the class itself. This
    is because the descriptor will be replaced if its corresponding class
    attribute is modified with a new value. Stated another way, the __set__
    method is not called from a class--only instances of a class.
    """

    __slots__ = ('key', '_config')

    # The key/name of the parameter in the Config
    key: str

    # The delimiter used for splitting keys
    delim: str = '.'

    # A reference to the Config() singleton
    _config: Config

    def __init__(self, key):
        self.key = key
        self._config = Config()

    def __repr__(self):
        value = getattr(self._config, self.key)
        return f"Param({self.key}={value})"

    def __get__(self, instance, objtype=None):
        # Convert strings with '.' into nested keys
        keys = self.key.split(self.delim)
        value = self._config
        for key in keys:
            value = getattr(value, key)
        return value

    def __set__(self, instance, value):
        # Convert strings with '.' into nested keys
        keys = self.key.split(self.delim)
        obj = self._config
        for key in keys[:-1]:
            obj = getattr(obj, key)
        setattr(obj, keys[-1], value)
