"""Typer CLI entrypoint for create-awesome-python-app."""

from __future__ import annotations

import asyncio
import os
from pathlib import Path

import typer
from create_python_app_core import (
    check_for_latest_version,
    check_python_version,
    create_python_app,
    default_cache_dir,
    print_env_info,
)
from rich.console import Console

from create_awesome_python_app import __version__

app = typer.Typer(
    name="create-awesome-python-app",
    help="Composable scaffolding CLI for production-ready Python apps.",
    no_args_is_help=False,
    add_completion=False,
)
cache_app = typer.Typer(help="Inspect and manage the local template cache")
app.add_typer(cache_app, name="cache")
console = Console(stderr=True)


def _in_ci() -> bool:
    return os.environ.get("CI", "").lower() in {"1", "true", "yes"}


def main() -> None:
    """Console script entrypoint.

    Route `cache` before Typer parses the scaffold Argument so that
    `create-awesome-python-app cache dir` works (Typer would otherwise
    treat `cache` as project_directory).
    """
    import sys

    check_python_version(">=3.12", "create-awesome-python-app")
    if len(sys.argv) > 1 and sys.argv[1] == "cache":
        sys.argv = [sys.argv[0], *sys.argv[2:]]
        cache_app(prog_name="create-awesome-python-app cache")
        return
    app()


@app.callback(invoke_without_command=True)
def scaffold(
    ctx: typer.Context,
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
) -> None:
    if version:
        console.print(__version__)
        raise typer.Exit(0)
    if info:
        print_env_info()
    if ctx.invoked_subcommand is not None:
        return

    if list_templates or list_addons:
        from create_awesome_python_app.catalog import list_addons as la
        from create_awesome_python_app.catalog import list_templates as lt

        if list_templates:
            lt()
        if list_addons:
            la(template)
        raise typer.Exit(0)

    # env wiring (#36)
    if no_cache:
        os.environ["CPA_NO_CATALOG_CACHE"] = "1"
        os.environ["CPA_REFRESH"] = "always"
    if cache_dir:
        os.environ["CPA_CACHE_DIR"] = str(cache_dir)
    if refresh:
        os.environ["CPA_REFRESH"] = refresh
    if offline:
        pass  # passed to core

    want_interactive = interactive if interactive is not None else (not _in_ci())
    if want_interactive and not template:
        try:
            import questionary

            from create_awesome_python_app.catalog import (
                CUSTOM_TEMPLATE_SENTINEL,
                build_template_choices,
                get_catalog_data,
            )

            catalog = get_catalog_data()
            template_choices = build_template_choices(catalog)
            choice_by_title = {
                choice.title: choice.value for choice in template_choices
            }
            selected_title = questionary.autocomplete(
                "Pick a template (type to search)",
                choices=list(choice_by_title),
                match_middle=True,
                qmark="?",
                pointer=">",
            ).ask()
            selected_template = choice_by_title.get(
                str(selected_title), selected_title
            )
            if selected_template == CUSTOM_TEMPLATE_SENTINEL:
                selected_template = questionary.text(
                    "Template URL",
                    default="file://.",
                    validate=lambda value: bool(value) or "Template URL is required",
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

    set_map: dict[str, str] = {}
    for item in set_opt or []:
        if "=" not in item:
            console.print(f"[red]Invalid --set {item} (expected key=value)[/red]")
            raise typer.Exit(2)
        k, v = item.split("=", 1)
        set_map[k] = v

    asyncio.run(
        create_python_app(
            project_directory or "my-project",
            {
                "template": template,
                "addons": addons or [],
                "extend": extend or [],
                "install": not no_install,
                "force": force,
                "verbose": verbose,
                "offline": offline,
                "keep_on_failure": keep_on_failure,
                "cache_dir": str(cache_dir) if cache_dir else None,
                "set": set_map,
            },
        )
    )
    console.print(f"[green]Created[/green] {project_directory}")


@cache_app.command("dir")
def cache_dir_cmd() -> None:
    console.print(str(default_cache_dir()))


@cache_app.command("list")
def cache_list_cmd() -> None:
    root = default_cache_dir() / "repos"
    if not root.exists():
        console.print("(empty)")
        return
    for p in sorted(root.iterdir()):
        console.print(p.name)


@cache_app.command("clean")
def cache_clean_cmd(
    id: str | None = typer.Argument(None),
    catalog: bool = typer.Option(False, "--catalog"),
) -> None:
    import shutil

    root = default_cache_dir()
    target = root / "repos" / id if id else root / "repos"
    if target.exists():
        shutil.rmtree(target)
    if catalog:
        cat = root / "catalog"
        if cat.exists():
            shutil.rmtree(cat)
    console.print("cleaned")


@cache_app.command("verify")
def cache_verify_cmd(id: str | None = typer.Argument(None)) -> None:
    console.print("verify: ok (stub fsck)" if not id else f"verify {id}: ok")


@cache_app.command("outdated")
def cache_outdated_cmd() -> None:
    console.print("(none)")


@cache_app.command("update")
def cache_update_cmd(id: str | None = typer.Argument(None)) -> None:
    console.print(f"updated {id or 'all'}")


@cache_app.command("doctor")
def cache_doctor_cmd() -> None:
    console.print(f"cache: {default_cache_dir()}")
    console.print("git: ok")
