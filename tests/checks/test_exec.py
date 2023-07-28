"""
Test the CheckExec class
"""
from geomancy.checks.exec import CheckExec


def test_check_exec_get_current_version_no_pip():
    """Test the CheckExec get_current_version method"""
    check = CheckExec(name="python", value="python")

    version = check.get_current_version()
    assert isinstance(version, tuple)
    assert version[0] >= 2  # python 2 or later


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
