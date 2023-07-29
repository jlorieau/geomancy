"""
Test the path check class
"""
from pathlib import Path

import pytest

from geomancy.checks import CheckPath, CheckException


def test_check_path_missing():
    """Test CheckPath with a missing path"""
    missing_path = "./.missing.miss"
    assert not Path(missing_path).exists()

    check = CheckPath("missing", missing_path)
    assert check.name == "missing"
    assert check.value == missing_path
    assert not check.check().passed


@pytest.mark.parametrize("path_type", (None, "file", "dir", "nonsense"))
def test_check_path_file_type(tmp_path, path_type):
    """Test CheckPath with different file types"""
    # Create the test files and dirs
    tmp_file = tmp_path / "exists.txt"
    tmp_file.touch()

    tmp_dir = tmp_path / "sub"
    tmp_dir.mkdir()

    # Create the check with an existing file
    if path_type == "nonsense":
        with pytest.raises(CheckException):
            CheckPath(name="PathCheck", value=tmp_file, type=path_type)
        return None
    else:
        check = CheckPath(name="PathCheck", value=tmp_file, type=path_type)

    if path_type in (None, "file"):
        assert check.check().passed
    else:
        assert not check.check().passed

    # Switch to the directory, and the check conditions change
    check.value = tmp_dir

    if path_type in (None, "dir"):
        assert check.check().passed
    else:
        assert not check.check().passed


def test_check_path_env_substitution(tmp_path):
    """Test CheckPath with environmental subsitution"""
    # Create the test files and dirs
    ENV = "dev"
    tmp_file = tmp_path / ENV / "exists.txt"
    tmp_file.parent.mkdir()
    tmp_file.touch()

    path = tmp_path / "$ENV" / "exists.txt"
    assert "$ENV" in str(path)  # not substituted yet

    with pytest.MonkeyPatch.context() as mp:
        # Make sure the ENV variable hasn't been created yet
        mp.delenv("ENV", raising=False)

        # The variable doesn't exist so the check should fail
        check = CheckPath(name="PathEnvVariable", value=path)
        assert not check.check().passed

        # Set the ENV variable, and it should now work
        mp.setenv("ENV", ENV)
        assert check.check().passed
