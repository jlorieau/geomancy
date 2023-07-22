"""Utility functions"""
import os

__all__ = ('sub_env',)


def sub_env(obj):
    """Substitutes environment variables of the form {VARIABLE_NAME} in
    strings"""
    if isinstance(obj, str):
        try:
            # Substitute environment variables
            return obj.format(**os.environ)
        except KeyError:
            # Could find the environment variable; return unchanged
            return obj
    elif hasattr(obj, "__iter__"):
        # Iterate over items to substitute environment variables
        o_type = type(obj)
        items = obj.items() if hasattr(obj, "items") else obj
        return o_type(sub_env(i) for i in items)
    else:
        return obj
