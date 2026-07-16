from pathlib import Path

import pytest
from create_python_app_core.errors import ScaffoldAbortedError
from create_python_app_core.loaders import merge_layers, process_file, render_template
from create_python_app_core.paths import ResolvedSource


def _layer(tmp: Path, name: str, files: dict[str, str]) -> tuple[ResolvedSource, Path]:
    root = tmp / name
    tpl = root / "template"
    for rel, content in files.items():
        path = tpl / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    src = ResolvedSource(kind="file", url=f"file://{root}", local_path=root)
    return src, root


def test_merge_later_wins(tmp_path: Path) -> None:
    a = _layer(tmp_path, "a", {"README.md": "a", "keep.txt": "keep"})
    b = _layer(tmp_path, "b", {"README.md": "b"})
    dest = tmp_path / "out"
    merge_layers([a, b], dest)
    assert (dest / "README.md").read_text() == "b"
    assert (dest / "keep.txt").read_text() == "keep"


def test_template_renders_and_strips_suffix(tmp_path: Path) -> None:
    layer = _layer(
        tmp_path,
        "t",
        {"README.md.template": "Hello {{ projectName }}!\n"},
    )
    dest = tmp_path / "out"
    merge_layers([layer], dest, context={"projectName": "demo"})
    assert (dest / "README.md").read_text() == "Hello demo!\n"
    assert not (dest / "README.md.template").exists()


def test_append_concatenates(tmp_path: Path) -> None:
    a = _layer(tmp_path, "a", {"notes.txt": "one\n"})
    b = _layer(tmp_path, "b", {"notes.txt.append": "two\n"})
    dest = tmp_path / "out"
    merge_layers([a, b], dest)
    assert (dest / "notes.txt").read_text() == "one\ntwo\n"


def test_append_template(tmp_path: Path) -> None:
    a = _layer(tmp_path, "a", {".env.example": "A=1\n"})
    b = _layer(
        tmp_path,
        "b",
        {".env.example.append.template": "NAME={{ projectName }}\n"},
    )
    dest = tmp_path / "out"
    merge_layers([a, b], dest, context={"projectName": "api"})
    assert (dest / ".env.example").read_text() == "A=1\nNAME=api\n"


def test_strict_undefined_raises() -> None:
    with pytest.raises(ScaffoldAbortedError, match="Template render failed"):
        render_template("{{ missing }}", {}, path="x.template")


def test_process_file_copy(tmp_path: Path) -> None:
    src = tmp_path / "a.txt"
    src.write_text("x")
    dest = tmp_path / "out"
    written = process_file(src, dest, Path("a.txt"), context={})
    assert written == dest / "a.txt"
    assert (dest / "a.txt").read_text() == "x"
