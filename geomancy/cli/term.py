"""Messages for the command-line interface"""
import sys
import os

from ..config import Parameter

__all__ = ("term",)


class Term:
    """Terminal settings"""

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

    # Whether to use the level parameters to add spacing
    use_level = Parameter("TERM.USE_LEVEL", default=True)

    # Whether to use color
    use_color = Parameter("TERM.USE_COLOR", default=True)

    # Maximum allowed number of characters per line
    max_width = Parameter("TERM.MAX_WIDTH", default=80)

    @property
    def width(self):
        """The current width of the termina"""
        return os.get_terminal_size().columns

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

    def p_h1(self, msg: str, end: str = "\n", level: int = 0):
        """Print a heading (level 1)"""
        # Format the message
        term_width = min(self.width, self.max_width)
        msg = "{:=^{length}s}".format(" " + msg.strip() + " ", length=term_width)

        sys.stdout.write(f"{self.BOLD}{msg}{self.RESET}{end}")

    def p_bold(self, msg: str, end: str = "\n", level: int = 0):
        """Print a message in bold"""
        start = "  " * level if self.use_level else ""
        sys.stdout.write(f"{start}{self.BOLD}{msg.strip()}{self.RESET}{end}")

    def p_pass(self, msg: str, end: str = "\n", level: int = 0):
        """Print a message for a passed test"""
        start = "  " * level if self.use_level else ""
        sys.stdout.write(f"{start}{self.GREEN}✔ {msg.strip()}{self.RESET}{end}")

    def p_fail(self, msg: str, end: str = "\n", level: int = 0):
        """Print a message for a failed test"""
        start = "  " * level if self.use_level else ""
        sys.stderr.write(f"{start}{self.RED}✖ {msg.strip()}{self.RESET}{end}")

    def p_warn(self, msg: str, end: str = "\n", level: int = 0):
        """Print a message for a warning"""
        start = "  " * level if self.use_level else ""
        sys.stderr.write(f"{start}{self.YELLOW}! {msg.strip()}{self.RESET}{end}")


term = Term()
