"""Shared test fixtures for create-awesome-python-app."""

from __future__ import annotations

import os

import pytest

_CPA_ENV_VARS = (
    "CPA_REFRESH",
    "CPA_NO_CATALOG_CACHE",
    "CPA_CACHE_DIR",
    "CPA_CATALOG_FIXTURE",
    "CPA_FIXTURE_DIR",
)


@pytest.fixture(autouse=True)
def _clean_cpa_process_env() -> None:
    """Clear CPA env vars that CLI helpers set via ``os.environ`` (not monkeypatch).

    ``apply_fixture_mode`` mutates ``os.environ`` directly. Pairing that with
    ``monkeypatch.delenv`` after the test can restore the leaked value when
    monkeypatch undoes its stack — so cleanup must use ``os.environ.pop``.
    """
    from create_awesome_python_app.catalog import (
        reset_catalog_cache_for_tests,
        reset_fixture_root_for_tests,
    )

    for name in _CPA_ENV_VARS:
        os.environ.pop(name, None)
    reset_catalog_cache_for_tests()
    reset_fixture_root_for_tests()
    yield
    for name in _CPA_ENV_VARS:
        os.environ.pop(name, None)
    reset_catalog_cache_for_tests()
    reset_fixture_root_for_tests()
