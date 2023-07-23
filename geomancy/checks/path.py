"""
Checks for paths
"""
import typing as t
from pathlib import Path

from .base import CheckBase, CheckException, CheckResult
from ..config import Parameter


class CheckPath(CheckBase):
    """Check paths for valid files and directories"""

    # (Optional) the type of path expected
    type: t.Optional[str] = None

    # The valid values of path types
    type_options = (None, "dir", "file")

    # The message for checking environment variables
    msg = Parameter("CHECKPATH.MSG", default="Check path '{check.value}'...")

    # Alternative names for the class
    aliases = ("checkPath",)

    def __init__(self, *args, type: t.Optional[str] = None, **kwargs):
        super().__init__(*args, **kwargs)
        if type not in self.type_options:
            raise CheckException(
                f"Path type '{type}' must be one of: "
                f"{tuple(opt for opt in self.type_options if opt is not None)}"
            )
        self.type = type

    def check(self, level: int = 0) -> CheckResult:
        """Check paths"""
        passed = False
        value = self.value
        path = Path(value)

        if not path.exists():
            status = "missing"
        elif self.type == "dir" and not path.is_dir():
            status = "not dir"
        elif self.type == "file" and not path.is_file():
            status = "not file"
        else:
            status = "passed"
            passed = True

        msg = self.msg.format(check=self, status=status)
        return CheckResult(passed=passed, msg=msg, status=status)
