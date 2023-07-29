"""
Checks for python environment and packages
"""
import typing as t
import logging
import importlib.metadata  # python >= 3.8

from .version import CheckVersion
from .utils import version_to_tuple
from ..config import Parameter

__all__ = ("CheckPythonPackage",)

logger = logging.getLogger(__name__)


class CheckPythonPackage(CheckVersion):
    """Check the availability and version of a python package"""

    # The message for checking python packages
    msg = Parameter(
        "CHECKPYTHONPACKAGE.MSG",
        default="Check python package '{check.raw_value}'...",
    )

    aliases = ("checkPythonPackage", "checkPythonPkg", "CheckPythonPkg")

    def get_current_version(self) -> t.Union[None, t.Tuple[int]]:
        # Get the package name, operator and version to check against (the last
        # 2 aren't used here)
        pkg_name, op, version = self.value

        # Nothing to do if the package name was not found
        if pkg_name is None:
            return None

        # Method 1 -- importlib.metadata
        try:
            # Returns a version string--e.g. '0.9.3'
            version_string = importlib.metadata.version(pkg_name)

            # Return the version tuple--e.g. (0, 9, 3)
            return version_to_tuple(version_string) if version_string else None
        except importlib.metadata.PackageNotFoundError:
            return None
