"""An instance-wide configuration"""
import typing as t

# Singleton dict
_config = dict()


class Config:
    """A Config manager to get and set configuration parameters.

    Notes
    -----
    The base class is deliberately modified dynamically with descriptors. This
    is because the Config was designed to be configured on the fly.
    """

    def __init__(self, **kwargs):
        global _config
        self.__dict__ = _config

        for k, v in kwargs.items():
            setattr(self, k, v)


class Parameter:
    """A descriptor for a Config parameter"""

    __slots__ = ('key', '_config')

    key: str
    _config: dict

    def __init__(self, key):
        global _config
        self.key = key
        self._config = _config

    def __repr__(self):
        value = getattr(self._config, self.key)
        return f"Param({self.key}={value})"

    def __get__(self, instance, objtype=None):
        return self._config.get(self.key)

    def __set__(self, instance, value):
        self._config[self.key] = value
