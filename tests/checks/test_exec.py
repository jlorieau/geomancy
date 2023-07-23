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
