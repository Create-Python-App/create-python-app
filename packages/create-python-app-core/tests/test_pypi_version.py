import pytest
from create_python_app_core.api import check_for_latest_version


@pytest.mark.asyncio
async def test_check_for_latest_version_handles_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import httpx

    class FakeClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return None

        async def get(self, url: str):
            raise httpx.ConnectError("offline")

    monkeypatch.setattr("httpx.AsyncClient", FakeClient)
    assert await check_for_latest_version("create-awesome-python-app") is None
