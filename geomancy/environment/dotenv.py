"""Functions to load dotenv files"""
import os
import re

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
comment_re = re.compile(r"([^\\])(#.+)$")  # Strip comments (# but not \#)


def parse_dotenv_str(
    string: str, strip_values: bool = True, substitute: bool = True
) -> dict:
    """Parse a string in dotenv format into a dict

    Parameters
    ----------
    string
        The string in dotenv format to parse
    strip_values
        Remove whitespace at the start and end of non-quoted values
    substitute
        environment variables in the form of '${NAME}'
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

    return d
