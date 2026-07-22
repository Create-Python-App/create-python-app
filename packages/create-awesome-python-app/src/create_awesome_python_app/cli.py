"""Typer CLI entrypoint for create-awesome-python-app."""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path
from typing import Any

import typer
from create_python_app_core import (
    ConfigParseError,
    CpaCustomOption,
    NonEmptyTargetDirectoryError,
    assert_directory_is_empty,
    check_for_latest_version,
    check_python_version,
    create_python_app,
    default_cache_dir,
    download_repository,
    load_cpa_config,
    print_env_info,
    resolve_source,
)
from create_python_app_core.git_cache import RefreshMode
from rich.console import Console

from create_awesome_python_app import __version__

# Sentinel for bare ``--fixture`` (optional DIR rewritten in argv preprocess).
_FIXTURE_AUTO = "__CPA_FIXTURE_AUTO__"

app = typer.Typer(
    name="create-awesome-python-app",
    help="Composable scaffolding CLI for production-ready Python apps.",
    no_args_is_help=False,
    add_completion=True,
    # Keep cache out of this Typer app (routed in main()). A nested command
    # group turns the CLI into Click Group form `[ARGS] COMMAND`, so
    # `cpa my-api --template …` fails with "No such command '--template'".
    epilog="Cache: create-awesome-python-app cache [list|dir|clean|verify|…]",
)
cache_app = typer.Typer(help="Inspect and manage the local template cache")
console = Console(stderr=True)


def _preprocess_fixture_argv(argv: list[str] | None = None) -> list[str]:
    """Rewrite bare ``--fixture`` to ``--fixture=__CPA_FIXTURE_AUTO__``.

    Typer/Click requires an option argument; Commander allows ``--fixture [dir]``.
    This keeps CNA-compatible UX: ``--fixture`` alone enables auto-detect mode.
    """
    raw = list(sys.argv if argv is None else argv)
    if not raw:
        return raw
    out = [raw[0]]
    i = 1
    while i < len(raw):
        arg = raw[i]
        if arg == "--fixture":
            if i + 1 < len(raw) and not raw[i + 1].startswith("-"):
                out.extend(["--fixture", raw[i + 1]])
                i += 2
            else:
                out.append(f"--fixture={_FIXTURE_AUTO}")
                i += 1
            continue
        out.append(arg)
        i += 1
    if argv is None:
        sys.argv = out
    return out


def _expand_variadic_option(argv: list[str], option: str) -> list[str]:
    """Expand ``--addons a b`` into ``--addons a --addons b`` (CNA Commander parity).

    Typer's ``list[str]`` Option only accepts one value per flag. Commander uses
    ``--addons [extensions...]``, so users naturally write space-separated lists.

    When ``project_directory`` comes *after* options and no positional was seen
    yet, peel the final trailing token at EOS back as the directory so that
    ``--addons a --addons b /tmp/app`` does not treat ``/tmp/app`` as an addon.
    """
    out: list[str] = []
    i = 0
    prefix = option + "="
    saw_positional = False
    while i < len(argv):
        arg = argv[i]
        if arg == option:
            i += 1
            values: list[str] = []
            while i < len(argv) and not argv[i].startswith("-"):
                values.append(argv[i])
                i += 1
            ended_at_eos = i >= len(argv)
            trailing: str | None = None
            if ended_at_eos and not saw_positional and len(values) >= 2:
                trailing = values.pop()
            if not values:
                out.append(option)
            else:
                for value in values:
                    out.extend([option, value])
            if trailing is not None:
                out.append(trailing)
                saw_positional = True
            continue
        if arg.startswith(prefix):
            value = arg[len(prefix) :]
            out.extend([option, value] if value else [option])
            i += 1
            continue
        if i > 0 and not arg.startswith("-"):
            saw_positional = True
        out.append(arg)
        i += 1
    return out


def _preprocess_cli_argv(argv: list[str] | None = None) -> list[str]:
    """Apply argv rewrites needed before Typer parses the CLI."""
    raw = list(sys.argv if argv is None else argv)
    # Pass an explicit list so fixture preprocess does not mutate sys.argv early.
    out = _preprocess_fixture_argv(raw)
    out = _expand_variadic_option(out, "--addons")
    out = _expand_variadic_option(out, "--extend")
    if argv is None:
        sys.argv = out
    return out


