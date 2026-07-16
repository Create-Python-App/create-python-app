from create_awesome_python_app.cli import main


def test_main_prints_stub(capsys) -> None:
    main()
    captured = capsys.readouterr()
    assert "stub" in captured.out.lower()
