"""
Test the CheckExec class
"""
from geomancy.checks.exec import CheckExec


def test_check_exec_exists():
    """Tests CheckExec checking for an existing and a missing command"""
    # Should exist
    check = CheckExec(name="Check Python", value="python3")
    assert check.check().passed

    # Should not exist
    check = CheckExec(name="Check Python", value="_miss_ing_")
    assert not check.check().passed


def test_check_exec_version():
    """Tests CheckExec checking with version number"""
    # Should be greater than version 2.0
    check = CheckExec(name="Check Python", value="python>=2.0")
    assert check.check().passed

    # Should be less than version 1000.
    check = CheckExec(name="Check Python", value="python>=1000.0")
    assert not check.check().passed


def test_check_exec_missing_version():
    """Tests CheckExec check with a command that doesn't give a version number"""
    # Command without a version number
    check = CheckExec(name="Check ls", value="ls>=2.0")
    assert not check.check().passed

    # Without a version number, the check passes
    check = CheckExec(name="Check ls", value="ls")
    assert check.check().passed
