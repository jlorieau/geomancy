"""Check abstract base class for checks that include versions"""
import typing as t
from abc import abstractmethod

from .base import CheckBase, CheckResult
from .utils import name_and_version

__all__ = ("CheckVersion",)


class CheckVersion(CheckBase):
    """An abstract Check for package and program versions"""

    # If true, the result of get_current_version must not be None
    # Set to True if get_current_version should return a version if the command
    # or package exists
    # Set to False if get_current_version may not be able to return the
    # version, even if the command or package is installed or present
    require_current_version: bool = True

    @property
    def value(
        self,
    ) -> t.Tuple[
        t.Union[str, None], t.Union[t.Callable, None], t.Union[t.Tuple[int], None]
    ]:
        """Get the package name, comparison operator and version tuple."""
        value = CheckBase.value.fget(self)
        name, op, version = name_and_version(value)
        return name, op, version

    @value.setter
    def value(self, v):
        CheckBase.value.fset(self, v)

    @abstractmethod
    def get_current_version(self) -> t.Union[None, t.Tuple[int]]:
        """Get the current version as a tuple of integers, or None if it can't
        be found."""
        return None

    def check(self, level: int = 0) -> CheckResult:
        """Check whether the current version is compatible with the version
        specified in the value."""
        name, op, version = self.value
        current_version = self.get_current_version()
        passed = False

        if name is None:
            status = "missing"
        elif self.require_current_version and current_version is None:
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
                status = f"incorrect version=" f"{'.'.join(map(str, current_version))}"
            else:
                status = "passed"
                passed = True

        return CheckResult(
            passed=passed, msg=self.msg.format(check=self), status=status
        )
