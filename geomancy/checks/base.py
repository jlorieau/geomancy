"""
Abstract base class for checks
"""
import typing as t
import importlib
from concurrent.futures import Future, Executor
from types import ModuleType
from inspect import isabstract
from dataclasses import dataclass, field

from rich.table import Table
from rich.padding import Padding

from .utils import pop_first, all_subclasses
from ..config import Parameter
from ..environment import sub_env

__all__ = ("Check", "CheckException", "Result")


class CheckException(Exception):
    """Exception raised when an error is encountered in the setup of a check."""


@dataclass(slots=True)
class Result:
    """A Check's result with awareness of concurrent.futures and rich
    functionality"""

    #: Result's status--e.g. 'passed', 'failed', 'not found'
    #: Only a 'passed' status is considered a passed result
    status: str = "pending"

    #: Result message used when displaying the result
    msg: str = ""

    #: The pass condition for children checks and their passed property values
    condition: t.Callable = all

    #: The flat list of Results or Futures from children checks
    children: t.List[t.Union["Result", t.Awaitable["Result"]]] = field(
        default_factory=list
    )

    @property
    def passed(self) -> bool:
        """Whether the check that generated this result passed.

        Notes
        -----
        This function checks whether children results have passed, whether this
        result has a non-pending status, and it updates "pending" status when
        the children are done
        """
        # Determine whether the children have finished
        done = True  # updated by loop below

        # Get the pass conditions for children. This list should only comprise
        # bools (True/False)
        children_passed = []
        for child in self.children:
            if isinstance(child, Result):
                # The child is a Result object
                child_status = child.status == "passed"
                children_passed.append(child_status)
            elif isinstance(child, Future) and child.done():
                # The child is a future with a result
                result = child.result()
                child_status = result.status == "passed"
                children_passed.append(child_status)
            else:
                # The child is a future that isn't done evaluating
                done = False
                children_passed.append(False)

        # Update the status from "pending" if this result is done (finished)
        if self.status.lower() == "pending" and done:
            self.status = "passed" if self.condition(children_passed) else "failed"

        # Only a 'passed' status is considered a passed result
        return self.status.lower() == "passed"

    @property
    def done(self) -> bool:
        """Whether the check that generated this result and children checks are
        done"""
        # Get the done status for children. This list should only comprise
        # bools (True/False)
        children_done = []
        for child in self.children:
            if isinstance(child, Result):
                # The child is a Result object
                child_done = child.done  # This function
                children_done.append(child_done)
            elif isinstance(child, Future) and child.done():
                # The child is a future with a result
                result = child.result()
                child_done = result.done  # This function
                children_done.append(child_done)
            else:
                children_done.append(False)

        if all(children_done) and self.status.lower() != "pending":
            # All children are done and this result has a non-pending status
            return True
        elif all(children_done) and self.status.lower() == "pending":
            # All the children are done and this result's pending. This result's
            # status can be updated/changed from 'pending'. The passed
            # property will do this
            _ = self.passed  # update status from "pending" to something else
            return True
        else:
            return False

    def rich_table(self, table=None, level: int = 0) -> Table:
        """Generate a table with rich to display this result and child results"""
        # Create the table
        if table is None:
            table = Table(show_header=False, box=None)
            table.add_column("Status")
            table.add_column("Value")

        # Add a row for self
        if self.status.lower() == "pending":
            checkbox = "[ ]"
        elif self.status.lower() == "passed":
            checkbox = "[[green]:heavy_check_mark:[/green]]"
        else:
            checkbox = "[[red]x[/red]]"

        table.add_row(
            checkbox, Padding(f"{self.msg}...{self.status}", (0, 0, 0, 2 * level))
        )

        # Add a row for children
        for child in self.children:
            if isinstance(child, Result):
                # The child is a Result object
                child.rich_table(table=table, level=level + 1)
            elif isinstance(child, Future) and child.done():
                # The child is a future with a result
                result = child.result()
                result.rich_table(table=table, level=level + 1)

        return table


