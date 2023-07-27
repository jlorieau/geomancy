"""CLI utils"""
import typing as t
from pathlib import Path
import logging

__all__ = ("filepaths",)

logger = logging.getLogger(__name__)


def filepaths(string: str) -> t.List[Path]:
    """Given a string for a filepath or file glob, verifies that the path(s)
    exist converts to path object(s).

    Parameters
    ----------
    string
        The path string to verify and convert, which may include gobs

    Returns
    -------
    paths
        The paths for the existing files
    """
    # See if there's a glob pattern in the string
    if any(c in string for c in ("*", "?", "[", "]")):
        # Expand the glob from the current directory
        paths = list(Path(".").glob(string))
    else:
        paths = [Path(string)]

    # Check the paths
    existing_paths = []
    for path in paths:
        if path.is_file():
            existing_paths.append(path)

    return existing_paths
