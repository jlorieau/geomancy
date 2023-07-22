"""
Checks for paths
"""
import typing as t
from pathlib import Path

from .base import CheckBase, CheckException
from ..config import Parameter
from ..cli import term


class CheckPath(CheckBase):
    """Check paths for valid files and directories"""

    # (Optional) the type of path expected
    path_type: t.Optional[str] = None

    # The valid values of path types
    path_type_options = (None, "dir", "file")

    # The message for checking environment variables
    msg = Parameter("CHECKPATH.MSG", default="Check path '{name}'...{status}.")

    # Alternative names for the class
    aliases = ("checkPath",)

    def __init__(self, *args, path_type: t.Optional[str] = None, **kwargs):
        super().__init__(*args, **kwargs)
        if path_type not in self.path_type_options:
            raise CheckException(
                f"Path type '{path_type}' must be one of: "
                f"{tuple(opt for opt in self.path_type_options if opt is not None)}"
            )
        self.path_type = path_type

    def check(self, level: int = 0) -> bool:
        """Check paths"""
        passed = False
        value = self.value
        path = Path(value)

        if not path.exists():
            status = "missing"
        elif self.path_type == "dir" and not path.is_dir():
            status = "not dir"
        elif self.path_type == "file" and not path.is_file():
            status = "not file"
        else:
            status = "passed"
            passed = True

        if passed:
            term.p_pass(self.msg.format(name=self.name, status=status), level=level)
        else:
            term.p_fail(self.msg.format(name=self.name, status=status), level=level)
        return passed
