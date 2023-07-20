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

    # A list of sub checks
    sub_checks: list

    def __init__(self,
                 name: str,
                 value: t.Any,
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
        self.sub_checks = list(sub_checks)

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

    @classmethod
    def types_dict(cls) -> t.Dict[str, type]:
        """Return all the types and subtypes of Checks in a dict."""
        types = [cls] + cls.__subclasses__()
        return {c.__name__:c for c in types}
