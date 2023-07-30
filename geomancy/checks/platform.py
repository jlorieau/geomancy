"""
Checks the platform (Operating System) and its version
"""
import platform
import typing as t

from .base import CheckResult
from .version import CheckVersion
from .utils import version_to_tuple
from ..config import Parameter

__all__ = ("CheckPlatform",)


class CheckPlatform(CheckVersion):
    """Check the availability and version of a python package"""

    # The message for checking python packages
    msg = Parameter(
        "CHECKPLATFORM.MSG",
        default="Check platform '{check.raw_value}'...",
    )

    aliases = ("checkPlatform",)

    def get_current_platform(self) -> str:
        """Retrieve the OS platform name"""
        uname = platform.uname()

        if uname.system in ("Darwin",):
            return "macOS"
        elif uname.system in ("Linux",):
            return "Linux"
        elif uname.system in ("Microsoft", "Windows"):
            return "Windows"
        else:
            raise NotImplementedError

    def get_current_version(self) -> t.Union[None, t.Tuple[int]]:
        """Retrieve the OS current version"""
        uname = platform.uname()

        # Get the current OS version
        current_platform = self.get_current_platform()

        # This code follows 'platform.platform()' to some extent
        if current_platform == "macOS":
            release = platform.mac_ver()[0]
            return version_to_tuple(release) if release else None
        elif current_platform in ("Linux", "Windows"):
            return version_to_tuple(uname.release) if uname.release else None
        else:
            raise NotImplementedError

    def check(self, level: int = 0) -> CheckResult:
        """Check whether the OS matches and the version"""
        # Get the OS name checked against
        name, op, version = self.value
        current_platform = self.get_current_platform()

        if current_platform.lower() != name.lower():
            # Failed check if the platform doesn't match this check
            return CheckResult(passed=False, msg=self.msg, status="wrong platform")

        # Check the version, as usual
        return super().check(level=level)