def apply_fixture_mode(fixture: str | None) -> None:
    """Translate ``--fixture`` into ``CPA_CATALOG_FIXTURE`` / ``CPA_FIXTURE_DIR``."""
    if fixture is None and os.environ.get("CPA_CATALOG_FIXTURE") != "1":
        return
    os.environ["CPA_CATALOG_FIXTURE"] = "1"
    if fixture is not None and fixture != _FIXTURE_AUTO and fixture != "":
        os.environ["CPA_FIXTURE_DIR"] = fixture


def _in_ci() -> bool:
    return os.environ.get("CI", "").lower() in {"1", "true", "yes"}


def _template_config_path(source_subdir: str | None, root: Path) -> Path:
    cfg_path = root / "cpa.config.json"
    if not cfg_path.is_file() and source_subdir:
        cfg_path = root / source_subdir / "cpa.config.json"
    return cfg_path


def _parse_set_options(set_opt: list[str] | None) -> dict[str, str]:
    set_map: dict[str, str] = {}
    for item in set_opt or []:
        if "=" not in item:
            console.print(f"[red]Invalid --set {item} (expected key=value)[/red]")
            raise typer.Exit(2)
        key, value = item.split("=", 1)
        set_map[key] = value
    return set_map


def _normalize_refresh(refresh: str | None) -> RefreshMode | None:
    if refresh == "always":
        return "always"
    if refresh == "stale":
        return "stale"
    if refresh == "manual":
        return "manual"
    return None


def _stringify_option_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def _registry_custom_options(items: list[dict[str, Any]]) -> list[CpaCustomOption]:
    options: list[CpaCustomOption] = []
    for item in items:
        key = item.get("key") or item.get("name")
        if not key:
            continue
        options.append(
            CpaCustomOption(
                key=str(key),
                type=str(item.get("type", "string")),
                message=str(item.get("message", "")),
                default=item.get("default", item.get("initial")),
            )
        )
    return options


def _prompt_custom_options(
    template: str,
    *,
    set_map: dict[str, str],
    cache_dir: Path | None,
    offline: bool,
    refresh: str | None,
    registry_options: list[dict[str, Any]] | None = None,
) -> dict[str, str]:
    import questionary

    from create_awesome_python_app.prompt_style import CPA_PROMPT_STYLE

    source = resolve_source(template, cache_dir=cache_dir)
    root = download_repository(
        source,
        offline=offline,
        refresh=_normalize_refresh(refresh),
        cache_root=cache_dir,
    )
    try:
        config = load_cpa_config(_template_config_path(source.subdir, root))
    except ConfigParseError as err:
        console.print(f"[yellow]Warning: {err}[/yellow]")
        return {}

    custom_options = config.custom_options
    if not custom_options and registry_options:
        custom_options = _registry_custom_options(registry_options)

    answers: dict[str, str] = {}
    blocked_types = {"password", "invisible"}
    for option in custom_options:
        if option.type in blocked_types:
            console.print(
                f"[yellow]Warning: skipped blocked custom option {option.key}[/yellow]"
            )
            continue
        if option.key in set_map:
            answers[option.key] = set_map[option.key]
            continue
        initial = set_map.get(option.key, _stringify_option_value(option.default))
        message = option.message or option.key
        if option.type in {"bool", "boolean", "confirm"}:
            answer = questionary.confirm(
                message,
                default=initial.lower() in {"1", "true", "yes", "on"},
                style=CPA_PROMPT_STYLE,
            ).ask()
        else:
            answer = questionary.text(
                message, default=initial, style=CPA_PROMPT_STYLE
            ).ask()
        if answer is None:
            raise typer.Exit(1)
        answers[option.key] = _stringify_option_value(answer)
    return answers


def main() -> None:
    """Console script entrypoint.

    Route `cache` before Typer parses the scaffold Argument so that
    `create-awesome-python-app cache dir` works (Typer would otherwise
    treat `cache` as project_directory).
    """
    check_python_version(">=3.12", "create-awesome-python-app")
    _preprocess_cli_argv()
    if len(sys.argv) > 1 and sys.argv[1] == "cache":
        sys.argv = [sys.argv[0], *sys.argv[2:]]
        cache_app(prog_name="create-awesome-python-app cache")
        return
    app()


