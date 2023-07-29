"""Terminal messages for the command-line interface"""
import typing as t
import os
import textwrap
from types import MappingProxyType
from abc import ABC, abstractmethod

from click import echo, style

from ..config import Parameter, ConfigException

__all__ = ("Term",)


class Term(ABC):
    """Manage terminal settings and output"""

    # Other names for the concrete classes
    aliases: t.Tuple[str] = ()

    # Default formatting options to append to a
    format_kwargs = MappingProxyType({"level": 0})

    # Whether to use the level parameters to add spacing
    use_level = Parameter("TERM.USE_LEVEL", default=True)

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
            "style_check": (),  # Style dict tuple or dict for 'check' character
            "style_msg": (),  # Style dict tuple or dict for 'msg'
            "style_status": (),  # Style dict tuple or dict for 'status'
            "level": 0,  # Indentation level of the statement
        }
    )

    def fmt(self, msg: str, **kwargs):
        """Formats the text string as needed for messages"""
        status = kwargs.get("status", self.format_kwargs["status"])
        check = kwargs.get("check", self.format_kwargs["check"])
        style_check = kwargs.get("style_check", dict(self.format_kwargs["style_check"]))
        style_msg = kwargs.get("style_msg", dict(self.format_kwargs["style_msg"]))
        style_status = kwargs.get(
            "style_status", dict(self.format_kwargs["style_status"])
        )
        level = kwargs.get("level", self.format_kwargs["level"])

        # The first 4 characters are for the status checkbox--e.g. "[✔] "
        check_len = len(check) + 3 if len(check) > 0 else 4

        # subsequent indenting comes from the level
        if self.use_level:
            level = level + 1
            indent = " " * (2 * level - check_len)
        else:
            indent = ""

        # Add indent, colored start, color msg and colored status
        check_str = f"[{style(check, **style_check)}]" if check else "    "
        text = (
            f"{check_str}"
            f"{indent}"
            f"{style(msg, **style_msg)}"
            f"{style(status, **style_status)}"
        )

        return text

    def p_h1(self, msg: str, nl: bool = True, **kwargs):
        """Print a heading (level 1)"""
        style_msg = kwargs.get("style_msg", {"bold": True})

        # Format the message
        if self.max_width is not None:
            term_width = min(self.width, self.max_width)
        else:
            term_width = self.width
        msg = "{:=^{length}s}".format(" " + msg.strip() + " ", length=term_width)

        echo(f"{style(msg, **style_msg)}", nl=nl)

    def p_h2(self, msg: str, nl: bool = True, **kwargs):
        kwargs.setdefault("style_msg", {"bold": True})
        kwargs.setdefault("check", {})
        echo(self.fmt(msg, **kwargs), nl=nl)

    def p_pass(self, msg: str, nl: bool = True, **kwargs):
        kwargs.setdefault("style_check", {"fg": "green"})
        kwargs.setdefault("style_status", {"fg": "green"})
        kwargs.setdefault("check", "✔")
        echo(self.fmt(msg, **kwargs), nl=nl)

    def p_fail(self, msg: str, nl: bool = True, **kwargs):
        kwargs.setdefault("style_check", {"fg": "red"})
        kwargs.setdefault("style_status", {"fg": "red"})
        kwargs.setdefault("check", "✖")
        echo(self.fmt(msg, **kwargs), nl=nl)

    def p_warn(self, msg: str, nl: bool = True, **kwargs):
        """Print a message for a warning"""
        kwargs.setdefault("style_check", {"fg": "yellow"})
        kwargs.setdefault("style_status", {"fg": "yellow"})
        kwargs.setdefault("check", "!")
        echo(self.fmt(msg, **kwargs), nl=nl)
