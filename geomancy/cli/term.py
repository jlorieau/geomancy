"""Terminal messages for the command-line interface"""
import typing as t
import sys
import os
import textwrap
from types import MappingProxyType
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

    # Default formatting options to append to a
    format_kwargs = MappingProxyType({"end": "\n", "color": 0, "level": 0})

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
    def p_h1(self, msg: str, **kwargs) -> None:
        """Print a heading (level 1)

        Parameters
        ----------
        msg
            The message to print
        kwargs
            Options in formatting the printout. Options must be kwargs.
            See :attr:`format_kwargs`
        """
        return None

    @abstractmethod
    def p_h2(self, msg: str, **kwargs) -> None:
        """Print a heading (level 2)

        Parameters
        ----------
        msg
            The message to print
        kwargs
            Options in formatting the printout. Options must be kwargs.
            See :attr:`format_kwargs`
        """
        return None

    @abstractmethod
    def p_pass(self, msg: str, **kwargs) -> None:
        """Print a passed check message

        Parameters
        ----------
        msg
            The message to print
        kwargs
            Options in formatting the printout. Options must be kwargs.
            See :attr:`format_kwargs`
        """
        return None

    @abstractmethod
    def p_fail(self, msg: str, **kwargs) -> None:
        """Print a failed check messagd

        Parameters
        ----------
        msg
            The message to print
        kwargs
            Options in formatting the printout. Options must be kwargs.
            See :attr:`format_kwargs`
        """
        return None

    @abstractmethod
    def p_warn(self, msg: str, **kwargs) -> None:
        """Print a warned check messagd

        Parameters
        ----------
        msg
            The message to print
        kwargs
            Options in formatting the printout. Options must be kwargs.
            See :attr:`format_kwargs`
        """
        return None

    @classmethod
    def get(cls) -> "Term":
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

    format_kwargs = MappingProxyType(
        {
            "status": "",  # Status string. e.g. "passed"
            "check": "✔",  # Use this character for the check. e.g. ""
            "end": "\n",  # Terminate the message with this character
            "color_check": "",  # Color to use for the check
            "color_msg": "",  # Color to use for the message
            "color_status": "",  # Color to use for status message
            "level": 0,  # Indentation level of the statement
        }
    )

    def fmt(self, msg: str, **kwargs):
        """Formats the text string as needed for messages"""
        status = kwargs.get("status", self.format_kwargs["status"])
        check = kwargs.get("check", self.format_kwargs["check"])
        end = kwargs.get("end", self.format_kwargs["end"])
        color_check = kwargs.get("color_check", self.format_kwargs["color_check"])
        color_msg = kwargs.get("color_msg", self.format_kwargs["color_msg"])
        color_status = kwargs.get("color_status", self.format_kwargs["color_status"])
        level = kwargs.get("level", self.format_kwargs["level"])

        # Substitute text without ANSI codes
        text = f"{msg}{status}"

        # Wrap string (without ANSI codes)
        # The first 4 characters are for the status checkbox--e.g. "[✔] "
        check_len = len(check) + 3 if len(check) > 0 else 4

        # subsequent indenting comes from the level
        if self.use_level:
            level = level + 1
            initial_indent = " " * (2 * level - check_len)
            subsequent_indent = " " * 2 * level
        else:
            initial_indent = ""
            subsequent_indent = " " * check_len

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
                f"{text[:-status_len]}{color_status}{status}{self.RESET}"
                if status_len > 0
                else f"{text}{color_status}{self.RESET}"
            )

            # Add the colored start
            check_str = f"[{color_check}{check}{self.RESET}] " if check else "    "
            text = f"{check_str}{color_msg}{text}{self.RESET}{end}"

        else:
            check_str = f"[{check}] " if check else "    "
            text = f"{check_str}{text}{end}"

        # Color the status
        return text

    def p_h1(self, msg: str, **kwargs):
        """Print a heading (level 1)"""
        end = kwargs.get("end", self.format_kwargs["end"])

        # Format the message
        if self.max_width is not None:
            term_width = min(self.width, self.max_width)
        else:
            term_width = self.width
        msg = "{:=^{length}s}".format(" " + msg.strip() + " ", length=term_width)

        sys.stdout.write(f"{self.BOLD}{msg}{self.RESET}{end}")

    def p_h2(self, msg: str, **kwargs):
        fmt = self.format_kwargs
        kwargs.setdefault("color_msg", self.BOLD)
        kwargs.setdefault("check", "")
        sys.stdout.write(self.fmt(msg, **kwargs))

    def p_pass(self, msg: str, **kwargs):
        fmt = self.format_kwargs
        kwargs.setdefault("color_check", self.GREEN)
        kwargs.setdefault("color_status", self.GREEN)
        kwargs.setdefault("check", "✔")
        sys.stdout.write(self.fmt(msg, **kwargs))

    def p_fail(self, msg: str, **kwargs):
        fmt = self.format_kwargs
        kwargs.setdefault("color_check", self.RED)
        kwargs.setdefault("color_status", self.RED)
        kwargs.setdefault("check", "✖")
        sys.stdout.write(self.fmt(msg, **kwargs))

    def p_warn(self, msg: str, **kwargs):
        """Print a message for a warning"""
        fmt = self.format_kwargs
        kwargs.setdefault("color_check", self.YELLOW)
        kwargs.setdefault("color_status", self.YELLOW)
        kwargs.setdefault("check", "!")
        sys.stdout.write(self.fmt(msg, **kwargs))
