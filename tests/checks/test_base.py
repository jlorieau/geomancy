"""
Test the environment variable check class
"""
import typing as t
from concurrent.futures import ThreadPoolExecutor

import pytest

from geomancy.checks.base import Check, Result, CheckException, Executor


class CheckDummy(Check):
    """A dummy Check subclass for testing aliases"""

    aliases = ("checkDummy",)


class HangCheck(Check):
    """A Check subclass that allows thread hanging"""

    locked = True

    def check(self, executor: t.Optional[Executor] = None, level: int = 0) -> Result:
        # The following hangs the thread until self.locked is set to False
        while self.locked:
            pass
        return Result(msg=self.name, status="passed")


class DefaultCheck(Check):
    """A Check subclass that reads the returned result status from an instance
    attribute"""

    default_status = "passed"

    def check(self, executor: t.Optional[Executor] = None, level: int = 0) -> Result:
        return Result(msg=self.name, status=self.default_status)


def test_result_status_validation():
    """The Result validation of status"""
    # These are ok
    allowed = (
        "passed",
        "failed",
        "pending",
        "passed (it went well)",
        "failed (it didn't go well)",
    )
    for status in allowed:
        Result(status=status)

    # These are not ok
    not_allowed = (
        "passed ",  # extra space
        "passed (open",  # parenthesis not closed
        "passed  (it went well)",  # extra space before parenthesis
        "passed (it went well) ",  # extra space after parenthesis
        "passed (This has\na new line)",  # new line
    )

    for status in not_allowed:
        with pytest.raises(AssertionError):
            Result(status=status)


def test_check_init_env_subtitute():
    """Test the Check init with env_substitute specified"""
    for kwargs, expected in (
        ({"env_substitute": False}, False),
        ({"substitute": False}, False),
        ({}, True),  # default
    ):
        check = Check(name="EnvTest", **kwargs)
        assert check.env_substitute == expected


def test_check_init_condition():
    """Test the Check init with condition specified"""
    # 2. Test condition parameter aliases
    for kwargs, expected in (
        ({"condition": "all"}, all),
        ({"condition": "any"}, any),
        ({"subchecks": "all"}, all),
        ({"subchecks": "any"}, any),
        ({}, all),  # default
    ):
        check = Check(name="ConditionTest", **kwargs)
        assert check.condition == expected


def test_check_init_bad_child():
    """Test the Check init with a non-Check child"""
    with pytest.raises(CheckException):
        Check(name="BadChild", children=["a"])


def test_check_env_substitution():
    """Test the Check environment substitution of the value property"""
    with pytest.MonkeyPatch.context() as mp:
        # Set some present and missing environment variables
        mp.setenv("VARIABLE", "my value")
        mp.delenv("MISSING", raising=False)

        # 1. Present environment variable without braces
        assert Check(name="sub_env", value="$VARIABLE").raw_value == "$VARIABLE"
        assert Check(name="sub_env", value="$VARIABLE").value == "my value"

        # 2. Present environment variable with braces
        assert Check(name="sub_env", value="${VARIABLE}").raw_value == "${VARIABLE}"
        assert Check(name="sub_env", value="${VARIABLE}").value == "my value"

        # 3. Missing environment variable with braces substitute to empty string
        assert Check(name="sub_env", value="${MISSING}").raw_value == "${MISSING}"
        assert Check(name="sub_env", value="${MISSING}").value == ""

        # 4. Disable substitution
        #   4.1. Use the env_substitute=False flag without brace
        assert (
            Check(name="sub_env", value="$VARIABLE", env_substitute=False).value
            == "$VARIABLE"
        )

        #   4.2. Use the substitute=False flag without brace
        assert (
            Check(name="sub_env", value="$VARIABLE", substitute=False).value
            == "$VARIABLE"
        )

        #   4.3. Use the substitute=False flag with brace
        assert (
            Check(name="sub_env", value="${VARIABLE}", substitute=False).value
            == "${VARIABLE}"
        )

        #   4.4. Use string literal with and without brace
        assert Check(name="sub_env", value="'$VARIABLE'").value == "$VARIABLE"
        assert Check(name="sub_env", value="'${VARIABLE}'").value == "${VARIABLE}"

        #   4.5. Use the substitute=False flag without brace for missing variable
        assert (
            Check(name="sub_env", value="$MISSING", substitute=False).value
            == "$MISSING"
        )

        #   4.6. Use string literal for missing variable
        assert Check(name="sub_env", value="'$MISSING'").value == "$MISSING"


# noinspection GrazieInspection
def test_check_flatten_count():
    """Test the Check.flatten and Check.count properties"""
    # Create a Check tree
    sub11 = Check(name="sub11")
    sub12 = Check(name="sub12")
    sub1 = Check(name="sub1", children=[sub11, sub12])
    sub2 = Check(name="sub2")
    root = Check(name="root", children=[sub1, sub2])

    # Check the flattened tree
    flattened = root.flatten

    assert len(flattened) == 5
    assert root.count == 5
    assert flattened[0] == root
    assert flattened[1] == sub1
    assert flattened[2] == sub11
    assert flattened[3] == sub12
    assert flattened[4] == sub2


