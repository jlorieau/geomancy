"""Functions to load dotenv files and parse strings in dotenv format"""
import typing as t
import os
import re
import codecs
import logging
from pathlib import Path

__all__ = ("sub_env", "parse_env", "load_env")

logger = logging.getLogger(__name__)

# Regex to match environment variables for subsitution--e.g. ${NAME} or $NAME
sub_re = re.compile(
    r"[$]"  # Start with a '$'. e.g. $NAME
    r"((?P<name_nobrace>[a-zA-Z_][a-zA-Z0-9_:\-?+]*)|"  # e.g. $NAME
    r" \{(?P<name_brace>[a-zA-Z_][a-zA-Z0-9_\s:\-?+]*)\})",  # e.g ${NAME}
    re.VERBOSE,
)

# Regex to identify alternate variables from variable names
# e.g. ${NAME:-default}
sub_alt_re = re.compile(
    # Does not require a brace. e.g. $NAME
    r"(?P<name>[a-zA-Z_][a-zA-Z0-9_]*)"
    # May have an alternative descriptor
    r"((?P<default>:-|-)|(?P<error>:\?|\?)|(?P<replace>:\+|\+))?(?P<alt>[\w\s]*)",
    re.VERBOSE,
)

# Regex to match environment variable names
env_name = r"(?P<name>[a-zA-Z_][a-zA-Z0-9_]*)"  # env variable name
env_name_re = re.compile(env_name)

# Regex to match environment variable values with substitution
env_value = (
    # Quoted value--e.g. "My $VAR" or 'My $VAR'--allowing for escaped quotes
    r"""((?P<quote>["|']{1,3})(?P<qvalue>(?:\\.|[^"'\\])+)(?P=quote)[^'"\n]*|"""
    # Unquoted value--e.g. My $VAR
    r"""(?P<value>[^'"\n]+))"""
)
env_value_re = re.compile(
    env_value,
    re.MULTILINE | re.DOTALL,
)

# Regex to match "name=value" pairs from an env file
env_name_value_re = re.compile(
    r"^\s*{env_name}\s*=\s*{env_value}\s*$".format(
        env_name=env_name, env_value=env_value
    ),
    re.MULTILINE | re.DOTALL,
)

# Regex to strip comments to the end of a line--# and not escaped values, \#
comment_re = re.compile(r"(^|\s+)(#.+)$")

# Regex to strip backslashes from escaped quotes.
# e.g. r"Let\'s go" -> r"Let's go"
escaped_quote_re = re.compile(r"\\(['\"])")


