"""Messages for the command-line interface"""
import sys
import os
import textwrap

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

    # Exit the program when encountering a fail
    exit_on_fail = Parameter("TERM.EXIT_ON_FAIL", default=True)

    # Maximum allowed number of characters per line
    max_width = Parameter("TERM.MAX_WIDTH", default=80)

    @property
    def width(self):
        """The current width of the terminal"""
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

    def fmt(self, text: str, color: str, end: str = "\n", level: int = 0):
        """Formats the text string as needed for messages"""
        text_lines = textwrap.wrap(
            f"{text}{end}",
            initial_indent=" " * 2 * level if self.use_level else "",
            subsequent_indent=" " * 4 * level if self.use_level else " " * 2,
            tabsize=4,
        )
        text = "\n".join(text_lines)
        return f"{color}{text}{self.RESET}{end}"

    def p_h1(self, msg: str, end: str = "\n", level: int = 0):
        """Print a heading (level 1)"""
        # Format the message
        term_width = min(self.width, self.max_width)
        msg = "{:=^{length}s}".format(" " + msg.strip() + " ", length=term_width)

        sys.stdout.write(f"{self.BOLD}{msg}{self.RESET}{end}")

    def p_bold(self, msg: str, end: str = "\n", level: int = 0):
        """Print a message in bold"""
        sys.stdout.write(self.fmt(msg, self.BOLD, end, level))

    def p_pass(self, msg: str, end: str = "\n", level: int = 0):
        """Print a message for a passed test"""
        sys.stdout.write(self.fmt(f"✔ {msg}", self.GREEN, end, level))

    def p_fail(self, msg: str, end: str = "\n", level: int = 0):
        """Print a message for a failed test"""
        sys.stderr.write(self.fmt(f"✖ {msg}", self.RED, end, level))
        if self.exit_on_fail:
            exit(1)

    def p_warn(self, msg: str, end: str = "\n", level: int = 0):
        """Print a message for a warning"""
        sys.stderr.write(self.fmt(f"! {msg}", self.YELLOW, end, level))


term = Term()
