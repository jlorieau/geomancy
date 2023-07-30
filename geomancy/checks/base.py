"""
Abstract base class for checks
"""
import typing as t
from abc import ABC
from inspect import isabstract
from collections import namedtuple
from time import process_time

from .utils import all_subclasses, pop_first
from ..config import Parameter
from ..environment import sub_env
from ..cli import Term

__all__ = ("CheckBase", "CheckException", "CheckResult")


class CheckException(Exception):
    """Exception raised when an error is encountered in the setup of a check."""


# Storage class for the results of checks
CheckResult = namedtuple("CheckResult", "passed msg status", defaults=("", ""))


class CheckBase(ABC):
    """Check base class and grouper

    .. versionchanged:: 0.9.3
        Switch to :meth:`environment.sub_env` for value substitutions, which
        require a '$' character  and allow different expansion rules like
        defaults, errors and replacements.
    """

    # Unprocessed value for the check
    raw_value: str

    # Description of the check
    desc: str = ""

    # The message to print during the check.
    msg: str = "{check.name}"

    # A list of children checks
    children: t.List["CheckBase"]

    # Alternative names for the class
    aliases: t.Optional[t.Tuple[str, ...]] = None

    # This check (and children) are enabled
    enabled: bool = True

    # If True (default), environment variables in variable_name or
    # variable_value are substituted with the values of other environment
    # variables.
    env_substitute: bool

    # The condition for children results to be considered a pass
    condition: t.Callable = all
    condition_aliases = ("subchecks", "condition")  # other names for variable

    # The default value for env_substitute
    env_substitute_default = Parameter("CHECKBASE.ENV_SUBSTITUTE_DEFAULT", default=True)

    # Alternative parameter names for env_substitute
    env_substitute_aliases = ("substitute", "env_substitute")

    # The maximum recursion depth of the load function
    max_level = Parameter("CHECKBASE.MAX_LEVEL", default=10)

    def __init__(
        self,
        name: str,
        value: t.Optional[str] = None,
        desc: str = "",
        children: t.Optional[list["CheckBase", ...]] = None,
        **kwargs,
    ):
        self.name = name
        self.value = value
        self.desc = desc
        self.children = list(children) if children is not None else []

        # Parse kwargs, which may use different aliases
        condition = pop_first(kwargs, *self.condition_aliases, default=None)
        self.env_substitute = pop_first(
            kwargs, *self.env_substitute_aliases, default=self.env_substitute_default
        )

        # Make sure the condition values are allowed
        if condition is None:
            pass
        elif condition in ("all", "All", "ALL"):
            self.condition = all
        elif condition in ("any", "Any", "ANY"):
            self.condition = any
        else:
            raise CheckException(
                f"The condition '{condition}' should be either 'all' or 'any'."
            )

        # Check attributes
        msg = "All children should be instances of CheckBase"
        assert all(isinstance(sc, CheckBase) for sc in self.children), msg

    def __repr__(self):
        return f"{self.__class__.__name__}({self.name})"

    def __len__(self):
        """The number of children"""
        return len(self.children)

    @property
    def value(self) -> t.Any:
        """Check's value with optional environment substitution"""
        if self.env_substitute and self.raw_value is not None:
            subbed = sub_env(self.raw_value)
            return subbed if subbed is not None else self.raw_value
        else:
            return self.raw_value

    @value.setter
    def value(self, v):
        self.raw_value = str(v) if v is not None else None

    @property
    def count(self, all: bool = True) -> int:
        """The number of children

        Parameters
        ----------
        all
            If True, count all the immediate and nested level children.
            If False, only count the immediate level children.
        """
        # flatten() returns this check, so the count is subtracted by 1 to only
        # count sub-checks
        return len(self.flatten()) - 1 if all else len(self.children)

    @property
    def is_collection(self) -> bool:
        """Evaluate whether this is a collection check--i.e. it's only a
        check that holds other check groups (BaseCheck instances).

        Collection checks have headings that are printed before the results of
        the children are evaluated.
        """
        collection_clses = (CheckBase,)
        return self.__class__ in collection_clses and all(
            child.__class__ in (CheckBase,) for child in self.children
        )

    def check(self, level: int = 0) -> CheckResult:
        """Performs the checks of this check and of children.

        Parameters
        ----------
        level
            The current depth level of the check

        Returns
        -------
        result
            The result of the check
        """
        term = Term.get()

        # Print a heading and start timer
        msg = self.msg.format(check=self)
        start_time = None
        if level == 0:
            # Top level heading
            term.p_h1(msg=msg, level=level)
            start_time = process_time()
        elif self.is_collection:
            # Collection checks print right away since we don't need to wait to
            # see the results of "check" for children
            term.p_h2(
                msg=msg,
                level=level,
                status=f" ({self.count} checks)",
                style_status={"reset": True},
            )

        # Run all children checks
        results = []
        for child in self.children:
            result = child.check(level=level + 1)
            results.append(result)

        # Determine if this check passed based on the condition
        passed = self.condition(result.passed for result in results)

        # Print this check's results
        if passed and not self.is_collection:
            term.p_pass(
                msg=msg,
                level=level,
                status=f" ({self.count} checks)",
                style_status={"reset": True},
                style_msg={"bold": True},
            )
        elif not passed and not self.is_collection:
            term.p_fail(
                msg=msg,
                level=level,
                status=f" ({self.count} checks)",
                style_status={"reset": True},
                style_msg={"bold": True},
            )

        for result in results:
            if result.msg == "":
                # This result has already been handled and printed
                continue
            elif result.passed:
                term.p_pass(msg=result.msg, status=result.status, level=level + 1)
            elif passed:
                # If the child check failed but this check passed, then it's a
                # warning
                term.p_warn(msg=result.msg, status=result.status, level=level + 1)
            else:
                # If the child check failed and this check failed, then it's a
                # fail
                term.p_fail(msg=result.msg, status=result.status, level=level + 1)

        # Print terminal information if this is the root check
        if level == 0:
            msg = f"{'PASSED' if passed else 'FAILED'}. {self.count} checks"

            # Add timing info, if available
            if start_time is not None:
                total_time = process_time() - start_time
                msg += f" in {total_time:.2f}s"

            # Determine the message color
            style_msg = {"bold": True}
            style_msg["fg"] = "green" if passed else "red"

            # Print the message
            term.p_h1(msg, style_msg=style_msg)

        return CheckResult(passed=passed, msg="", status="")

    def flatten(self) -> t.List["CheckBase"]:
        """Return a flattened list of this check (first item) and children
        checks"""
        flattened = [self]
        for child in self.children:
            flattened += child.flatten()
        return flattened

    @classmethod
    def types_dict(cls) -> t.Dict[str, t.Type]:
        """Return all the instantiatable CheckBase types in a dict."""
        # Retrieve the base class (BaseCheck) and children classes
        cls_types = [cls] + list(all_subclasses(cls))

        # Create a dict with the class name string (key) and the class type
        # (value)
        d = dict()
        for cls_type in cls_types:
            # Skip abstract classes, which can't be instantiated
            if isabstract(cls_type):
                continue

            # Make sure class name isn't alreay in the dict
            assert (
                cls_type.__name__ not in d
            ), f"class {cls_type.__name__} already registered class"

            # Add the class name directly
            d[cls_type.__name__] = cls_type

            # Add class name aliases
            aliases = cls_type.aliases if cls_type.aliases is not None else ()
            for alias in aliases:
                # Aliases should not create name collisions
                assert alias not in d, f"Duplicate alias name '{alias}'"

                # Make sure the alias doesn't match a class that's already
                # registered
                assert (
                    alias not in d
                ), f"Alias {alias} already matches a registered class"

                # Add alias
                d[alias] = cls_type
        return d

    @classmethod
    def load(
        cls, d: dict, name: str, level: int = 1, max_level: t.Optional[int] = None
    ) -> t.Union["CheckBase", None]:
        """Load checks from a dict.

        Parameters
        ----------
        d
            The dict with checks to load
        name
            The name of the returned check instance
        level
            The current recursion depth of this load
        max_level
            The maximum recursion depth allowed

        Returns
        -------
        root_check
            The loaded root CheckBase instance
        """
        # Check that the maximum recursion level hasn't been reached
        max_level = max_level if max_level is not None else cls.max_level

        if level >= max_level:
            msg = f"Parsing level {level} exceed the maximum level of {max_level}"
            raise NotImplementedError(msg)

        # Get a listing of the available Check types
        check_types = cls.types_dict()

        # See if the dict has keys that reference Check types
        matching_keys = [k for k in d.keys() if k in check_types]

        if len(matching_keys) > 1:
            msg = f"More than 1 check type specified: {matching_keys}"
            raise NotImplementedError(msg)

        # Parse the check if a single check was given
        if len(matching_keys) == 1:
            # Get the check class
            check_type = matching_keys[0]
            matching_cls = check_types[check_type]

            # Get the value for the check
            value = d[check_type]

            # Get the other kwargs
            kwargs = {k: v for k, v in d.items() if k != check_type}

            # Create and return the check_type
            return matching_cls(name, value, **kwargs)

        # Otherwise, try parsing the children
        items = d.items()
        found_checks = []  # Values parsed into CheckBase objects
        other_d = dict()  # All other values
        for key, value in items:
            if not isinstance(value, dict):
                other_d[key] = value
                continue

            return_value = cls.load(
                d=value, name=key, level=level + 1, max_level=max_level
            )

            # Replace the value withe CheckBase instance, if it was parsed correctly
            # Otherwise, just place it in the parsed_dict.
            if isinstance(return_value, CheckBase):
                found_checks.append(return_value)
            else:
                other_d[key] = value

        # No child checks found; nothing else to do
        if len(found_checks) == 0:
            return None

        # Create a check grouping, first, by parsing the other arguments
        return CheckBase(name=name, children=found_checks, **other_d)
