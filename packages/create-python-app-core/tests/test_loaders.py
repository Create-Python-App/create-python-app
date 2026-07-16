from pathlib import Path

from create_python_app_core.loaders import merge_layers
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
