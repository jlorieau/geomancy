"""
Checks for executables
"""
import typing as t
from shutil import which

from .base import CheckBase, CheckResult
from .utils import name_and_version
from ..config import Parameter

__all__ = ("CheckExec",)


class CheckExec(CheckBase):
    """Check for the presence and version of executables"""

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
        passed = False
        name, op, version = self.value

        # See if the executable can be found
        path = which(name)

        if path:
            passed = True
            status = "passed"
        else:
            status = "missing"

        return CheckResult(
            passed=passed, msg=self.msg.format(check=self), status=status
        )