@app.command(name="create-awesome-python-app")
def scaffold(
    project_directory: str | None = typer.Argument("my-project"),
    version: bool = typer.Option(False, "--version"),
    info: bool = typer.Option(False, "--info", "-i"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
    template: str | None = typer.Option(None, "--template", "-t"),
    addons: list[str] | None = typer.Option(None, "--addons"),
    extend: list[str] | None = typer.Option(None, "--extend"),
    set_opt: list[str] | None = typer.Option(None, "--set"),
    no_install: bool = typer.Option(False, "--no-install"),
    force: bool = typer.Option(False, "--force", "-f"),
    interactive: bool | None = typer.Option(None, "--interactive/--no-interactive"),
    list_templates: bool = typer.Option(False, "--list-templates"),
    list_addons: bool = typer.Option(False, "--list-addons"),
    offline: bool = typer.Option(False, "--offline"),
    no_cache: bool = typer.Option(False, "--no-cache"),
    cache_dir: Path | None = typer.Option(None, "--cache-dir"),
    pin: str | None = typer.Option(None, "--pin"),
    refresh: str | None = typer.Option(None, "--refresh"),
    strict_version: bool = typer.Option(False, "--strict-version"),
    keep_on_failure: bool = typer.Option(False, "--keep-on-failure"),
    fixture: str | None = typer.Option(
        None,
        "--fixture",
        help=(
            "Load the template catalog from the local fixtures/ directory "
            "instead of the network (optional DIR = repo root; also "
            "CPA_FIXTURE_DIR / CPA_CATALOG_FIXTURE)"
        ),
    ),
) -> None:
    if version:
        console.print(__version__)
        raise typer.Exit(0)
    if info:
        print_env_info()

    # Translate --fixture into env vars before catalog loads
    # (--list-templates / interactive / scaffold).
    apply_fixture_mode(fixture)

    if list_templates or list_addons:
        from create_awesome_python_app.catalog import list_addons as la
        from create_awesome_python_app.catalog import list_templates as lt

        if list_templates:
            lt()
        if list_addons:
            la(template)
        raise typer.Exit(0)

    target_directory = project_directory or "my-project"
    # Fail before the interactive wizard so a leftover `my-project/` does not
    # waste a full prompt session (and so we exit cleanly, not with a traceback).
    if not force:
        try:
            assert_directory_is_empty(
                Path(target_directory).expanduser().resolve(), force=False
            )
        except NonEmptyTargetDirectoryError as err:
            console.print(f"[red]{err}[/red]")
            raise typer.Exit(1) from err

    effective_refresh = _normalize_refresh(refresh)
    if refresh and effective_refresh is None:
        console.print(
            "[red]Invalid --refresh mode: "
            f"'{refresh}'. Use one of: always, stale, manual.[/red]"
        )
        raise typer.Exit(2)

    # env wiring (#36)
    if no_cache:
        os.environ["CPA_NO_CATALOG_CACHE"] = "1"
        effective_refresh = effective_refresh or "always"
    if cache_dir:
        os.environ["CPA_CACHE_DIR"] = str(cache_dir)
    if effective_refresh:
        os.environ["CPA_REFRESH"] = effective_refresh
    if offline:
        pass  # passed to core

    want_interactive = interactive if interactive is not None else (not _in_ci())
    interactive_catalog: dict[str, object] | None = None
    if want_interactive and not template:
        try:
            import questionary
            from questionary import Choice

            from create_awesome_python_app.catalog import (
                CUSTOM_TEMPLATE_SENTINEL,
                build_template_choices,
                get_catalog_data,
            )
            from create_awesome_python_app.prompt_style import CPA_PROMPT_STYLE

            interactive_catalog = get_catalog_data()
            template_choices = build_template_choices(interactive_catalog)
            # select + type-to-filter: browseable list (CNA-style discovery)
            # instead of autocomplete-only. use_jk_keys must be False with search.
            selected_template = questionary.select(
                "Pick a template",
                choices=[
                    Choice(title=choice.title, value=choice.value)
                    for choice in template_choices
                ],
                qmark="?",
                pointer="❯",
                style=CPA_PROMPT_STYLE,
                use_search_filter=True,
                use_jk_keys=False,
                instruction="(↑↓ browse · type to filter · Enter)",
            ).ask()
            if selected_template == CUSTOM_TEMPLATE_SENTINEL:
                selected_template = questionary.text(
                    "Template URL",
                    default="file://.",
                    validate=lambda value: bool(value) or "Template URL is required",
                    style=CPA_PROMPT_STYLE,
                ).ask()
            template = selected_template
            if not template:
                raise typer.Exit(1)
        except ImportError:
            console.print("[red]questionary not available[/red]")
            raise typer.Exit(1) from None

    if not template:
        console.print("[red]--template is required in non-interactive mode[/red]")
        raise typer.Exit(2)

    set_map = _parse_set_options(set_opt)

    from create_awesome_python_app.catalog import (
        CatalogResolutionError,
        resolve_catalog_spec,
        resolve_catalog_specs,
    )

    try:
        template = resolve_catalog_spec(template)
        addons = resolve_catalog_specs(addons or [])
        extend = resolve_catalog_specs(extend or [])
    except CatalogResolutionError as err:
        console.print(f"[red]{err}[/red]")
        raise typer.Exit(2) from err

    if pin and "://" in template and "ref=" not in template:
        sep = "&" if "?" in template else "?"
        template = f"{template}{sep}ref={pin}"

    if want_interactive and not addons:
        try:
            import questionary
            from questionary import Choice

            from create_awesome_python_app.catalog import (
                build_extension_choices,
                get_catalog_data,
                group_extension_choices,
            )
            from create_awesome_python_app.prompt_style import CPA_PROMPT_STYLE

            interactive_catalog = interactive_catalog or get_catalog_data()
            extension_choices = build_extension_choices(interactive_catalog, template)
            grouped_extensions = group_extension_choices(extension_choices)
            if grouped_extensions:
                from create_awesome_python_app.catalog import (
                    CategoryInfo,
                    category_index,
                    format_category_choice_title,
                )

                categories = category_index(interactive_catalog)
                category_choices = [
                    Choice(
                        title=format_category_choice_title(
                            categories.get(category_slug)
                            or CategoryInfo(
                                slug=category_slug,
                                name=choices[0].category_name,
                            ),
                            len(choices),
                        ),
                        value=category_slug,
                    )
                    for category_slug, choices in grouped_extensions.items()
                ]
                selected_categories = questionary.checkbox(
                    "Which kinds of extensions do you need?",
                    choices=category_choices,
                    qmark="?",
                    pointer="❯",
                    style=CPA_PROMPT_STYLE,
                ).ask()
                selected_addons: list[str] = []
                for category_slug in selected_categories or []:
                    choices = grouped_extensions.get(str(category_slug), [])
                    if not choices:
                        continue
                    picked = questionary.checkbox(
                        f"{choices[0].category_name} extensions",
                        choices=[
                            Choice(title=choice.title, value=choice.value)
                            for choice in choices
                        ],
                        qmark="?",
                        pointer="❯",
                        style=CPA_PROMPT_STYLE,
                    ).ask()
                    selected_addons.extend(str(item) for item in picked or [])
                addons = selected_addons
        except ImportError:
            console.print("[red]questionary not available[/red]")
            raise typer.Exit(1) from None

    from create_awesome_python_app.catalog import (
        IncompatibleExtensionsError as CatalogIncompatibleExtensionsError,
    )
    from create_awesome_python_app.catalog import (
        get_catalog_data,
        validate_extension_compatibility,
    )

    try:
        validate_extension_compatibility(
            [*(addons or []), *(extend or [])],
            catalog=interactive_catalog or get_catalog_data(),
        )
    except CatalogIncompatibleExtensionsError as err:
        console.print(f"[red]{err}[/red]")
        raise typer.Exit(2) from err

    if want_interactive:
        try:
            from create_awesome_python_app.catalog import (
                find_template_by_url,
                get_catalog_data,
            )

            interactive_catalog = interactive_catalog or get_catalog_data()
            registry_options: list[dict[str, Any]] = []
            template_entry = find_template_by_url(interactive_catalog, template)
            if template_entry:
                raw_registry_options = (
                    template_entry.get("customOptions")
                    or template_entry.get("custom_options")
                    or []
                )
                if isinstance(raw_registry_options, list):
                    registry_options = [
                        item for item in raw_registry_options if isinstance(item, dict)
                    ]
            custom_answers = _prompt_custom_options(
                template,
                set_map=set_map,
                cache_dir=cache_dir,
                offline=offline,
                refresh=effective_refresh,
                registry_options=registry_options,
            )
        except ImportError:
            console.print("[red]questionary not available[/red]")
            raise typer.Exit(1) from None
        custom_answers.update(set_map)
        set_map = custom_answers

    # version check
    latest = asyncio.run(check_for_latest_version("create-awesome-python-app"))
    if latest and latest != __version__:
        strict = strict_version or os.environ.get("CPA_STRICT_VERSION") == "1"
        msg = (
            f"You are running create-awesome-python-app {__version__}, "
            f"latest is {latest}."
        )
        if strict:
            console.print(f"[red]{msg}[/red]")
            raise typer.Exit(1)
        console.print(f"[yellow]{msg}[/yellow]")

    try:
        asyncio.run(
            create_python_app(
                target_directory,
                {
                    "template": template,
                    "addons": addons or [],
                    "extend": extend or [],
                    "install": not no_install,
                    "force": force,
                    "verbose": verbose,
                    "offline": offline,
                    "refresh": effective_refresh,
                    "keep_on_failure": keep_on_failure,
                    "cache_dir": str(cache_dir) if cache_dir else None,
                    "set": set_map,
                },
            )
        )
    except NonEmptyTargetDirectoryError as err:
        # Safety net if the target fills up after the early check (e.g. during
        # a long interactive session).
        console.print(f"[red]{err}[/red]")
        raise typer.Exit(1) from err
    console.print(f"[green]Created[/green] {target_directory}")


@cache_app.command("dir")
def cache_dir_cmd() -> None:
    console.print(str(default_cache_dir()))


def _cache_json_print(payload: Any) -> None:
    """Print machine-readable JSON to stdout (not the stderr console)."""
    import json
    from dataclasses import asdict, is_dataclass

    def _to_jsonable(value: Any) -> Any:
        if isinstance(value, Path):
            return str(value)
        if is_dataclass(value) and not isinstance(value, type):
            return {k: _to_jsonable(v) for k, v in asdict(value).items()}
        if isinstance(value, list):
            return [_to_jsonable(item) for item in value]
        if isinstance(value, dict):
            return {k: _to_jsonable(v) for k, v in value.items()}
        return value

    typer.echo(json.dumps(_to_jsonable(payload), indent=2))


@cache_app.command("list")
def cache_list_cmd(
    json_out: bool = typer.Option(False, "--json", help="Output as JSON"),
) -> None:
    from create_awesome_python_app.cache import (
        format_age,
        format_bytes,
        list_cache_entries,
        short_sha,
    )

    entries = list_cache_entries()
    if json_out:
        _cache_json_print(entries)
        return
    if not entries:
        console.print("[dim]No cached templates or extensions.[/dim]")
        console.print(
            f"[dim]Cache root: {default_cache_dir()}\n"
            "Run 'create-awesome-python-app my-app -t <template>' to populate it.[/dim]"
        )
        return
    id_width = max(2, *(len(e.id) for e in entries))
    console.print(
        f"{'ID'.ljust(id_width)}  "
        f"{'URL'.ljust(50)}  "
        f"{'REF'.ljust(8)}  "
        f"{'LAST FETCHED'.ljust(14)}  "
        f"{'SHA'.ljust(8)}  "
        "SIZE"
    )
    for entry in entries:
        url = (entry.url or "—")[:50].ljust(50)
        ref = (entry.ref or "—")[:8].ljust(8)
        console.print(
            f"[cyan]{entry.id.ljust(id_width)}[/cyan]  "
            f"[dim]{url}[/dim]  "
            f"[dim]{ref}[/dim]  "
            f"[dim]{format_age(entry.fetched_at).ljust(14)}[/dim]  "
            f"[dim]{short_sha(entry.commit).ljust(8)}[/dim]  "
            f"[dim]{format_bytes(entry.size_bytes)}[/dim]"
        )
    console.print(f"[dim]\nCache root: {default_cache_dir()}[/dim]")


@cache_app.command("clean")
def cache_clean_cmd(
    id: str | None = typer.Argument(None),
    catalog: bool = typer.Option(False, "--catalog"),
    json_out: bool = typer.Option(False, "--json", help="Output as JSON"),
    force: bool = typer.Option(
        False, "--force", "-f", help="Skip interactive confirmation"
    ),
) -> None:
    from create_awesome_python_app.cache import clean_cache

    # Targeted cleans (id / --catalog) never prompt.
    if not catalog and id is None and not json_out and not force:
        if not sys.stdin.isatty():
            console.print(
                "[yellow]Non-interactive shell — use --json or --force to skip "
                "the prompt, or specify an id to target a specific entry.[/yellow]"
            )
            return
        import questionary

        from create_awesome_python_app.prompt_style import CPA_PROMPT_STYLE

        confirmed = questionary.confirm(
            "Remove ALL cached templates and extensions?",
            default=False,
            style=CPA_PROMPT_STYLE,
        ).ask()
        if not confirmed:
            console.print("[dim]Clean cancelled.[/dim]")
            return

    result = clean_cache(id, catalog=catalog)
    if json_out:
        _cache_json_print(result)
        return
    if result.not_found:
        console.print(f"[yellow]No cache entry found for id: {id}[/yellow]")
        return
    if not result.removed:
        console.print("[dim]Nothing to remove.[/dim]")
        return
    for path in result.removed:
        console.print(f"[green]✓ Removed {path}[/green]")


@cache_app.command("verify")
def cache_verify_cmd(
    id: str | None = typer.Argument(None),
    json_out: bool = typer.Option(False, "--json", help="Output as JSON"),
) -> None:
    from create_awesome_python_app.cache import verify_cache

    results = verify_cache(id)
    if json_out:
        _cache_json_print(results)
        if any(not bool(entry.fsck_ok) for entry in results):
            raise typer.Exit(1)
        raise typer.Exit(0)
    if not results:
        console.print("[dim]No cached entries.[/dim]")
        raise typer.Exit(0)
    all_ok = True
    for entry in results:
        ok = bool(entry.fsck_ok)
        if not ok:
            all_ok = False
        mark = "[green]✓[/green]" if ok else "[red]✗[/red]"
        console.print(f"{mark} [cyan]{entry.id}[/cyan]  [dim]{entry.url or '—'}[/dim]")
    if not all_ok:
        console.print()
        console.print(
            "[red]Some entries failed git fsck. "
            "Consider 'create-awesome-python-app cache clean' and re-run.[/red]"
        )
        raise typer.Exit(1)


@cache_app.command("outdated")
def cache_outdated_cmd(
    json_out: bool = typer.Option(False, "--json", help="Output as JSON"),
) -> None:
    from create_awesome_python_app.cache import check_outdated

    results = check_outdated()
    if json_out:
        _cache_json_print(results)
        return
    if not results:
        console.print("[dim]No cached entries to check.[/dim]")
        return
    id_width = max(2, *(len(r.id) for r in results))
    behind_count = 0
    for row in results:
        if row.error:
            console.print(
                f"[dim]?[/dim] [cyan]{row.id.ljust(id_width)}[/cyan]  "
                f"[dim]{row.error}[/dim]"
            )
            continue
        icon = "[yellow]▼[/yellow]" if row.behind else "[green]✓[/green]"
        local = (row.local_sha or "—")[:7]
        remote = (row.remote_sha or "—")[:7]
        console.print(
            f"{icon} [cyan]{row.id.ljust(id_width)}[/cyan]  "
            f"local={local}  remote={remote}"
        )
        if row.behind:
            behind_count += 1
    if behind_count:
        noun = "entry is" if behind_count == 1 else "entries are"
        console.print(
            f"[yellow]\n{behind_count} {noun} behind remote. "
            "Run 'create-awesome-python-app cache update [id]' to refresh.[/yellow]"
        )


@cache_app.command("update")
def cache_update_cmd(id: str | None = typer.Argument(None)) -> None:
    from create_awesome_python_app.cache import list_cache_entries, update_cache

    entries = list_cache_entries()
    targets = [e for e in entries if e.id == id] if id else entries
    if not targets:
        label = f"y matching '{id}'" if id else "ies"
        console.print(f"[dim]No cached entr{label} found.[/dim]")
        raise typer.Exit(0)

    updated, failed = update_cache(id)
    by_id = {e.id: e for e in targets}
    for entry_id in updated:
        entry = by_id.get(entry_id)
        console.print(
            f"[green]✓[/green] [cyan]{entry_id}[/cyan]  "
            f"[dim]{entry.url if entry else ''}[/dim]"
        )
    for entry_id in failed:
        entry = by_id.get(entry_id)
        detail = "missing url or refresh failed"
        if entry and not entry.url:
            detail = "missing url in meta"
        console.print(f"[red]✗[/red] [cyan]{entry_id}[/cyan]  [dim]{detail}[/dim]")
    if failed:
        raise typer.Exit(1)


@cache_app.command("doctor")
def cache_doctor_cmd(
    json_out: bool = typer.Option(False, "--json", help="Output as JSON"),
) -> None:
    from create_awesome_python_app.cache import run_doctor

    results = run_doctor()
    if json_out:
        _cache_json_print(results)
        if any(not row.ok for row in results):
            raise typer.Exit(1)
        raise typer.Exit(0)
    all_ok = True
    for row in results:
        mark = "[green]✓[/green]" if row.ok else "[red]✗[/red]"
        console.print(f"{mark} {row.check}: {row.detail}")
        if not row.ok:
            all_ok = False
    if not all_ok:
        raise typer.Exit(1)
