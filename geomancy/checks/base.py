"""
Abstract base class for checks
"""
import typing as t
from collections import namedtuple
from time import process_time

from .utils import sub_env
from ..config import Parameter
from ..cli import Term

__all__ = ("CheckBase", "CheckException")


class CheckException(Exception):
    """Exception raised when an error is encountered in the setup of a check."""


# Storage class for the results of checks
CheckResult = namedtuple("CheckResult", "passed msg status", defaults=("", ""))


class CheckBase:
    """Check base class and grouper"""

    # Value for the check to check
    _value: str

    # Description of the check
    desc: str = ""

    # The message to print during the check.
    msg: str = "{self.name}"

    # A list of sub checks
    sub_checks: t.List["CheckBase"]

    # Alternative names for the class
    aliases: t.Optional[t.Tuple[str, ...]] = None

    # The check (and sub-checks) are enabled
    enabled: bool = True

    # If True (default), environment variables in variable_name or
    # variable_value are substituted with the values of other environment
    # variables.
    env_substitute: bool

    # The condition for sub-check results to be considered a pass
    condition: t.Callable = all

    # The default value for env_substitute
    env_substitute_default = Parameter("CHECKBASE.ENV_SUBSTITUTE_DEFAULT", default=True)

    # The maximum recursion depth of the load function
    max_level = Parameter("CHECKBASE.MAX_LEVEL", default=10)

    def __init__(
        self,
        name: str,
        value: t.Optional[str] = None,
        desc: str = "",
        condition: t.Optional[str] = None,
        env_substitute: t.Optional[bool] = None,
        sub_checks: t.Optional[list["CheckBase", ...]] = None,
    ):
        self.name = name
        self.value = value
        self.desc = desc
        self.env_substitute = (
            env_substitute
            if env_substitute is not None
            else self.env_substitute_default
        )
        self.sub_checks = list(sub_checks) if sub_checks is not None else []

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
        msg = "All sub-checks should be instances of CheckBase"
        assert all(isinstance(sc, CheckBase) for sc in self.sub_checks), msg

    def __repr__(self):
        return f"{self.__class__.__name__}({self.name})"

    def __len__(self):
        """The number of sub-checks"""
        return len(self.sub_checks)

    @property
    def count(self, all: bool = True) -> int:
        """The number of sub-checks

        Parameters
        ----------
        all
            If True, count all the immediate and nested level sub-checks.
            If False, only count the immediate level sub-checks.
        """
        # flatten() returns this check, so the count is subtracted by 1 to only
        # count sub-checks
        return len(self.flatten()) - 1 if all else len(self.sub_checks)

    @property
    def value(self) -> t.Any:
        """Check's value with optional environment substitution"""
        if self.env_substitute and self._value is not None:
            subbed = sub_env(self._value)
            return subbed if subbed is not None else self._value
        else:
            return self._value

    @value.setter
    def value(self, v):
        self._value = str(v) if v is not None else None

    @property
    def is_collection(self) -> bool:
        """Evaluate whether this is a collection check--i.e. it's only a check that
        holds other check groups (BaseCheck instances).

        Collection checks have headings that are printed before the results of the
        sub-checks are evaluated.
        """
        collection_clses = (CheckBase,)
        return self.__class__ in collection_clses and all(
            sub.__class__ in (CheckBase,) for sub in self.sub_checks
        )

    def check(self, level: int = 0) -> CheckResult:
        """Performs the checks and sub-checks.

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
        msg = self.msg.format(self=self)
        start_time = None
        if level == 0:
            # Top level heading
            term.p_h1(msg=msg, level=level)
            start_time = process_time()
        elif self.is_collection:
            # Collection checks print right away since we don't need to wait to
            # see the results of "check" for sub_checks
            term.p_h2(
                msg=msg,
                level=level,
                status=f" ({self.count} checks)",
                color_status=term.RESET,
            )

        # Run all sub-checks
        results = []
        for sub_check in self.sub_checks:
            result = sub_check.check(level=level + 1)
            results.append(result)

        # Determine if this check passed based on the condition
        passed = self.condition(result.passed for result in results)

        # Print this check's results
        if passed and not self.is_collection:
            term.p_pass(
                msg=msg,
                level=level,
                color_msg=term.BOLD,
                status=f" ({self.count} checks)",
                color_status=term.RESET,
            )
        elif not passed and not self.is_collection:
            term.p_fail(
                msg=msg,
                level=level,
                color_msg=term.BOLD,
                status=f" ({self.count} checks)",
                color_status=term.RESET,
            )

        for result in results:
            if result.msg == "":
                # This result has already been handled and printed
                continue
            elif result.passed:
                term.p_pass(msg=result.msg, status=result.status, level=level + 1)
            elif passed:
                # If the sub-check failed but this check passed, then it's a
                # warning.
                term.p_warn(msg=result.msg, status=result.status, level=level + 1)
            else:
                # If the sub-check failed and this check failed, then it's a fail.
                term.p_fail(msg=result.msg, status=result.status, level=level + 1)

        # Print terminal information if this is the root check
        if level == 0:
            msg = f"{self.count} checks {'passed' if passed else 'failed'}"

            # Add timing info, if available
            if start_time is not None:
                total_time = process_time() - start_time
                msg += f" in {total_time:.2f}s"

            # Determine the message color
            color_msg = term.BOLD + term.GREEN if passed else term.BOLD + term.RED

            # Print the message
            term.p_h1(msg, color_msg=color_msg)

        return CheckResult(passed=passed, msg="", status="")

    def flatten(self) -> t.List["CheckBase"]:
        """Return a flattened list of this check (first item) and all
        sub checks."""
        flattened = [self]
        for sub_check in self.sub_checks:
            flattened += sub_check.flatten()
        return flattened

    @classmethod
    def types_dict(cls) -> t.Dict[str, type]:
        """Return all the types and subtypes of Checks in a dict."""
        # Retrieve the base class (BaseCheck) and subclasses
        cls_types = [cls] + cls.__subclasses__()

        # Create a dict with the class name string (key) and the class type
        # (value)
        d = dict()
        for cls_type in cls_types:
            # Add the class name directly
            d[cls_type.__name__] = cls_type

            # Add class name aliases
            aliases = cls_type.aliases if cls_type.aliases is not None else ()
            for alias in aliases:
                # Aliases should not create name collisions
                assert alias not in d, f"Duplicate alias name '{alias}'"

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

        # Otherwise, try parsing the sub_checks
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

        # No sub-checks found; nothing else to do
        if len(found_checks) == 0:
            return None

        # Create a check grouping, first, by parsing the other arguments
        return CheckBase(name=name, sub_checks=found_checks, **other_d)
