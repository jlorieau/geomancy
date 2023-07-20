"""An instance-wide configuration"""
import typing as t
from threading import Lock
from pathlib import Path
import tomllib


class Config:
    """A thread-safe Config manager to get and set configuration parameters.

    Notes
    -----
    The base class is deliberately modified dynamically with descriptors. This
    is because the Config was designed to be configured on the fly.
    """

    # The root singleton instance
    _instance: t.Optional["Config"] = None

    # The thread lock
    _lock: Lock = Lock()

    def __new__(cls, root: bool = True, **kwargs):
        # Create the singleton instance if it hasn't been created
        if cls._instance is None:
            # Lock the thread
            with cls._lock:
                # Prevent another thread from creating the instance in the
                # interim
                if cls._instance is None:
                    cls._instance = super().__new__(cls)

        if not root:
            # If this is not the root Config--i.e. a sub config--return a
            # new Config object instead of the root singleton
            obj = super().__new__(cls)
            return obj
        else:
            # Otherwise return the singleton
            return cls._instance

    def __init__(self, root: bool = True, **kwargs):
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
            self.__dict__[key] = Config(root=False)
            return super().__getattribute__(key)

    def __setattr__(self, key, value):
        """Set attributes in the Config"""
        super().__setattr__(key, value)

    def __len__(self):
        """The number of items in this Config"""
        return len(self.__dict__)

    @classmethod
    def load(cls, d: dict, root=True) -> "Config":
        """Load config with values from a dict.

        Parameters
        ----------
        d
            The dict with config values to load
        root
            Whether the root Config singleton is returned or a new sub config
            is returned.

        Returns
        -------
        config
            The root config instance with parameters loaded
        """
        config = cls(root=root)

        for k, v in d.items():
            # Only key strings are allowed for the Config
            assert isinstance(k, str), (
                f"Config keys must be strings. " f"Received: '{k}'"
            )

            if isinstance(v, dict):
                # Create a sub Config and load the sub dict
                sub_config = Config.load(v, root=False)
                setattr(config, k, sub_config)
            else:
                # Otherwise just store the value
                setattr(config, k, v)

        return config

    @classmethod
    def toml_loads(cls, s: str) -> "Config":
        """Load config from a string formatted in TOML format.

        Returns
        -------
        config
            The root config instance with parameters loaded
        """
        d = tomllib.loads(s)
        return cls.load(d)

    @classmethod
    def toml_load(cls, filename: Path) -> "Config":
        """Load config from a file formatted in TOML format.

        Returns
        -------
        config
            The root config instance with parameters loaded
        """
        with open(filename, "rb") as f:
            d = tomllib.load(f)
        return cls.load(d)

    def pprint(self, level=0):
        """Pretty pring the config"""
        for k, v in self.__dict__.items():
            if isinstance(v, Config):
                print("  " * level + f"** {k} **")
                v.pprint(level=level + 1)
            else:
                print("  " * level + f"{k} = {v}")


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

    __slots__ = ("key", "_config")

    # The key/name of the parameter in the Config
    key: str

    # The delimiter used for splitting keys
    delim: str = "."

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
