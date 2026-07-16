"""Typed CPA errors (mirrors create-node-app-core/errors.ts)."""

from __future__ import annotations


class CpaError(Exception):
    """Base error with a stable machine-readable code."""

    code: str = "CPA_ERROR"

    def __init__(self, message: str, *, code: str | None = None) -> None:
        super().__init__(message)
        if code is not None:
            self.code = code


class ConfigParseError(CpaError):
    code = "CPA_CONFIG_PARSE"


class ManifestLoadError(CpaError):
    code = "CPA_MANIFEST_LOAD"


class PackageManagerFallbackError(CpaError):
    code = "CPA_PM_FALLBACK"


class ScaffoldAbortedError(CpaError):
    code = "CPA_ABORTED"


class NonEmptyTargetDirectoryError(CpaError):
    code = "CPA_NON_EMPTY_TARGET_DIR"


NON_EMPTY_DIR_ERROR_CODE = NonEmptyTargetDirectoryError.code
