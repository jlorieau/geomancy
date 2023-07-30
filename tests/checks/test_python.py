"""Test the CheckPythonPackage check"""
from geomancy.checks.python import CheckPythonPackage

try:
    import pip
except ImportError:
    pip = None


def test_check_python_package_exists():
    """Tests CheckPythonPackage checking for an existing and a missing
    package"""
    # Should exist
    check = CheckPythonPackage(name="Check pytest", value="pytest")
    assert check.check().passed

    # Should not exist
    check = CheckPythonPackage(name="Check missing", value="_miss_ing_")
    assert not check.check().passed


def test_check_python_package_version():
    """Tests CheckPythonPackage checking with version number"""
    # Should be greater than version 1.0
    check = CheckPythonPackage(name="Check pytest", value="pytest>=1.0")
    assert check.check().passed

    # Should be less than version 1000.
    check = CheckPythonPackage(name="Check pytest", value="pytest>=1000.0")
    assert not check.check().passed
