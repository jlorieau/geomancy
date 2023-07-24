"""Test the CheckPythonPackage check"""
import pytest

from geomancy.checks.python import CheckPythonPackage

try:
    import pip
except ImportError:
    pip = None


@pytest.fixture
def reset():
    """Reset class caches"""
    # Reset cached version, if populated by another test
    if hasattr(CheckPythonPackage, "pip_freeze"):
        del CheckPythonPackage.pip_freeze
    return CheckPythonPackage


@pytest.mark.skipif(pip is None, reason="pip must be installed")
def test_check_python_package_get_current_version_pip(reset):
    """Test the CheckPythonPackage get_current_version method with pip"""
    # Check that pip_freeze can get populated
    check = CheckPythonPackage(name="Python package", value="mypkg>=3.0")
    check.use_pip_freeze = True

    assert not hasattr(check, "pip_freeze")
    check.get_current_version()
    assert hasattr(check, "pip_freeze") and isinstance(check.pip_freeze, str)

    # Substitute the pip freeze and see if the package version is correctly parsed
    check.pip_freeze = ""
    assert check.get_current_version() is None
    check.pip_freeze = "\n".join(("more-itertools==9.1.0", "mypkg==3.0"))
    assert check.get_current_version() == (3, 0)


def test_check_python_package_get_current_version_no_pip(reset):
    """Test the CheckPythonPackage get_current_version method without pip"""
    check = CheckPythonPackage(name="Python package", value="pytest")
    check.use_pip_freeze = False

    version = check.get_current_version()
    assert not hasattr(check, "pip_freeze")
    assert version is not None  # A version should have been found for 'pytest'
    assert isinstance(version, tuple)


def test_check_python_package_exists(reset):
    """Tests CheckPythonPackage checking for an existing and a missing
    package"""
    # Should exist
    check = CheckPythonPackage(name="Check pytest", value="pytest")
    assert check.check().passed

    # Should not exist
    check = CheckPythonPackage(name="Check missing", value="_miss_ing_")
    assert not check.check().passed


def test_check_python_package_version(reset):
    """Tests CheckPythonPackage checking with version number"""
    # Should be greater than version 1.0
    check = CheckPythonPackage(name="Check pytest", value="pytest>=1.0")
    assert check.check().passed

    # Should be less than version 1000.
    check = CheckPythonPackage(name="Check pytest", value="pytest>=1000.0")
    assert not check.check().passed