def test_check_types():
    """Test the Check.types() method"""

    types = Check.types()

    # All keys should be strings (class names)
    assert all(isinstance(k, str) for k in types.keys())

    # All values should be classes
    assert all(issubclass(v, Check) or v == Check for v in types.values())


# noinspection GrazieInspection
def test_check_load_simple():
    """Test the Check.load method from a simple dict"""
    d = {"CheckDummy": "PATH", "desc": "The $PATH environment variable"}

    check = Check.load(d=d, name="base check")

    assert check is not None
    assert isinstance(check, Check)
    assert check.__class__ == CheckDummy
    assert check.value == "PATH"
    assert check.desc == d["desc"]


def test_check_load_nested():
    """Test the Check.load method from a nested dict"""
    d = {
        "Environment": {
            "desc": "Environment checks",
            "Path": {"checkDummy": "VAR1", "desc": "Check VAR2"},
            "Term": {"checkDummy": "VAR2", "desc": "Check VAR2"},
        }
    }

    check = Check.load(d=d, name="base check")

    # Validate the root check
    assert check is not None
    assert isinstance(check, Check)
    assert check.name == "base check"

    # Validate the check tree
    flattened = check.flatten
    assert len(flattened) == 4

    # Validate class types
    assert flattened[0].__class__ == Check
    assert flattened[1].__class__ == Check
    assert flattened[2].__class__ == CheckDummy
    assert flattened[3].__class__ == CheckDummy

    # Validate check names
    assert flattened[0].name == "base check"
    assert flattened[1].name == "Environment"
    assert flattened[2].name == "Path"
    assert flattened[3].name == "Term"

    # Validate check values
    assert flattened[0].value is None
    assert flattened[1].value is None
    assert flattened[2].value == "VAR1"
    assert flattened[3].value == "VAR2"

    # Validate children entries
    assert flattened[0].children == [flattened[1]]
    assert flattened[1].children == [flattened[2], flattened[3]]
    assert flattened[2].children == []
    assert flattened[3].children == []


def test_check_import_modules():
    """Test the Check.import_modules method"""
    # Try a present module
    other_pytest = Check.import_modules("pytest")
    assert other_pytest == pytest

    # Try a missing module
    with pytest.raises(ImportError):
        Check.import_modules("nonexist-missing")


@pytest.mark.parametrize("condition", ("all", "any"))
def test_check_result_passed(condition):
    """Test Check.check and Result.passed methods together (all condition."""

    # Create a check with a thread-locking sub-check
    sub1 = DefaultCheck(name="DefaultCheck1")
    sub2 = DefaultCheck(name="DefaultCheck2")
    check = Check(name="root", children=[sub1, sub2], condition=condition)

    # Create an executor to run the checks
    with ThreadPoolExecutor() as executor:
        result = check.check(executor=executor)

        # 1. Both sub1 and sub2 return results with status="passed" so the root
        #    check should pass under any 'condition'

        while not result.done:  # Wait for the thread to evaluate
            pass

        assert result.passed
        assert result.status == "passed"

        # 2. Changing one of the sub default statuses and rerunning the check
        #    should impact how the root check passes
        sub1.default_status = "failed"
        result = check.check(executor=executor)

        while not result.done:  # Wait for the thread to evaluate
            pass

        if condition == "any":
            assert result.passed  # Just one sub passing is good enough
            assert result.status == "passed"
        elif condition == "all":
            assert not result.passed  # One sub failed, so the root check fails
            assert result.status == "failed"

        # 3. Change both the sub default statuses and rerunning the check should
        #    impact how the root check passes
        sub2.default_status = "failed"
        result = check.check(executor=executor)

        while not result.done:  # Wait for the thread to evaluate
            pass

        assert not result.passed  # all children checks fail
        assert result.status == "failed"


def test_check_result_done():
    """Test Check.check and Result.done methods together."""

    # Create a check with a thread-locking sub-check
    sub = HangCheck(name="HangCheck")
    check = Check(name="root", children=[sub])

    # Create an executor to run the checks
    with ThreadPoolExecutor() as executor:
        result = check.check(executor=executor)

        # The 'sub' has the thread hanged and can't finish its check
        assert not result.done

        # Releasing the thread lock should allow 'sub' to finish its check
        sub.locked = False

        # The release might not be instantaneously after releasing the lock,
        # so we wait until the 'sub' check is done
        while not result.done:
            pass
        assert result.done


def test_check_result_finished():
    """Test Check.check and Result.finished methods together."""

    # Create a check with a thread-locking sub-check
    sub = HangCheck(name="HangCheck")
    check = Check(name="root", children=[sub])

    # Create an executor to run the checks
    with ThreadPoolExecutor() as executor:
        result = check.check(executor=executor)

        # The 'sub1' and 'sub2 has the thread hanged and can't finish their checks
        assert not result.done
        assert result.finished == []  # nothing is finished

        # Release thread locks and check that it's finished
        sub.locked = False

        # The release might not be instantaneously after releasing the lock,
        # so we wait until the 'sub' check is done
        while not result.done:
            pass

        assert result.done
        assert len(result.finished) == 2
        assert all(isinstance(r, Result) for r in result.finished)
