"""
Abstract base class for checks
"""
import typing as t

__all__ = ('CheckBase',)


class CheckBase:
    """Check base class and grouper"""

    # Name of the check
    name: str

    # Value for the check to check
    value: t.Any

    # Description of the check
    desc: str = ''

    # The check (and sub-checks) are enabled
    enabled: bool = True

    # The message to print during the check. {STATUS} is substituted
    msg: str = ''

    # Alternative names for the class
    aliases: t.Optional[t.Tuple[str, ...]] = None

    # A list of sub checks
    sub_checks: list

    def __init__(self,
                 name: str,
                 value: t.Any = None,
                 desc: str = '',
                 sub_checks: t.Optional[list['CheckBase', ...]] = None):
        # Make sure the sub_checks are checks
        if sub_checks is not None:
            msg = "All sub-checkers must be instances of CheckBase"
            assert all(isinstance(check, CheckBase)
                       for check in sub_checks), msg
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

    def check(self) -> bool:
        """Performs the checks and sub-checks.

        Returns
        -------
        passed
            True if the check and all sub-checks passed
            False if the check or any sub-checked failed
        """
        # Run all subchecks
        return all(sub.check() for sub in self.sub_checks)

    def flatten(self) -> t.List['CheckBase']:
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
