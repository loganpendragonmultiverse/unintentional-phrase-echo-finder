import json

import pytest

from phrase_echo_finder.cli import main
from phrase_echo_finder.core import analyze, render_markdown

TEXT = "Silver rain crossed the window.\nMara waited. Silver rain crossed the window again."


def test_analyze_finds_longest_echo():
    report = analyze(TEXT, min_words=3, max_words=5, min_characters=10, max_gap_words=50)
    assert report["echo_count"] >= 1
    assert report["echoes"][0]["phrase"].startswith("silver rain crossed the window")
    assert report["echoes"][0]["occurrences"][1]["line"] == 2
    assert "closest gap" in render_markdown(report)


def test_threshold_validation_and_far_pair():
    with pytest.raises(ValueError, match="thresholds"):
        analyze("words", min_words=1)
    text = (
        "one bright phrase "
        + " ".join(f"filler{index}" for index in range(20))
        + " one bright phrase"
    )
    assert analyze(text, min_words=3, max_words=3, max_gap_words=5)["echo_count"] == 0


def test_cli_json_and_output_safety(tmp_path, capsys):
    source = tmp_path / "story.txt"
    source.write_text(TEXT, encoding="utf-8")
    assert main([str(source), "--min-characters", "10", "--format", "json"]) == 0
    assert json.loads(capsys.readouterr().out)["echo_count"] >= 1
    output = tmp_path / "report.md"
    output.write_text("keep", encoding="utf-8")
    assert main([str(source), "--output", str(output)]) == 2
