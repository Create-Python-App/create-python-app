# create-awesome-python-app

![banner](./assets/hero.svg)

CLI package. Framework: **Typer** (chosen over Click for richer typing/help).

```bash
uv run create-awesome-python-app --help
uvx create-awesome-python-app@latest my-app   # after PyPI publish
pipx run create-awesome-python-app my-app
```

## Shell completion

Typer installs completion scripts for bash, zsh, and fish:

```bash
# Interactive install into your shell profile
create-awesome-python-app --install-completion

# Or print the script and source it manually
create-awesome-python-app --show-completion
```

After installing, restart the shell (or `source` your profile) and tab-complete
flags such as `--template`, `--addons`, and `cache` subcommands.
