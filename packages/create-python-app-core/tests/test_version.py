import re

from create_python_app_core import CPA_USER_AGENT, __version__

_SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+(?:[.-][0-9A-Za-z.-]+)?$")


def test_version_is_semver() -> None:
    assert _SEMVER_RE.match(__version__), f"not semver: {__version__!r}"


def test_user_agent_contains_version() -> None:
    assert __version__ in CPA_USER_AGENT
    assert "create-python-app-core" in CPA_USER_AGENT
