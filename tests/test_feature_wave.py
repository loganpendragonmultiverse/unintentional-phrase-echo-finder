import json

import pytest

from phrase_echo_finder.cli import main
from phrase_echo_finder.core import analyze

TEXT = "Silver rain crossed the window. Other violet stars shine. Silver rain crossed the window. Other violet stars shine."


def test_exact_normalized_allowlist_before_limit(tmp_path, capsys):
    args = {"min_words": 3, "max_words": 5, "min_characters": 1, "limit": 1}
    original = analyze(TEXT, **args)
    phrase = original["echoes"][0]["phrase"]
    allowed = analyze(TEXT, **args, allowlist=[phrase.upper().replace(" ", ", ")])
    assert allowed["echo_count"] == 1
    assert allowed["echoes"][0]["phrase"] != phrase
    assert analyze(TEXT, **args, allowlist=[]) == original
    assert analyze(TEXT, **args, allowlist=["silver rain crossed"]) == original
    assert analyze(TEXT, **args, allowlist=["silver rain crossed the window again"]) == original
    source = tmp_path / "story.txt"
    source.write_text(TEXT)
    file = tmp_path / "allow.json"
    file.write_text(json.dumps([phrase]))
    assert (
        main(
            [
                str(source),
                "--allowlist",
                str(file),
                "--format",
                "json",
                "--limit",
                "1",
                "--max-words",
                "5",
                "--min-characters",
                "1",
            ]
        )
        == 0
    )
    assert json.loads(capsys.readouterr().out)["echoes"][0]["phrase"] != phrase
    assert source.read_text() == TEXT


@pytest.mark.parametrize("bad", [{}, "phrase", [None], [""], ["!!!"], [1]])
def test_malformed_allowlist(bad, tmp_path, capsys):
    with pytest.raises((TypeError, ValueError), match="allowlist"):
        analyze(TEXT, allowlist=bad)
    source = tmp_path / "story.txt"
    source.write_text(TEXT)
    file = tmp_path / "allow.json"
    file.write_text(json.dumps(bad))
    assert main([str(source), "--allowlist", str(file)]) == 2
    assert "allowlist" in capsys.readouterr().err


def test_apostrophe_normalization():
    result = analyze(
        "Traveler’s silver bell rang. Traveler's silver bell rang.",
        min_words=4,
        max_words=4,
        min_characters=1,
        allowlist=["TRAVELER'S SILVER BELL RANG"],
    )
    assert result["echo_count"] == 0


def test_cli_rejects_null_allowlist_without_output(tmp_path, capsys):
    source = tmp_path / "story.txt"
    source.write_text(TEXT, encoding="utf-8")
    allowlist = tmp_path / "allow.json"
    allowlist.write_text("null", encoding="utf-8")
    output = tmp_path / "report.json"
    assert main([str(source), "--allowlist", str(allowlist), "--output", str(output)]) == 2
    captured = capsys.readouterr()
    assert "allowlist must be a JSON array" in captured.err
    assert not captured.out
    assert not output.exists()
    assert source.read_text(encoding="utf-8") == TEXT
    assert allowlist.read_text(encoding="utf-8") == "null"
