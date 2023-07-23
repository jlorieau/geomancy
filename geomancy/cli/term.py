"""Terminal messages for the command-line interface"""
import typing as t
import sys
import os
import textwrap
from abc import ABC, abstractmethod

from ..config import Parameter, ConfigException

__all__ = ("Term",)


class Term(ABC):
    """Manage terminal settings and output"""

    # Default ANSI codes for color
    ansi_codes = {
        "RED": "\033[1;31m",
        "BLUE": "\033[1;34m",
        "CYAN": "\033[1;36m",
        "GREEN": "\033[0;32m",
        "YELLOW": "\033[1;33m",
        "MAGENTA": "\033[1;35m",
        "RESET": "\033[0;0m",
        "BOLD": "\033[;1m",
        "REVERSE": "\033[;7m",
    }

    # Other names for the concrete classes
    aliases: t.Tuple[str] = ()

    # Whether to use the level parameters to add spacing
    use_level = Parameter("TERM.USE_LEVEL", default=True)

    # Whether to use color
    use_color = Parameter("TERM.USE_COLOR", default=True)

    # Maximum allowed number of characters per line
    max_width = Parameter("TERM.MAX_WIDTH", default=None)

    # Default terminal to use
    default = Parameter("TERM.DEFAULT", default="full")

    @property
    def width(self):
        """The current width of the terminal"""
        try:
            return os.get_terminal_size().columns
        except OSError:
            return self.max_width or 80

    @property
    def RED(self):
        return self.ansi_codes["RED"] if self.use_color else ""

    @property
    def BLUE(self):
        return self.ansi_codes["BLUE"] if self.use_color else ""

    @property
    def CYAN(self):
        return self.ansi_codes["CYAN"] if self.use_color else ""

    @property
    def GREEN(self):
        return self.ansi_codes["GREEN"] if self.use_color else ""

    @property
    def YELLOW(self):
        return self.ansi_codes["YELLOW"] if self.use_color else ""

    @property
    def MAGENTA(self):
        return self.ansi_codes["MAGENTA"] if self.use_color else ""

    @property
    def RESET(self):
        return self.ansi_codes["RESET"] if self.use_color else ""

    @property
    def BOLD(self):
        return self.ansi_codes["BOLD"] if self.use_color else ""

    @property
    def REVERSE(self):
        return self.ansi_codes["REVERSE"] if self.use_color else ""

    @abstractmethod
    def p_h1(self, msg: str, status: str = "", end: str = "\n", level: int = 0) -> None:
        return None

    @abstractmethod
    def p_h2(self, msg: str, status: str = "", end: str = "\n", level: int = 0) -> None:
        return None

    @abstractmethod
    def p_pass(
        self, msg: str, status: str = "", end: str = "\n", level: int = 0
    ) -> None:
        return None

    @abstractmethod
    def p_fail(
        self, msg: str, status: str = "", end: str = "\n", level: int = 0
    ) -> None:
        return None

    @classmethod
    def get(cls):
        """Get the currently configured terminal"""
        term_subclasses = cls.__subclasses__()
        matching_term = [
            subclass for subclass in term_subclasses if cls.default in subclass.aliases
        ]
        if len(matching_term) == 0:
            raise ConfigException(
                f"Could not find a terminal with name '{cls.default}'"
            )
        else:
            subclass = matching_term[0]
            return subclass()


class FullTerm(Term):
    """A terminal within printing full information"""

    aliases = ("full", "Full", "FULL")

    def fmt(
        self,
        msg: str,
        status: str = "",
        start: str = "",
        end: str = "\n",
        level: int = 0,
        color: str = "",
    ):
        """Formats the text string as needed for messages"""
        # Substitute text without ANSI codes
        text = f"{msg}{status}"

        # Wrap string (without ANSI codes)
        # The first 4 characters are for the status checkbox from the start
        # string--e.g. "[✔] "
        start_len = len(start) + 3 if len(start) > 0 else 4

        # subsequent indenting comes from the level
        if self.use_level:
            level = level + 1
            initial_indent = " " * (2 * level - start_len)
            subsequent_indent = " " * 2 * level
        else:
            initial_indent = ""
            subsequent_indent = " " * start_len

        # Wrap the text without ANSI codes
        text_lines = textwrap.wrap(
            text,
            initial_indent=initial_indent,
            subsequent_indent=subsequent_indent,
            tabsize=4,
        )
        text = "\n".join(text_lines)

        # Add the ANSI codes to the wrapped string
        if self.use_color:
            # Replace the colored status at the end
            status_len = len(status)
            text = (
                f"{text[:-status_len]}{color}{status}{self.RESET}"
                if status_len > 0
                else f"{text}{color}{self.RESET}"
            )

            # Add the colored start
            text = f"[{color}{start}{self.RESET}] {text}{end}"

        else:
            text = f"[{start}] {text}{end}"

        # Color the status
        return text

    def p_h1(self, msg: str, status: str = "", end: str = "\n", level: int = 0):
        """Print a heading (level 1)"""
        # Format the message
        if self.max_width is not None:
            term_width = min(self.width, self.max_width)
        else:
            term_width = self.width
        msg = "{:=^{length}s}".format(" " + msg.strip() + " ", length=term_width)

        sys.stdout.write(f"{self.BOLD}{msg}{self.RESET}{end}")

    def p_h2(self, msg: str, status: str = "", end: str = "\n", level: int = 0):
        """Print a heading (level 1)"""
        sys.stdout.write(self.fmt(msg, status, "✔", end, level, self.BOLD))

    def p_bold(self, msg: str, status: str = "", end: str = "\n", level: int = 0):
        """Print a message in bold"""
        sys.stdout.write(self.fmt(msg, status, "✔", end, level, self.BOLD))

    def p_pass(self, msg: str, status: str = "", end: str = "\n", level: int = 0):
        """Print a message for a passed test"""
        sys.stdout.write(self.fmt(msg, status, "✔", end, level, self.GREEN))

    def p_fail(self, msg: str, status: str = "", end: str = "\n", level: int = 0):
        """Print a message for a failed test"""
        sys.stdout.write(self.fmt(msg, status, "✖", end, level, self.RED))

    def p_warn(self, msg: str, status: str = "", end: str = "\n", level: int = 0):
        """Print a message for a warning"""
        sys.stdout.write(self.fmt(msg, status, "!", end, level, self.YELLOW))
