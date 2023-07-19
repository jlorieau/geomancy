"""Utility functions"""
import os

__all__ = ('sub_env',)


def sub_env(string: str):
    """Substitutes environment variables of the form {VARIABLE_NAME} in the
    string"""
    return string.format(**os.environ)
