from create_python_app_core import (
    NON_EMPTY_DIR_ERROR_CODE,
    ConfigParseError,
    CpaError,
    NonEmptyTargetDirectoryError,
)


def test_error_codes_use_cpa_prefix() -> None:
    assert ConfigParseError("x").code.startswith("CPA_")
    assert NonEmptyTargetDirectoryError("x").code == NON_EMPTY_DIR_ERROR_CODE
    assert isinstance(ConfigParseError("x"), CpaError)
