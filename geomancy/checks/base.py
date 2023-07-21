"""
Abstract base class for checks
"""
import typing as t

from ..config import Parameter
from ..cli import term

__all__ = ("CheckBase",)


class CheckBase:
    """Check base class and grouper"""

    # Name of the check
    name: str

    # Value for the check to check
    value: t.Any

    # Description of the check
    desc: str = ""

    # The check (and sub-checks) are enabled
    enabled: bool = True

    # The message to print during the check. {STATUS} is substituted
    msg: str = ""

    # Alternative names for the class
    aliases: t.Optional[t.Tuple[str, ...]] = None

    # A list of sub checks
    sub_checks: list

    # The maximum recursion depth of the load function
    max_level = Parameter("CHECKBASE.MAX_LEVEL", default=10)

    # Whether to print headings for every CheckBase
    print_heading = Parameter("CHECKBASE.PRINT_HEADING", default=True)

    def __init__(
        self,
        name: str,
        value: t.Any = None,
        desc: str = "",
        sub_checks: t.Optional[list["CheckBase", ...]] = None,
    ):
        # Make sure the sub_checks are checks
        if sub_checks is not None:
            msg = "All sub-checkers must be instances of CheckBase"
            assert all(isinstance(check, CheckBase) for check in sub_checks), msg
        else:
            sub_checks = []

        # Set attributes
        self.name = name
        self.value = value
        self.desc = desc
        self.sub_checks = list(sub_checks) if sub_checks is not None else []

        # Check attributes
        msg = "All sub-checks should be instances of CheckBase"
        assert all(isinstance(sc, CheckBase) for sc in self.sub_checks), msg

    def __repr__(self):
        return f"{self.__class__.__name__}({self.name})"

    def check(self, level: int = 0) -> bool:
        """Performs the checks and sub-checks.

        Parameters
        ----------
        level
            The current depth level of the check

        Returns
        -------
        passed
            True if the check and all sub-checks passed
            False if the check or any sub-checked failed
        """
        # Print a heading
        if self.print_heading:
            if level == 0:
                # Top level heading
                term.p_h1(self.name, level=level)
            else:
                term.p_bold(self.name, level=level)

        # Run all subchecks
        return all(sub.check(level=level + 1) for sub in self.sub_checks)

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
