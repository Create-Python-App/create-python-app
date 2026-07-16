"""Typer CLI entrypoint for create-awesome-python-app."""

from __future__ import annotations

import asyncio

import typer
from create_python_app_core import (
    check_python_version,
    create_python_app,
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
console = Console(stderr=True)


def main() -> None:
    """Console script entrypoint."""
    check_python_version(">=3.12", "create-awesome-python-app")
    app()


@app.callback(invoke_without_command=True)
def scaffold(
    ctx: typer.Context,
    project_directory: str | None = typer.Argument("my-project"),
    version: bool = typer.Option(False, "--version", help="Show version"),
    info: bool = typer.Option(False, "--info", "-i", help="Print env info"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
    template: str | None = typer.Option(None, "--template", "-t"),
    no_install: bool = typer.Option(False, "--no-install"),
    force: bool = typer.Option(False, "--force", "-f"),
) -> None:
    """Scaffold a new Python project (flags expand in later issues)."""
    if version:
        console.print(__version__)
        raise typer.Exit(0)
    if info:
        print_env_info()
    if ctx.invoked_subcommand is not None:
        return
    if not template:
        console.print(
            "[yellow]Stub CLI[/yellow]: pass --template "
            "(full interactive mode lands in #34)."
        )
        console.print(f"Would scaffold [cyan]{project_directory}[/cyan]")
        raise typer.Exit(0)

    asyncio.run(
        create_python_app(
            project_directory or "my-project",
            {
                "template": template,
                "install": not no_install,
                "force": force,
                "verbose": verbose,
            },
        )
    )
    console.print(f"[green]Created[/green] {project_directory}")


@app.command("cache")
def cache_placeholder() -> None:
    """Cache management (subcommands land in #37)."""
    console.print("cache subcommands: see #37")
