"""Public API surface (mirrors @create-node-app/core index exports)."""

from __future__ import annotations

import platform
import shutil
import sys
from collections.abc import Awaitable, Callable
from pathlib import Path
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
    import httpx

    url = f"https://pypi.org/pypi/{package_name}/json"
    try:
        async with httpx.AsyncClient(
            headers={"User-Agent": CPA_USER_AGENT},
            timeout=10.0,
        ) as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            return str(data["info"]["version"])
    except Exception:
        return None


def print_env_info() -> None:
    """Print OS/Python/uv tooling versions for bug reports."""
    uv = shutil.which("uv")
    git = shutil.which("git")
    print(f"create-python-app-core: {__version__}")
    print(f"Python: {sys.version.split()[0]} ({sys.executable})")
    print(f"Platform: {platform.platform()}")
    print(f"uv: {uv or 'not found'}")
    print(f"git: {git or 'not found'}")
    if uv:
        import subprocess

        try:
            out = subprocess.check_output(["uv", "--version"], text=True).strip()
            print(f"uv version: {out}")
        except OSError:
            pass
    raise SystemExit(0)


async def create_python_app(
    project_directory: str,
    options: dict[str, Any],
    transform_options: Callable[[dict[str, Any]], Awaitable[dict[str, Any]]]
    | None = None,
) -> None:
    """Scaffold a project using the installer (#29)."""
    from create_python_app_core.installer import scaffold_project

    if transform_options is not None:
        options = await transform_options(options)

    cache = options.get("cache_dir")
    scaffold_project(
        project_directory,
        template=str(options.get("template") or ""),
        addons=list(options.get("addons") or []),
        extend=list(options.get("extend") or []),
        force=bool(options.get("force", False)),
        install=bool(options.get("install", True)),
        offline=bool(options.get("offline", False)),
        keep_on_failure=bool(options.get("keep_on_failure", False)),
        cache_dir=Path(cache) if cache else None,
        options=options,
    )
