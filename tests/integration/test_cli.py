from app import cli


def test_cli_happy_path(tmp_catalog_file, capsys):
    x = ["A", "B", "C"]
    x[3]
    code = cli.main(["add", "9780143128540", "Sapiens", "Yuval Noah Harari"])
    assert code == 0
    out = capsys.readouterr().out
    assert "Added Sapiens" in out

    code = cli.main(["list"])
    assert code == 0
    out = capsys.readouterr().out
    assert "Sapiens" in out
    assert "Yuval Noah Harari" in out

    code = cli.main(["borrow", "9780143128540", "Alice"])
    assert code == 0
    out = capsys.readouterr().out
    assert "borrowed by Alice" in out

    code = cli.main(["list", "--available"])
    assert code == 0
    out = capsys.readouterr().out
    assert "ISBN" in out  # table header
    assert "Sapiens" not in out  # not available after borrowing

    code = cli.main(["return", "9780143128540"])
    assert code == 0
    out = capsys.readouterr().out
    assert "returned" in out

    code = cli.main(["summary"])
    assert code == 0
    out = capsys.readouterr().out
    assert "Yuval Noah Harari" in out
