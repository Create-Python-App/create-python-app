from create_python_app_core import CPA_USER_AGENT, __version__


def test_version_is_semver_stub() -> None:
    assert __version__ == "0.0.0"


def test_user_agent_contains_version() -> None:
    assert __version__ in CPA_USER_AGENT
    assert "create-python-app-core" in CPA_USER_AGENT
