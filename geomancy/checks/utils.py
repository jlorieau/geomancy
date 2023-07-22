"""Utility functions"""
import os

__all__ = ('sub_env',)


def sub_env(obj):
    """Substitutes environment variables of the form {VARIABLE_NAME} in
    strings"""
    if isinstance(obj, str):
        return obj.format(**os.environ)
    elif hasattr(obj, "__iter__"):
        o_type = type(obj)
        items = obj.items() if hasattr(obj, "items") else obj
        return o_type(sub_env(i) for i in items)
    else:
        return obj
