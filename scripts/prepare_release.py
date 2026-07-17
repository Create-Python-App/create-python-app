#!/usr/bin/env python3
"""Prepare a release bump across the CPA workspace."""

from __future__ import annotations

import argparse
import re
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

VERSION_RE = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+(?:[a-zA-Z0-9.-]+)?$")
PROJECT_VERSION_RE = re.compile(r'(?m)^version = "[^"]+"$')
CORE_DEP_RE = re.compile(r'"create-python-app-core>=[^"]+"')
PY_VERSION_RE = re.compile(r'__version__ = "[^"]+"')

VERSION_FILES = [
    ROOT / "packages/create-python-app-core/pyproject.toml",
    ROOT / "packages/create-awesome-python-app/pyproject.toml",
    ROOT / "packages/create-python-app-core/src/create_python_app_core/_version.py",
    ROOT / "packages/create-awesome-python-app/src/create_awesome_python_app/__init__.py",
]


def replace_once(path: Path, pattern: re.Pattern[str], replacement: str) -> None:
    text = path.read_text()
    updated, count = pattern.subn(replacement, text, count=1)
    if count != 1:
        raise SystemExit(f"Expected one replacement in {path}, got {count}")
    path.write_text(updated)


def update_versions(version: str) -> None:
    replace_once(
        ROOT / "packages/create-python-app-core/pyproject.toml",
        PROJECT_VERSION_RE,
        f'version = "{version}"',
    )
    replace_once(
        ROOT / "packages/create-awesome-python-app/pyproject.toml",
        PROJECT_VERSION_RE,
        f'version = "{version}"',
    )
    replace_once(
        ROOT / "packages/create-awesome-python-app/pyproject.toml",
        CORE_DEP_RE,
        f'"create-python-app-core>={version}"',
    )
    replace_once(
        ROOT / "packages/create-python-app-core/src/create_python_app_core/_version.py",
        PY_VERSION_RE,
        f'__version__ = "{version}"',
    )
    replace_once(
        ROOT / "packages/create-awesome-python-app/src/create_awesome_python_app/__init__.py",
        PY_VERSION_RE,
        f'__version__ = "{version}"',
    )


def update_changelog(version: str, notes: str) -> None:
    changelog = ROOT / "CHANGELOG.md"
    text = changelog.read_text()
    heading = f"## {version}"
    if heading in text:
        raise SystemExit(f"CHANGELOG.md already contains {heading}")

    today = datetime.now(UTC).date().isoformat()
    body = notes.strip() or "- Maintenance release."
    section = f"## {version} - {today}\n\n{body}\n\n"
    if not text.startswith("# Changelog\n\n"):
        raise SystemExit("CHANGELOG.md must start with '# Changelog'")
    changelog.write_text(text.replace("# Changelog\n\n", f"# Changelog\n\n{section}", 1))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("version", help="Release version, e.g. 0.1.1")
    parser.add_argument(
        "--notes",
        default="- Maintenance release.",
        help="Markdown notes to insert into CHANGELOG.md",
    )
    args = parser.parse_args()

    if not VERSION_RE.match(args.version):
        raise SystemExit(f"Invalid version: {args.version}")

    for path in VERSION_FILES:
        if not path.is_file():
            raise SystemExit(f"Missing expected version file: {path}")

    update_versions(args.version)
    update_changelog(args.version, args.notes)
    print(f"Prepared release {args.version}")


if __name__ == "__main__":
    main()
