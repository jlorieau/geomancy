"""
Checks for executables
"""
import typing as t
from shutil import which
import re
import subprocess

from .base import CheckBase, CheckResult
from .utils import name_and_version, version_to_tuple
from ..config import Parameter

__all__ = ("CheckExec",)


class CheckExec(CheckBase):
    """Check for the presence and version of executables

    Notes
    """

    # The message for checking environment variables
    msg = Parameter(
        "CHECKEXEC.MSG",
        default="Check executable '{check.value}'...",
    )

    # Alternative names for the class
    aliases = ("checkExec",)

    @property
    def value(self) -> t.Any:
        """Get the value, with parsing of versions"""
        value = CheckBase.value.fget(self)
        return name_and_version(value)

    @value.setter
    def value(self, v):
        CheckBase.value.fset(self, v)

    def check(self, level: int = 0) -> CheckResult:
        """Check for the executable."""
        # Setup variables and values
        name, op, version = self.value
        current_version = None
        passed = False

        # See if the executable can be found
        cmd_path = which(name)

        # See if a version string was specified and whether it can be determined
        if cmd_path is not None and version is not None:
            for args in (  # Different commands to try for versions
                (cmd_path, "-V"),
                (cmd_path, "--version"),
            ):
                proc = subprocess.run(args, capture_output=True)
                if proc.returncode != 0:  # Wasn't a success
                    continue

                # Try to parse the current version string
                current_version = version_to_tuple(proc.stdout.decode("UTF-8"))
                current_version = (
                    current_version
                    if current_version is not None
                    else version_to_tuple(proc.stderr.decode("UTF-8"))
                )

                if current_version is not None:
                    # Current version found! We're done
                    break

        # Evaluate whether the check passed
        if cmd_path is None:
            status = "missing"
        else:
            if version is not None and current_version is None:
                status = "present but current version unknown"
            elif (
                version is not None
                and current_version is not None
                and op is not None
                and not op(current_version, version)
            ):
                status = f"version={'.'.join(map(str, current_version))}"
            else:
                status = "passed"
                passed = True

        return CheckResult(
            passed=passed, msg=self.msg.format(check=self), status=status
        )
