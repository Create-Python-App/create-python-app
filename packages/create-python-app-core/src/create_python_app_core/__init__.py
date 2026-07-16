"""Programmatic scaffolding engine for Create Awesome Python App."""

from __future__ import annotations

from create_python_app_core._version import __version__
from create_python_app_core.api import (
    CPA_USER_AGENT,
    check_for_latest_version,
    check_python_version,
    create_python_app,
    print_env_info,
)
from create_python_app_core.errors import (
    NON_EMPTY_DIR_ERROR_CODE,
    ConfigParseError,
    CpaError,
    ManifestLoadError,
    NonEmptyTargetDirectoryError,
    PackageManagerFallbackError,
    ScaffoldAbortedError,
)

__all__ = [
    "__version__",
    "CpaError",
    "ConfigParseError",
    "ManifestLoadError",
    "PackageManagerFallbackError",
    "ScaffoldAbortedError",
    "NonEmptyTargetDirectoryError",
    "NON_EMPTY_DIR_ERROR_CODE",
    "CPA_USER_AGENT",
    "check_for_latest_version",
    "check_python_version",
    "create_python_app",
    "print_env_info",
]
