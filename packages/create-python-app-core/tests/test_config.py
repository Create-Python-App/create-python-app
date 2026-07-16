import json
from pathlib import Path

import pytest
from create_python_app_core.config import assert_directory_is_empty, load_cpa_config
from create_python_app_core.errors import ConfigParseError, NonEmptyTargetDirectoryError


def test_load_config(tmp_path: Path) -> None:
    path = tmp_path / "cpa.config.json"
    path.write_text(
        json.dumps(
            {
                "name": "demo",
                "customOptions": [{"key": "projectName", "default": "x"}],
            }
        )
    )
    cfg = load_cpa_config(path)
    assert cfg.name == "demo"
    assert cfg.custom_options[0].key == "projectName"


def test_bad_json(tmp_path: Path) -> None:
    path = tmp_path / "cpa.config.json"
    path.write_text("{")
    with pytest.raises(ConfigParseError):
        load_cpa_config(path)


def test_non_empty(tmp_path: Path) -> None:
    (tmp_path / "f").write_text("x")
    with pytest.raises(NonEmptyTargetDirectoryError):
        assert_directory_is_empty(tmp_path)
    assert_directory_is_empty(tmp_path, force=True)
