"""Utility functions"""
import typing as t
import os
import operator
import re

__all__ = ("sub_env",)


def sub_env(obj):
    """Substitutes environment variables of the form {VARIABLE_NAME} in
    strings.
    """
    if isinstance(obj, str):
        try:
            # Substitute environment variables
            return obj.format(**os.environ)
        except KeyError:
            # Could find the environment variable; return None
            return None
    elif hasattr(obj, "__iter__"):
        # Iterate over items to substitute environment variables
        o_type = type(obj)
        items = obj.items() if hasattr(obj, "items") else obj
        return o_type(sub_env(i) for i in items)
    else:
        return obj


def name_and_version(
    string,
) -> t.Tuple[
    t.Union[None, str], t.Union[None, t.Callable], t.Union[None, t.Tuple[int]]
]:
    """Parse the name and version from a package name string with an optional
    specifier.

    Parameters
    ----------
    string
        The string with a name and version to parase.

    Returns
    -------
    name, operator, version
        The name, operator and version for a package.
        None, if the string couldn't be parsed.

    Examples
    --------
    >>> name_and_version('test')
    ('test', None, None)
    >>> name_and_version('test-ab_one')
    ('test-ab_one', None, None)
    >>> name_and_version('test-ab_one>=0.3.1')
    ('test-ab_one', <built-in function ge>, (0, 3, 1))
    >>> name_and_version('new-package>1.2')
    ('new-package', <built-in function gt>, (1, 2))
    >>> name_and_version('jinja2>=2.10')
    ('jinja2', <built-in function ge>, (2, 10))
    >>> name_and_version('geo>=0.4.0a')
    ('geo', <built-in function ge>, (0, 4, 0))
    """

    m = re.search(
        r"([\w.\-_]+)"  # match package name
        r"\s*(==|>=|<=|>|<|!=)?\s*"  # operator
        r"([\d\w.]+)?",  # version number
        string,
    )

    if m is None:
        # The string couldn't be parsed
        return None, None, None

    name = m.group(1)
    op = m.group(2)
    version = m.group(3)

    # Convert the operator
    if op is not None:
        op_mapping = {
            "==": operator.eq,
            ">": operator.gt,
            "<": operator.lt,
            ">=": operator.ge,
            "<=": operator.le,
            "!=": operator.ne,
        }
        op = op_mapping[op]

    # Convert the version to a tuple of integers
    if version is not None:
        version = re.sub(r"[A-Za-z]", "", version)  # Remove letters from the version
        version = version.split(".")  # Split the version string at "."
        version = tuple(map(int, version))  # Convert to a tuple of ints

    return name, op, version
