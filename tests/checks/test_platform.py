"""Tests for the platform and version"""
from geomancy.checks import CheckPlatform


def test_check_platform():
    """Test the CheckPlatform check"""
    # Minimum version for Python 3.11 is macOS 10.9
    check_macos = CheckPlatform(name="checkMacOS", value="macOS >= 10.9")

    # Linux 4.0 was released in 2015
    check_linux = CheckPlatform(name="checkLinux", value="Linux >= 4.0")

    # Windows 10 was released in 2015
    check_windows = CheckPlatform(name="checkWindows", value="Windows >= 10")

    assert any(
        check.check().passed for check in (check_macos, check_linux, check_windows)
    )
