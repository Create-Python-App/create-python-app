"""High-contrast questionary styles for CPA interactive prompts."""

from __future__ import annotations

import os
from typing import Any

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

# Bright prompt_toolkit style strings (not raw ANSI — select() prints str titles
# literally, so escapes show as ^[[...m unless titles are FormattedText tokens).
_CATEGORY_STYLES = (
    "fg:#facc15 bold",  # yellow
    "fg:#4ade80 bold",  # green
    "fg:#22d3ee bold",  # cyan
    "fg:#e879f9 bold",  # magenta
    "fg:#60a5fa bold",  # blue
)


class SearchableFormattedText(list):
    """FormattedText tokens with ``.lower()`` for questionary search filter.

    ``select(use_search_filter=True)`` does ``needle in choice.title.lower()``.
    A plain token list has no ``.lower()``; this keeps filter working while
    titles render as styled FormattedText.
    """

    def __init__(self, tokens: list[tuple[str, str]], search: str) -> None:
        super().__init__(tokens)
        self._search = search

    def lower(self) -> str:
        return self._search.lower()


def colors_enabled() -> bool:
    return not os.environ.get("NO_COLOR")


def category_style(slug: str) -> str:
    idx = sum(ord(char) for char in slug) % len(_CATEGORY_STYLES)
    return _CATEGORY_STYLES[idx]


def plain_title_text(title: Any) -> str:
    """Join FormattedText token text (or return a plain string title)."""
    if isinstance(title, list):
        return "".join(str(token[1]) for token in title)
    return str(title)


def template_title_tokens(
    *,
    category_slug: str,
    badge: str,
    name: str,
    slug: str,
    labels: list[str],
    description: str,
    search: str,
) -> SearchableFormattedText | str:
    """Build a select-safe title: FormattedText when colors on, else plain str."""
    label_suffix = ""
    if labels:
        label_suffix = " · " + ", ".join(labels[:3])
    description_suffix = f" — {description}" if description else ""
    plain = f"{badge}  {name} ({slug}){label_suffix}{description_suffix}"

    if not colors_enabled():
        return plain

    tokens: list[tuple[str, str]] = [
        (category_style(category_slug), badge),
        ("", "  "),
        ("bold", name),
        ("class:instruction", f" ({slug})"),
    ]
    if label_suffix:
        tokens.append(("class:instruction", label_suffix))
    if description_suffix:
        tokens.append(("fg:#94a3b8", description_suffix))
    return SearchableFormattedText(tokens, search=search or plain)


def custom_template_title(search: str) -> SearchableFormattedText | str:
    label = "Use my own template URL"
    plain = " " * 12 + label
    if not colors_enabled():
        return plain
    return SearchableFormattedText(
        [("", " " * 12), ("italic fg:#94a3b8", label)],
        search=search or plain,
    )
