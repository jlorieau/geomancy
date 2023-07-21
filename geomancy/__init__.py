# Current package version
__version__ = (0, 1, 0, "a")  # Major, minor, patch, stage

# Current description
__description__ = "Geomancy validates deployment and development environments"


def get_version(version=__version__):
    """Generate a string from the __version__

    Examples
    --------
    >>> get_version((0, 1, 0, 'b'))
    '0.1.0b'
    >>> get_version((1, 0, 0))
    '1.0.0'
    """
    if isinstance(version[-1], str):
        return ".".join(map(str, version[:-1])) + version[-1]
    else:
        return ".".join(map(str, version))
