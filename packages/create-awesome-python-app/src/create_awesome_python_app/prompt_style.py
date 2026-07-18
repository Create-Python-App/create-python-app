"""High-contrast questionary styles for CPA interactive prompts."""

from __future__ import annotations

import os

from questionary import Style

# Lighter brand blues/greens than docs hex so selected rows stay readable on
# dark terminals (slate backgrounds common in Arch/Ghostty/Alacritty).
CPA_PROMPT_STYLE = Style.from_dict(
    {
        "qmark": "fg:#60a5fa bold",
        "question": "bold fg:#f8fafc",
        "answer": "fg:#4ade80 bold",
        "pointer": "fg:#60a5fa bold",
        "highlighted": "fg:#0f172a bg:#60a5fa bold",
        "selected": "fg:#4ade80 bold",
        "separator": "fg:#94a3b8",
        "instruction": "fg:#94a3b8",
        "text": "fg:#e2e8f0",
        "disabled": "fg:#64748b italic",
        "checkbox": "fg:#60a5fa",
        "checkbox-selected": "fg:#4ade80 bold",
    }
)


def colors_enabled() -> bool:
    return not os.environ.get("NO_COLOR")


def ansi(code: str, text: str) -> str:
    """Wrap *text* in an ANSI SGR sequence when colors are enabled."""
    if not colors_enabled():
        return text
    return f"\033[{code}m{text}\033[0m"


# Bold bright ANSI — readable on dark terminals; select() renders these safely
# (unlike autocomplete, which HTML-parses choice text).
_CATEGORY_PALETTE = (
    "1;93",  # bright yellow
    "1;92",  # bright green
    "1;96",  # bright cyan
    "1;95",  # bright magenta
    "1;94",  # bright blue
)


def color_category(slug: str, label: str) -> str:
    idx = sum(ord(char) for char in slug) % len(_CATEGORY_PALETTE)
    return ansi(_CATEGORY_PALETTE[idx], label)


def bold(text: str) -> str:
    return ansi("1", text)


def dim(text: str) -> str:
    return ansi("2", text)
