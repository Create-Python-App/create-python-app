import pytest
from create_python_app_core import check_python_version


def test_check_python_version_accepts_current() -> None:
    check_python_version(">=3.12", "create-python-app-core")


def test_check_python_version_rejects_impossible() -> None:
    with pytest.raises(SystemExit):
        check_python_version(">=99.0", "create-python-app-core")
