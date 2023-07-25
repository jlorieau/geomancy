"""Functions to load dotenv files"""
import typing as t
import os
import re
import logging
from pathlib import Path

__all__ = ("parse_env_str", "load_env")

logger = logging.getLogger(__name__)

# Regex to match "name=value" pairs from an env file
env_re = re.compile(
    r"""
    ^\s*(?P<name>[a-zA-Z_]+[a-zA-Z0-9_]*)  # Variable name
    \s*=\s*  # operator to assign value
    ((?P<quote>["|']{1,3})\s*(?P<qvalue>.+)\s*(?P=quote)|  # quoted value
     (?P<value>[^'"]+))  # non-quoted value
    \s*$
    """,
    re.MULTILINE | re.VERBOSE | re.DOTALL,
)

# Regex to strip comments to the end of a line--# and not escaped values, \#
comment_re = re.compile(r"([^\\])(#.+)$")

# Regex to match environment variables for subsitution--e.g. {NAME} or ${NAME}
sub_re = re.compile(r"[$]?{\s*(?P<name>[A-Za-z_]\w*)\s*}")  # Match env variables


def parse_env_str(
    string: str,
    strip_values: bool = True,
    substitute: bool = True,
) -> dict:
    """Parse a string in env format into a dict

    Parameters
    ----------
    string
        The string in env format to parse
    strip_values
        Remove whitespace at the start and end of non-quoted values
    substitute
        Try substituting environment variable values in the form of '${NAME}'
        or '{NAME}' if available in the environment

    Returns
    -------
    env_vars
        The parsed environment variables from the string. The variable names
        are dict keys and the variable values are dict values.
    """
    # Strip comments (everything after #, but not \#
    string = comment_re.sub(r"\1", string)

    # Convert string into a dict
    env_vars = dict()
    for match in env_re.finditer(string):
        groupdict = match.groupdict()
        name = groupdict["name"]

        if "value" in groupdict and groupdict["value"]:
            # Parse non-quoted values
            env_vars[name] = (
                groupdict["value"].strip() if strip_values else groupdict["value"]
            )
        elif "qvalue" in groupdict and groupdict["qvalue"]:
            # Parse quoted value
            env_vars[name] = groupdict["qvalue"]
        else:
            continue

    # Substitute environment variables in values
    def sub_func(m: re.Match):
        """Substitute a regex match from the environment variables, if possible,
        or return unmodified"""
        name = m.groupdict()["name"]
        if name in os.environ:
            return os.environ[name]
        elif name in env_vars:
            return env_vars[name]
        else:
            return m.group()

    items = env_vars.items()
    for k, v in items:
        # Substitute environment variables
        if substitute:
            env_vars[k] = sub_re.sub(sub_func, v)
    return env_vars


def load_env(
    filepath: t.Union[str, Path], overwrite: bool = False, *args, **kwargs
) -> int:
    """Load an environment file.

    Parameters
    ----------
    filepath
        The path to the file with environment settings to load
    overwrite
        If True, overwrite environment variables that already exist
        If False (default), only load environment variables that don't already exist
    args, kwargs
        Arguments and keyword arguments passed to :func:`parse_env_str`

    Returns
    -------
    env_substituted
        The number of environment variables substituted
    """
    # Try loading the file
    filepath = Path(filepath)
    try:
        string = filepath.read_text()
    except FileNotFoundError:
        logger.error(f"Could not file the file '{filepath}'")
        return 0

    # Parse the environment
    env_vars = parse_env_str(string=string, *args, **kwargs)

    # Load the environment variables
    count = 0
    for name, value in env_vars.items():
        # Do nothing if the variable already exists, and overwrite isn't specified
        if name in os.environ and not overwrite:
            continue

        os.environ[name] = value
        count += 1

        logger.debug(f"Substituted environment variable {name}={value}")
    logger.debug(f"Substituted {count} environment variables from {filepath}")

    return count