def sub_env(
    string: str, missing_default: str = "", strip_values: bool = True, **kwargs
) -> str:
    """Try to substitute environment variables in the string.

    Parameters
    ----------
    string
        The string to substituted
    missing_default
        Missing environment variables will have this value placed instead
    strip_values
        Remove whitespace at the start and end of non-quoted values
    kwargs
        In addition to os.environ, search the given kwargs for matches.

    Raises
    ------
    EnvironmentError
        Raised if an environment variable was not found and the :?/? error
        error is specified
        e.g. ${MISSING?not found!}

    Returns
    -------
    substituted_str
        The string with environment variables substituted

    Notes
    -----
    This function follows the docker compose_ format.
    - Environment variable names are preceded with a '$' character and may
      include braces. e.g. ``$VAR_NAME`` or ``${VAR_NAME}``
    - Environment variables names may include directives for default values
      (``${MISSING-default}``), errors for missing values (``${missing?error``)
      or replacement values (``${MISSING+replace}``)

    .. _compose: https://docs.docker.com/compose/environment-variables/env-file/
    """

    # Substitute environment variables in values
    def sub_func(m: re.Match):
        """Substitute a regex match from the environment variables, if possible,
        or return unmodified"""
        # Get the variable name, which may include alternates identified by
        # :-/-/:?/?/:+/"
        d = m.groupdict()
        name = d["name_brace"] if d["name_brace"] is not None else d["name_nobrace"]

        # Parse the alternate values
        alt_m = sub_alt_re.match(name)
        alt_d = alt_m.groupdict() if alt_m is not None else None

        name = alt_d["name"] if alt_d and alt_d["name"] else name
        default = alt_d["alt"] if alt_d and alt_d["default"] else None
        error = alt_d["alt"] if alt_d and alt_d["error"] else None
        replace = alt_d["alt"] if alt_d and alt_d["replace"] else None

        if name in os.environ:
            # found match in environment variables ('replace' will
            # replace the returned value)
            return os.environ[name] if replace is None else replace

        elif name in kwargs and not replace:
            # found match in passed keyword arguments (replace will replace its value)
            return kwargs[name] if replace is None else replace

        elif default is not None:  # Not found, return default if available
            return default

        elif error is not None:  # Not found, raise exception
            raise EnvironmentError(error)

        else:
            return missing_default

    # Parse the string like an environment variable value, which may contain
    # single quotes, double quotes or may be unquoted
    match = env_value_re.match(string)
    groupdict = match.groupdict() if match is not None else None
    if groupdict is None:
        return string

    # Try to parse the value based on the type of quoting
    if "value" in groupdict and groupdict["value"]:
        # Strip comments for non-quoted strings
        value = groupdict["value"]
        value = comment_re.sub(r"\1", value)  # Remove comments

        # Substitute values for non-quoted values
        value = sub_re.sub(sub_func, value)

        # Strip whitespace, if specified
        return value.strip() if strip_values else value

    elif "qvalue" in groupdict and groupdict["qvalue"]:
        # Retrieve quoted value and quote type
        value = groupdict["qvalue"]
        quote = groupdict["quote"]

        # Substitute escaped quotes
        value = escaped_quote_re.sub(r"\1", value)

        # Double-quote values may be substituted
        if '"' in quote:  # double quoted
            # process escape characters, e.g. \\t -> \t
            value = codecs.decode(value, "unicode_escape")

            # substitute values for double quoted values
            return sub_re.sub(sub_func, value)

        # Single-quoted values are used literally--i.e. without substitution
        elif "'" in quote:
            return value

    else:
        raise NotImplementedError


def parse_env(string: str, strip_values: bool = True) -> dict:
    """Parse a string in env format into a dict.

    See :func:`sub_env` for details on substitution.

    Parameters
    ----------
    string
        The string in env format to parse
    strip_values
        Remove whitespace at the start and end of non-quoted values

    Returns
    -------
    env_vars
        The parsed environment variables from the string. The variable names
        are dict keys and the variable values are dict values.
    """

    # Convert string into a dict
    env_vars = dict()
    for match in env_name_value_re.finditer(string):
        name = match.group(1)  # name (group 1)

        # env_value match. Keep full group, including quotes so that sub_env can parse
        # the value
        rest = match.group(2)

        # Substitute environment variables in the value
        value = sub_env(rest, strip_values=strip_values, **env_vars)

        # Add the new name-value pair in the env_vars
        env_vars[name] = value

    return env_vars


def load_env(
    filepath: t.Union[str, Path], overwrite: bool = False, *args, **kwargs
) -> dict:
    """Load an environment file.

    Parameters
    ----------
    filepath
        The path to the file with environment settings to load
    overwrite
        If True, overwrite environment variables that already exist
        If False (default), only load environment variables that don't already
        exist
    args, kwargs
        Arguments and keyword arguments passed to :func:`parse_env_str`

    Returns
    -------
    env
        A dict with all of the loaded env variable name-value pairs in a dict
    """
    # Try loading the file
    filepath = Path(filepath)
    try:
        string = filepath.read_text()
    except FileNotFoundError:
        logger.error(f"Could not file the file '{filepath}'")
        return 0

    # Parse the environment
    env_vars = parse_env(string=string, *args, **kwargs)

    # Load the environment variables
    updated_env_vars = dict()
    for name, value in env_vars.items():
        # Do nothing if the variable already exists, and overwrite isn't
        # specified
        if name in os.environ and not overwrite:
            continue

        os.environ[name] = value
        updated_env_vars[name] = value

        logger.debug(f"Substituted environment variable {name}={value}")

    return updated_env_vars