class Check:
    """Check base class and tree structure.

    .. versionchanged:: 1.0.0
        Rewrite and implemented threading using concurrent.futures.

    .. versionchanged:: 0.9.3
        Switch to :meth:`environment.sub_env` for value substitutions, which
        require a '$' character  and allow different expansion rules like
        defaults, errors and replacements.
    """

    #: The name for the check
    name: str

    #: Unprocessed value for the check
    raw_value: str

    #: Description of the check
    desc: str = ""

    #: The default message to include in results
    msg: str = "{check.name}"

    #: A list of children checks
    children: t.List["Check"]

    #: The condition function to use to evaluate whether children checks have passed
    condition: t.Callable = all  # default all must pass

    #: Alternative parameter names (__init__ kwarg names) used to specify the condition
    condition_aliases = ("condition", "subchecks")  # other names for variable

    #: Substitute environment variables in check values
    env_substitute: bool

    #: The default value for env_substitute
    env_substitute_default = Parameter("CHECKBASE.ENV_SUBSTITUTE_DEFAULT", default=True)

    #: Alternative parameter names (__init__ kwarg names) for env_substitute
    env_substitute_aliases = ("env_substitute", "substitute")

    #: The import_module() exception message to use if a module is missing
    #: (see the :meth:`import_modules`)
    import_error_msg = "Missing dependency '{exception}'"

    #: Maximum recursion depth of the load function
    max_level = Parameter("CHECKBASE.MAX_LEVEL", default=15)

    #: Whether this check class is available for use. Check subclasses may
    #: require additional dependencies, which might change this flag.
    #: (see :meth:`types`)
    available: bool = True

    #: Alternative names for the class (used by types)
    aliases: t.Optional[t.Tuple[str, ...]] = None

    def __init__(
        self,
        name: str,
        value: t.Optional[str] = None,
        desc: str = "",
        children: t.Optional[list["Check"]] = None,
        **kwargs,
    ):
        # Set attributes
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
        elif condition.lower() == "all":
            self.condition = all
        elif condition.lower() == "any":
            self.condition = any
        else:
            raise CheckException(
                f"The condition '{condition}' should be either 'all' or 'any'."
            )

        # Check attributes
        if not all(isinstance(child, Check) for child in self.children):
            msg = "All children should be instances of Check"
            raise CheckException(msg)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.name})"

    def __len__(self):
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
    def flatten(self) -> t.List["Check"]:
        """Return a flattened list of this check (first item) and children
        checks"""
        flattened = [self]
        for child in self.children:
            flattened += child.flatten
        return flattened

    @property
    def count(self) -> int:
        """The number of children, sub-children, etc, including self"""
        # flatten returns this check, so the count is subtracted by 1 to only
        # count sub-checks
        return len(self.flatten)

    @staticmethod
    def types() -> t.Dict[str, t.Type]:
        """The available types of Check classes, including aliases.

        Returns
        -------
        types_dict
            A dict containing the Check class or subclass name (key) and the
            class or subclass as values. The key-value pairs are also populated
            with alias names for Checks
        """
        # Retrieve the base class (Check) and children classes
        cls_types = [Check] + list(all_subclasses(Check))

        # Create a dict with the class name and type as key-value pairs
        d = dict()
        for cls_type in cls_types:
            # Skip abstract classes, which can't be instantiated
            if isabstract(cls_type):
                continue

            # Make sure class name isn't already in the dict
            assert (
                cls_type.__name__ not in d
            ), f"class {cls_type.__name__} already registered class"

            # Add the class name directly
            d[cls_type.__name__] = cls_type

            # Add class name aliases
            aliases = cls_type.aliases if cls_type.aliases is not None else ()
            for alias in aliases:
                # Aliases should not create name collisions
                assert alias not in d, f"Alias '{alias}' already matches '{d[alias]}'."

                d[alias] = cls_type
        return d

    @classmethod
    def load(
        cls, d: dict, name: str, level: int = 1, max_level: t.Optional[int] = None
    ) -> t.Union["Check", None]:
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
            The loaded root Check instance
        """
        # Check that the maximum recursion level hasn't been reached
        max_level = max_level if max_level is not None else cls.max_level

        if level >= max_level:
            msg = f"Parsing level {level} exceed the maximum level of {max_level}"
            raise NotImplementedError(msg)

        # Get a listing of the available Check types
        check_types = cls.types()

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
        found_checks = []  # Values parsed into Check objects
        other_d = dict()  # All other values
        for key, value in items:
            if not isinstance(value, dict):
                other_d[key] = value
                continue

            return_value = cls.load(
                d=value, name=key, level=level + 1, max_level=max_level
            )

            # Replace the value withe Check instance, if it was parsed correctly
            # Otherwise, just place it in the parsed_dict.
            if isinstance(return_value, Check):
                found_checks.append(return_value)
            else:
                other_d[key] = value

        # No child checks found; nothing else to do
        if len(found_checks) == 0:
            return None

        # Create a check grouping, first, by parsing the other arguments
        return Check(name=name, children=found_checks, **other_d)

    @classmethod
    def import_modules(
        cls, *names: str
    ) -> t.Union[ModuleType, t.Tuple[ModuleType, ...]]:
        """Import and return modules given by the module name(s).

        This method is useful for loading modules for checks that require
        additional dependencies, which may not be installed--aws and the
        boto3 dependency, for example.

        Parameters
        ----------
        names
            The names of modules to return

        Returns
        -------
        modules
            The loaded module(s)

        Raises
        ------
        ImportError
            Raised if the modules couldn't be found, which can happen because
            the 'aws' extra dependency wasn't installed.
        """
        modules = []

        try:
            for name in names:
                module = importlib.import_module(name)
                modules.append(module)
        except ImportError as ie:
            msg = cls.import_error_msg.format(exception=ie)
            raise ImportError(msg)
        return modules[0] if len(modules) == 1 else tuple(modules)

    def check(self, executor: t.Optional[Executor] = None, level: int = 0) -> Result:
        """Performs this check and the children checks.

        Parameters
        ----------
        executor
            An object to submit or map calls asynchronously.
            See concurrent.futures.
        level
            The current depth level of the check tree

        Returns
        -------
        result
            The result of the check
        """
        assert (
            executor is not None
        ), "An executor must be specified to run children checks"

        # check children
        child_results = []
        for child in self.children:
            result = executor.submit(child.check, executor, level + 1)
            child_results.append(result)

        return Result(msg=self.name, children=child_results, condition=self.condition)
