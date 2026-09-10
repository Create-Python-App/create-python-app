# Shell completion

`create-awesome-python-app` ships tab completion via Typer (bash, zsh, fish,
PowerShell). Completion covers flags and the `cache` subcommands; catalog
values (template slugs) are intentionally not completed yet.

## Quick install

```bash
# Detect the current shell from $SHELL and install
create-awesome-python-app --install-completion
```

Restart the shell (or `exec "$SHELL" -l`) so the new script loads.

## Manual install per shell

```bash
# bash — append to ~/.bashrc
create-awesome-python-app --show-completion >> ~/.bash_completion
# zsh — needs compinit; save to a fpath entry
create-awesome-python-app --show-completion > ~/.zfunc/_create-awesome-python-app
# fish
create-awesome-python-app --show-completion > ~/.config/fish/completions/create-awesome-python-app.fish
# PowerShell — append to $PROFILE
create-awesome-python-app --show-completion >> $PROFILE
```

If you see `Shell sh not supported`, export a real shell first
(`export SHELL=/bin/bash`) — completion detection reads `$SHELL`.

## uvx users

Completion attaches to the shell, not the installer, so it works the same
under `uvx create-awesome-python-app`. Run `--install-completion` once with
any installed copy.
