"""Functions to load dotenv files"""
import os
import re

# Regex to match "name=value" pairs from a dotenv file
dotenv_re = re.compile(
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


def parse_dotenv_str(
    string: str, strip_values: bool = True, substitute: bool = True, load: bool = True
) -> dict:
    """Parse a string in dotenv format into a dict

    Parameters
    ----------
    string
        The string in dotenv format to parse
    strip_values
        Remove whitespace at the start and end of non-quoted values
    substitute
        Try substituting environment variable values in the form of '${NAME}'
        or '{NAME}' if available in the environment
    load
        Whether to load parsed values in the environment
    """
    # Strip comments (everything after #, but not \#
    string = comment_re.sub(r"\1", string)

    # Convert string into a dict
    d = dict()
    for match in dotenv_re.finditer(string):
        groupdict = match.groupdict()
        name = groupdict["name"]

        if "value" in groupdict and groupdict["value"]:
            # Parse non-quoted values
            d[name] = groupdict["value"].strip() if strip_values else groupdict["value"]
        elif "qvalue" in groupdict and groupdict["qvalue"]:
            # Parse quoted value
            d[name] = groupdict["qvalue"]
        else:
            continue

    # Substitute environment variables in values
    def sub_func(m: re.Match):
        """Substitute a regex match from the environment variables, if possible, or
        return unmodified"""
        name = m.groupdict()["name"]
        return os.environ[name] if name in os.environ else m.group()

    items = d.items()
    for k, v in items:
        # Substitute environment variables
        if substitute:
            v = sub_re.sub(sub_func, v)
            d[k] = v  # replace in returned dict

        # Load in the environment
        if load:
            os.environ[k] = v

    return d
