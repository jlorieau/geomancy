"""An instance-wide configuration"""
import typing as t
from threading import Lock
from pathlib import Path
from collections.abc import Mapping
import re
import tomllib
import yaml
import logging

__all__ = ("ConfigException", "Config", "Parameter")

logger = logging.getLogger(__name__)


class ConfigException(Exception):
    """An exception raised in validating or modifying the config"""


class ConfigMeta(type):
    """A metaclass to set up the creation of Config objects and singleton"""

    def __call__(cls, root: bool = True, **kwargs):
        # noinspection PyArgumentList
        obj = cls.__new__(cls, root=root)
        obj.__init__(**kwargs)
        return obj


class Config(metaclass=ConfigMeta):
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

    # The regex to validate key names
    key_regex = re.compile(r"^[_A-Za-z][_A-Za-z0-9]*$")

    def __new__(cls, root: bool = True):
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

    def __init__(self, **kwargs):
        # Set the specified parameters
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __getattribute__(self, key):
        """Get attributes Config with support for attribute nesting"""
        Config.validate(key)
        try:
            return super().__getattribute__(key)
        except AttributeError:
            # Create a dict by default for a missing attribute
            # This allows nested attribute access
            self.__dict__[key] = Config(root=False)
            return super().__getattribute__(key)

    def __setattr__(self, key, value):
        """Set attributes in the Config"""
        Config.validate(key)
        super().__setattr__(key, value)

    def __len__(self):
        """The number of items in this Config"""
        return len(self.__dict__)

    @classmethod
    def validate(cls, key):
        """Ensure that the given key is valid"""
        if not cls.key_regex.match(key):
            raise ConfigException(
                f"The key '{key}' is not valid. "
                f"Must match the pattern: '{cls.key_regex.pattern}'"
            )

    def update(self, updates: Mapping) -> None:
        """Recursively update config with values from a dict.

        Parameters
        ----------
        updates
            The dict with values to recursively update

        Raises
        ------
        ConfigException
            Raised when the updates include a change that would replace a
            sub-config (subsection) that includes parameters with a single
            parameter.

        Notes
        -----
        - This function operates recursively to update sub-config (subsection)
          objects
        - This function does not allow a sub-config (subsection) to be replaced
          or truncated by a parameter. This will raise a ConfigException.
        - This function is not atomic. If a ConfigException is raised partway
          through the update, this config will only be partially updated.
        """
        for k, v in updates.items():
            current_value = getattr(self, k)  # get the current value or sub_config

            if isinstance(v, Mapping):
                # Use the corresponding update function. ex: dict
                current_value.update(v)
            elif isinstance(v, Config):
                current_value.update(v.__dict__)
            elif isinstance(current_value, Config) and len(current_value.__dict__) > 0:
                # In this case, the update value 'v' is a simple parameter but the
                # current_value is a sub-config with items in it. This is not allowed.
                raise ConfigException(
                    f"Cannot replace config section '{k}' with a parameter '{v}'"
                )
            else:
                logger.debug(f"Config.update(): set {k}={v}")
                setattr(self, k, v)

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
                logger.debug(f"Config.load(): set {k}={v}")
                setattr(config, k, v)

        return config

    @classmethod
    def loads_toml(cls, s: str) -> "Config":
        """Load config from a string formatted in TOML format.

        Returns
        -------
        config
            The root config instance with parameters loaded
        """
        d = tomllib.loads(s)
        return cls.load(d)

    @classmethod
    def load_toml(cls, filename: Path) -> "Config":
        """Load config from a file formatted in TOML format.

        Returns
        -------
        config
            The root config instance with parameters loaded
        """
        with open(filename, "rb") as f:
            d = tomllib.load(f)
        return cls.load(d)

    def dumps_toml(self, name="config", level=0) -> str:
        """Produce a string of the current config in TOML format.

        Parameters
        ----------
        name
            Name of the current section. Sub-sections are identified with '.'
            characters
        level
            Current level of the hierarchy
        """
        indent = " " * 2 * level  # indentation
        text = f"{indent}[{name}]\n"  # section heading

        # Process general parameters before sections (sub configs)
        items = [
            (k, v)
            for k, v in sorted(self.__dict__.items())
            if not isinstance(v, Config)
        ]
        for key, value in items:
            text += indent  # Add indentation

            # Different simple parameter formats for TOML
            if isinstance(value, str) and "'" not in value:
                text += f"{key}='{value}'\n"
            elif isinstance(value, str):
                text += f'{key}="{value}"\n'
            elif isinstance(value, bool):
                text += f"{key}={str(value).lower()}\n"
            else:
                text += f"{key}={value}\n"

        if len(items) > 0:
            text += "\n"

        # Next process sections (sub configs)
        items = [
            (k, v) for k, v in sorted(self.__dict__.items()) if isinstance(v, Config)
        ]
        for key, value in items:
            text += indent  # Add indentation
            text += value.dumps_toml(name=".".join((name, key)), level=level + 1)

        if level == 0:
            text = text.rstrip("\n") + "\n"  # Remove multiple terminal newlines
        return text

    def pprint_toml(self):
        """Pretty print in TOML format."""
        print(self.dumps_toml())

    def pprint_yaml(self):
        """Pretty print in YAML format"""
        print(yaml.dump({"config": self.__dict__}))


# dummy placeholder object
missing = object()


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

    def __init__(self, key, default=missing):
        self.key = key
        self._config = Config()

        # Set the default, if specified
        if default is not missing:
            self.__set__(instance=None, value=default)

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
