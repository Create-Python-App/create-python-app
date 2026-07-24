# create-python-app-core

[![Discord](https://img.shields.io/discord/1527933660764831825?label=Discord&logo=discord&logoColor=white)](https://discord.gg/bR5VyATgka)

Programmatic scaffolding engine behind Create Awesome Python App.
Import the scaffolding pipeline -- composable, headless, and CI-ready.

Requires **Python >= 3.12**.

> This is the _engine_ package. For the interactive CLI, use
> [`create-awesome-python-app`](https://pypi.org/project/create-awesome-python-app/)
> instead.

---

## Installation

```bash
pip install create-python-app-core
```

Or with uv:

```bash
uv add create-python-app-core
```

---

## Usage

### Scaffold a project programmatically

```python
import asyncio
from create_python_app_core import create_python_app


async def main() -> None:
    await create_python_app(
        "my-app",
        {
            "projectName": "my-app",
            "template": "file:///path/to/template",
            "install": True,
        },
        transform_options=lambda opts: asyncio.sleep(0, result=opts),
    )


asyncio.run(main())
```

### Scaffold with the installer API

```python
from create_python_app_core import scaffold_project

scaffold_project(
    "my-app",
    template="file:///path/to/template",
    addons=[],
    extend=[],
    install=True,
    force=False,
    offline=False,
)
```

### Resolve a template source

```python
from create_python_app_core import resolve_source, get_template_dir_path

source = resolve_source(
    "https://github.com/Create-Python-App/cpa-templates?ref=main&subdir=fastapi"
)
print(source.kind)  # github
print(source.ref)  # main
print(source.subdir)  # fastapi
```

### Download a repository into the cache

```python
from create_python_app_core import resolve_source, download_repository

source = resolve_source("https://github.com/org/my-template")
root = download_repository(source, refresh="stale", offline=False)
template_dir = get_template_dir_path(source, root)
```

### Load template configuration

```python
from pathlib import Path

from create_python_app_core import load_cpa_config

cfg = load_cpa_config(Path("/path/to/template/cpa.config.json"))
for opt in cfg.custom_options:
    print(opt.key, opt.default)
```

### Check environment info

```python
from create_python_app_core import print_env_info

print_env_info()
# Prints Python, platform, uv, and git info. Then exits.
```

### Validate the Python version

```python
from create_python_app_core import check_python_version

check_python_version(">=3.12", "my-tool")
# Exits with code 1 if the interpreter does not match.
```

---

## API Reference

All public exports from `create_python_app_core`:

### Functions

| Signature | Description |
| --------- | ----------- |
| `create_python_app(project_directory, options, transform_options=None)` | Async orchestrator. Applies `transform_options`, then delegates to `scaffold_project`. |
| `scaffold_project(project_directory, *, template, addons=None, extend=None, force=False, install=True, offline=False, refresh=None, keep_on_failure=False, cache_dir=None, options=None)` | Main scaffolding pipeline. Resolves sources, downloads layers, merges files, runs `uv sync`, and initializes git. |
| `resolve_source(spec, *, cache_dir=None)` | Parses a template/extension specifier (GitHub URL, `file://`, slug) into a `ResolvedSource`. |
| `get_template_dir_path(source, root)` | Returns the `template/` subdirectory when present, otherwise the resolved root. |
| `default_cache_dir()` | Returns `CPA_CACHE_DIR` or `~/.cache/cpa`. |
| `download_repository(source, *, offline=False, refresh=None, cache_root=None)` | Clones or refreshes a Git repo into the cache. Returns the entry directory. |
| `read_cache_meta(entry)` | Reads `.cpa-cache.json` metadata from a cache entry. |
| `write_cache_meta(entry, meta)` | Writes `.cpa-cache.json` metadata for a cache entry. |
| `load_cpa_config(path)` | Loads optional `cpa.config.json` (custom CLI prompts). Returns empty `CpaConfig` when missing. |
| `assert_directory_is_empty(path, *, force=False)` | Raises `NonEmptyTargetDirectoryError` when the target exists and is non-empty. |
| `load_layer(source, root, dest, *, overwrite=True, context=None)` | Copies one template/extension layer into `dest`. |
| `merge_layers(layers, dest, *, context=None)` | Applies layers in order (template, addons, extend). Later layers win. |
| `merge_pyproject_text(base_text, overlay_text)` | Deep-merges two `pyproject.toml` documents as TOML. |
| `check_python_version(required, package_name)` | Compares `sys.version_info` against a PEP 440 specifier. Exits with code 1 if too old. |
| `check_for_latest_version(package_name)` | Async. Fetches the latest version from PyPI. Returns `None` on failure. |
| `print_env_info()` | Prints OS, Python, uv, and git info to stdout, then exits. |

### Constants

| Name | Description |
| ---- | ----------- |
| `__version__` | Installed package version string. |
| `CPA_USER_AGENT` | HTTP User-Agent sent to PyPI (`create-python-app-core/<version>`). |
| `NON_EMPTY_DIR_ERROR_CODE` | Stable code for `NonEmptyTargetDirectoryError` (`CPA_NON_EMPTY_TARGET_DIR`). |

### Types

| Type | Shape |
| ---- | ----- |
| `ResolvedSource` | `kind` (github \| file \| slug \| git), `url`, `ref`, `subdir`, `local_path` |
| `CacheMeta` | `url`, `ref`, `fetched_at`, `commit` |
| `CpaConfig` | `name`, `custom_options`, `raw` |
| `CpaCustomOption` | `key`, `type`, `message`, `default` |
| `CpaError` | Base exception with `.code` attribute |
| `ConfigParseError` | Invalid `cpa.config.json` (code: `CPA_CONFIG_PARSE`) |
| `ManifestLoadError` | Missing template directory (code: `CPA_MANIFEST_LOAD`) |
| `PackageManagerFallbackError` | Package manager fallback failure (code: `CPA_PM_FALLBACK`) |
| `ScaffoldAbortedError` | Scaffold failed mid-run (code: `CPA_ABORTED`) |
| `NonEmptyTargetDirectoryError` | Target directory not empty (code: `CPA_NON_EMPTY_TARGET_DIR`) |

### `create_python_app` options dict

| Key | Type | Default | Description |
| --- | ---- | ------- | ----------- |
| `template` | `str` | `""` | Primary template specifier (URL, `file://`, or slug). |
| `addons` | `list[str]` | `[]` | Additional template layers applied after the base template. |
| `extend` | `list[str]` | `[]` | Extension layers applied last (later wins on conflicts). |
| `force` | `bool` | `False` | Allow scaffolding into a non-empty directory. |
| `install` | `bool` | `True` | Run `uv sync` when `pyproject.toml` is present. |
| `offline` | `bool` | `False` | Use cached repos only; raise on cache miss. |
| `refresh` | `str` | env / `"stale"` | Cache refresh mode: `always`, `stale`, or `manual`. |
| `keep_on_failure` | `bool` | `False` | Keep the partial project directory when scaffolding fails. |
| `cache_dir` | `str \| Path` | `None` | Override the default cache root. |
| `set` | `dict` | `{}` | Jinja context overrides (merged into `projectName` and custom option defaults). |

---

## Environment Variables

All `CPA_*` variables read by the core engine:

| Variable | Default | Description |
| -------- | ------- | ----------- |
| `CPA_CACHE_DIR` | `~/.cache/cpa` | Root directory for cloned repository cache entries. |
| `CPA_REFRESH` | `stale` | Default cache refresh mode: `always`, `stale`, or `manual`. |
| `CPA_REFRESH_AFTER_HOURS` | `24` | Hours before a `stale` cache entry is refreshed. |
| `CPA_SKIP_GIT` | unset | Set to `1` to skip `git init` and block all git subprocess calls. |
| `CPA_STRICT_REPRO` | unset | Set to `1` to require a full 40-character commit SHA in `?ref=` query params. |

---

## Error Codes

Stable machine-readable codes on `CpaError.code`:

| Code | Exception class | When raised |
| ---- | --------------- | ----------- |
| `CPA_ERROR` | `CpaError` | Generic base error (default). |
| `CPA_CONFIG_PARSE` | `ConfigParseError` | Malformed or invalid `cpa.config.json`. |
| `CPA_MANIFEST_LOAD` | `ManifestLoadError` | Template directory not found on disk. |
| `CPA_PM_FALLBACK` | `PackageManagerFallbackError` | Package manager fallback failure. |
| `CPA_ABORTED` | `ScaffoldAbortedError` | Scaffold failed (template render, unexpected error, etc.). |
| `CPA_NON_EMPTY_TARGET_DIR` | `NonEmptyTargetDirectoryError` | Target directory exists and is not empty. |
| `CPA_GIT` | `CpaError` | Git subprocess failed or `git` not found. |
| `CPA_SKIP_GIT` | `CpaError` | Git operation attempted while `CPA_SKIP_GIT=1`. |
| `CPA_FILE` | `CpaError` | `file://` source path does not exist. |
| `CPA_OFFLINE` | `CpaError` | Offline mode with no cached copy of the repository. |
| `CPA_STRICT_REPRO` | `CpaError` | `?ref=` is not a full SHA while `CPA_STRICT_REPRO=1`. |

---

## How It Works

```text
create_python_app()
  |-- transform_options() (optional)
  |-- scaffold_project()
        |-- assert_directory_is_empty()
        |-- resolve_source() for each template / addon / extend
        |-- download_repository() (git clone or file://)
        |-- load_cpa_config() from cpa.config.json
        |-- build_scaffold_context() (projectName + custom options + --set)
        |-- merge_layers() (Jinja .template, .append, pyproject merge)
        |-- uv sync (when install=True and pyproject.toml exists)
        |-- git init (unless CPA_SKIP_GIT=1)
        +-- cleanup partial directory on failure (unless keep_on_failure)
```

---

## Architecture

The package is organized into these modules:

| Module | Responsibility |
| ------ | -------------- |
| `__init__.py` | Barrel export and public API surface |
| `api.py` | `create_python_app`, version checks, env info, PyPI lookup |
| `installer.py` | `scaffold_project` orchestration, `uv sync`, git init |
| `loaders.py` | File discovery, `.template` / `.append` processing, layer merge |
| `pyproject_merge.py` | Deep-merge `pyproject.toml` across template layers |
| `paths.py` | URL resolution (GitHub, `file://`, slugs, `?ref=`, `?subdir=`) |
| `git_cache.py` | Clone/pull with cache, refresh modes, offline support |
| `config.py` | Reads optional `cpa.config.json` for custom CLI prompts |
| `errors.py` | Typed `CpaError` hierarchy with stable codes |

---

## Related

- [`create-awesome-python-app`](https://pypi.org/project/create-awesome-python-app/) -- Interactive CLI built on this core
- [Create Python App](https://github.com/Create-Python-App/create-python-app) -- Monorepo
- [Templates catalog](https://github.com/Create-Python-App/cpa-templates)

---

## License

MIT (c) [Create Python App Contributors](https://github.com/Create-Python-App/create-python-app/graphs/contributors)
