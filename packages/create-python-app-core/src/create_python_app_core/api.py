"""Public API surface (mirrors @create-node-app/core index exports)."""

from __future__ import annotations

import sys
from collections.abc import Awaitable, Callable
from typing import Any

from create_python_app_core._version import __version__

CPA_USER_AGENT = (
    f"create-python-app-core/{__version__} "
    "(https://github.com/Create-Python-App/create-python-app)"
)


def check_python_version(required: str, package_name: str) -> None:
    """Exit if the running interpreter does not satisfy *required* (PEP 440)."""
    from packaging.specifiers import SpecifierSet
    from packaging.version import Version

    current = Version(".".join(map(str, sys.version_info[:3])))
    if current not in SpecifierSet(required):
        print(
            f"You are running Python {current}.\n"
            f"{package_name} requires Python {required}.\n"
            "Please update your version of Python.",
            file=sys.stderr,
        )
        raise SystemExit(1)


async def check_for_latest_version(package_name: str) -> str | None:
    """Fetch latest version from PyPI. Returns None on failure."""
    # Implemented fully in #31; stub returns None until then.
    _ = package_name
    return None


def print_env_info() -> None:
    """Print environment info then exit. Full implementation in #30."""
    print(f"create-python-app-core {__version__}")
    print(f"Python {sys.version}")
    raise SystemExit(0)


async def create_python_app(
    project_directory: str,
    options: dict[str, Any],
    transform_options: Callable[[dict[str, Any]], Awaitable[dict[str, Any]]]
    | None = None,
) -> None:
    """Scaffold a project. Full installer lands in #29."""
    if transform_options is not None:
        options = await transform_options(options)
    raise NotImplementedError(
        "create_python_app installer not implemented yet — see #29 "
        f"(project={project_directory!r}, options_keys={list(options)})"
    )
