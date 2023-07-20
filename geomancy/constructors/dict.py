"""Constructs for dict types"""
import typing as t

from ..checks import CheckBase

__all__ = ('construct_from_dict', )


def construct_from_dict(name: str,
                        d: dict,
                        level: int = 1,
                        max_level: int = 10) -> t.Union[None, CheckBase]:
    """Construct a Check tree from a dict.

    Notes
    -----
    This function is meant to work recursively."""
    # Check that the maximum recursion level hasn't been reached
    if level >= max_level:
        msg = f"Parsing level {level} exceed the maximum level of {max_level}"
        raise NotImplementedError(msg)

    # Get a listing of the available Check types
    check_types = CheckBase.types_dict()

    # See if the dict makes a call to a Check type
    matching_keys = [k for k in d.keys() if k in check_types]

    if len(matching_keys) > 1:
        msg = f"More than 1 check type specified: {matching_keys}"
        raise NotImplementedError(msg)

    # Parse the check if a single check was given
    if len(matching_keys) == 1:
        # Get the check class
        check_type = matching_keys[0]
        cls = check_types[check_type]

        # Get the value for the check
        value = d[check_type]

        # Get the other kwargs
        kwargs = {k: v for k, v in d.items() if k != check_type}

        # Create and return the check_type
        return cls(name, value, **kwargs)

    # Otherwise, try parsing the sub_checks
    items = d.items()
    found_checks = []  # Values parsed into CheckBase objects
    other_d = dict()   # All other values
    for key, value in items:
        if not isinstance(value, dict):
            other_d[key] = value
            continue

        return_value = construct_from_dict(name=key, d=value, level=level + 1,
                                           max_level=max_level)

        # Replace the value withe CheckBase instance, if it was parsed correctly
        # Otherwise, just place it in the parsed_dict.
        if isinstance(return_value, CheckBase):
            found_checks.append(return_value)
        else:
            other_d[key] = value

    # No sub-checks found; nothing else to do
    if len(found_checks) == 0:
        return None

    # Create a check grouping, first, by parsing the other arguments
    return CheckBase(name=name, sub_checks=found_checks, **other_d)

