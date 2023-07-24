"""
Checks for python environment and packages
"""
import typing as t
import sys
import subprocess
import re

from .base import CheckVersion
from .utils import version_to_tuple

__all__ = ("CheckPythonPackage",)


class CheckPythonPackage(CheckVersion):
    """Check the availability and version of a python package"""

    # use the pip freeze method
    use_pip_freeze: bool = True

    # The regex to use for parsing python package names
    pip_pkg_str = r"^(?P<name>{pkg_name})==(?P<ver>[\d\w.]+)$"

    # The results of pip freeze
    pip_freeze: t.Union[str, None]

    aliases = ("checkPythonPackage", "checkPythonPkg", "CheckPythonPkg")

    def get_current_version(self) -> t.Union[None, t.Tuple[int]]:
        pkg_name, op, version = self.value
        python = sys.executable  # current python interpreter

        # Nothing to do if the package name was not found
        if pkg_name is None:
            return None

        # Method 1 -- try pip freeze
        # First, try loading the freeze
        if self.use_pip_freeze and not hasattr(self, "pip_freeze"):
            proc = subprocess.run(
                args=(python, "-m", "pip", "freeze"), capture_output=True
            )

            if proc.returncode != 0:
                # This command didn't work. Set the class attribute for all
                # instances
                CheckPythonPackage.pip_freeze = None
            else:
                CheckPythonPackage.pip_freeze = proc.stdout.decode("UTF-8")

        # Parse the pip freeze
        if getattr(self, "pip_freeze", None) is not None:
            pattern = self.pip_pkg_str.format(pkg_name=pkg_name)
            match = re.search(pattern, self.pip_freeze, re.MULTILINE)

            # Convert the regex match to a version tuple
            version = match.groupdict()["ver"] if match is not None else None
            return version_to_tuple(version) if version is not None else None

        # Method 2 -- try importing and getting it from the __version__ string
        code = f"import {pkg_name}; print({pkg_name}.__version__)"
        proc = subprocess.run(args=(python, "-c", code), capture_output=True)

        if proc.returncode == 0:
            version_str = (
                proc.stdout.decode("UTF-8").strip() if proc.stdout is not None else None
            )
            return version_to_tuple(version_str) if version_str is not None else None

        # I'm out of ideas. Version couldn't be parsed
        return None
