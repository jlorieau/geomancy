"""Utility functions"""
import typing as t
import operator
import re

__all__ = ("all_subclasses", "version_to_tuple", "name_and_version")

__missing__ = object()  # used an argument for missing values


def all_subclasses(cls) -> t.List[t.Type]:
    """Retrieve all subclasses, sub-subclasses and so on for a class

    Parameters
    ----------
    cls : Type
        The class object to inspect for subclasses.

    Returns
    -------
    subclasses : list
        The list of all subclasses.

    Examples
    --------
    >>> class A(object): pass
    >>> class B(A): pass
    >>> class C(B): pass
    >>> all_subclasses(A)
    [<class 'geomancy.checks.utils.B'>, <class 'geomancy.checks.utils.C'>]
    """
    return cls.__subclasses__() + [
        g for s in cls.__subclasses__() for g in all_subclasses(s)
    ]


def pop_first(d: dict, *keys, del_remaining: bool = True, default: t.Any = __missing__):
    """Pop the first key found in the dict.

    Parameters
    ----------
    d
        The dict to search for keys to pop
    *keys
        The list of keys to search
    del_remaining
        Delete the remaining keys from the dict
    default
        Return this value if a key isn't found. If not specified, a KeyError
        is raised

    Returns
    -------
    value
        The value for the first matching key

    Raises
    ------
    KeyError
        If none of the keys were found and a default wasn't found

    Examples
    --------
    >>> pop_first({'a': 1, 'b': 2, 'c': 3}, 'b', 'a')
    2
    >>> pop_first({'a': 1, 'b': 2, 'c': 3}, 'a', 'b')
    1
    >>> pop_first({'a': 1, 'b': 2, 'c': 3}, 'e', default='missing')
    'missing'
    >>> d = {'a1': 1, 'a2': 2, 'b': 3}
    >>> pop_first(d, 'a1', 'a2')
    1
    >>> print(d)
    {'b': 3}
    >>> pop_first(d, 'a1')
    Traceback (most recent call last):
        ...
    KeyError: "Could not find any of the keys: ('a1',)"
    """
    value = __missing__

    # Find the first key
    for key in keys:
        value = d.pop(key, __missing__)
        if value is not __missing__:
            break

    # Del remaining
    if del_remaining:
        extra_keys = [key for key in keys if key in d]
        for k in extra_keys:
            del d[k]

    # Return a value or raise an exception
    if value is not __missing__:
        return value
    elif default is not __missing__:
        return default
    else:
        raise KeyError(f"Could not find any of the keys: {keys}")


def version_to_tuple(version: str) -> t.Union[t.Tuple[int], None]:
    """Convert a semantic version string to a tuple of integers.

    Parameters
    ----------
    version
        String with the version number. e.g. '1.4.3]

    Returns
    -------
    version_tuple or None
        Vesion in the form of a tuple of integers, or
        None if a version couldn't be found

    Notes
    -----
    This function ignores letters in a version. e.g. '0.4.1b' becomes (0, 4, 1)

    Examples
    --------
    >>> version_to_tuple('26')
    (26,)
    >>> version_to_tuple('1.3')
    (1, 3)
    >>> version_to_tuple('v0.1.3')
    (0, 1, 3)
    >>> version_to_tuple('1.2beta')
    (1, 2)
    """
    version_match = re.search(r"([\d\.]{2,}|\d+)", version)  # Capture the version
    if version_match is None:
        return None
    version = version_match.group().split(".")  # Split the version string at "."
    return tuple(map(int, version))  # Convert to a tuple of ints


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
        r"([\w\.\-_]+)"  # match package name
        r"\s*(==|>=|<=|>|<|!=)?\s*"  # operator
        r"([\d\w\.]+)?",  # version number
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
    version = version_to_tuple(version) if version is not None else None

    return name, op, version
