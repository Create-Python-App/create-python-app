#!/usr/bin/env python3
"""Extract a single version section from CHANGELOG.md."""

from __future__ import annotations

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def extract_notes(version: str) -> str:
    lines = (ROOT / "CHANGELOG.md").read_text().splitlines()
    heading_prefix = f"## {version}"
    start = next(
        (idx for idx, line in enumerate(lines) if line.startswith(heading_prefix)),
        None,
    )
    if start is None:
        raise SystemExit(f"CHANGELOG.md does not contain notes for {version}")

    end = next(
        (
            idx
            for idx, line in enumerate(lines[start + 1 :], start + 1)
            if line.startswith("## ")
        ),
        len(lines),
    )
    return "\n".join(lines[start + 1 : end]).strip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("version")
    parser.add_argument("--output", default="release-notes.md")
    args = parser.parse_args()

    Path(args.output).write_text(extract_notes(args.version))
    print(f"Wrote release notes for {args.version} to {args.output}")


if __name__ == "__main__":
    main()
