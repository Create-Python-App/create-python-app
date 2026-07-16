"""Programmatic scaffolding engine for Create Awesome Python App."""

from __future__ import annotations

from create_python_app_core._version import __version__
from create_python_app_core.api import (
    CPA_USER_AGENT,
    check_for_latest_version,
    check_python_version,
    create_python_app,
    print_env_info,
)
from create_python_app_core.config import (
    CpaConfig,
    CpaCustomOption,
    assert_directory_is_empty,
    load_cpa_config,
)
from create_python_app_core.errors import (
    NON_EMPTY_DIR_ERROR_CODE,
    ConfigParseError,
    CpaError,
    ManifestLoadError,
    NonEmptyTargetDirectoryError,
    PackageManagerFallbackError,
    ScaffoldAbortedError,
)
from create_python_app_core.git_cache import (
    CacheMeta,
    download_repository,
    read_cache_meta,
    write_cache_meta,
)
from create_python_app_core.installer import scaffold_project
from create_python_app_core.loaders import load_layer, merge_layers
from create_python_app_core.paths import (
    default_cache_dir,
    get_template_dir_path,
    resolve_source,
)
from create_python_app_core.pyproject_merge import merge_pyproject_text

__all__ = [
    "__version__",
    "CpaError",
    "ConfigParseError",
    "ManifestLoadError",
    "PackageManagerFallbackError",
    "ScaffoldAbortedError",
    "NonEmptyTargetDirectoryError",
    "NON_EMPTY_DIR_ERROR_CODE",
    "default_cache_dir",
    "resolve_source",
    "download_repository",
    "CacheMeta",
    "read_cache_meta",
    "write_cache_meta",
    "merge_layers",
    "load_layer",
    "merge_pyproject_text",
    "get_template_dir_path",
    "CpaConfig",
    "CpaCustomOption",
    "load_cpa_config",
    "assert_directory_is_empty",
    "scaffold_project",
    "CPA_USER_AGENT",
    "check_for_latest_version",
    "check_python_version",
    "create_python_app",
    "print_env_info",
]
