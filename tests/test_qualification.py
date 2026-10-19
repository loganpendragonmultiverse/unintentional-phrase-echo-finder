import io
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from phrase_echo_finder import cli
from phrase_echo_finder.core import analyze

TEXT = "Silver rain crossed the window. Other words. Silver rain crossed the window."


@pytest.mark.parametrize("format", ["json", "markdown"])
def test_new_report_and_input_preservation(tmp_path, capsys, format):
    source = tmp_path / "story.txt"
    source.write_text(TEXT, encoding="utf-8")
    output = tmp_path / "report"
    assert cli.main([str(source), "--format", format, "--output", str(output)]) == 0
    assert source.read_text(encoding="utf-8") == TEXT
    assert not capsys.readouterr().out
    if format == "json":
        assert (
            json.loads(output.read_text())["echoes"][0]["phrase"]
            == "silver rain crossed the window"
        )
    else:
        assert output.read_text().startswith("# Phrase Echo Report\n")


def test_arriving_destination_is_preserved(tmp_path, monkeypatch, capsys):
    source = tmp_path / "story.txt"
    source.write_text(TEXT)
    output = tmp_path / "report.json"
    original = Path.open

    def arrive(path, mode="r", *args, **kwargs):
        if path == output and mode == "x":
            output.write_bytes(b"EXTERNAL ARRIVAL")
        return original(path, mode, *args, **kwargs)

    monkeypatch.setattr(Path, "open", arrive)
    assert cli.main([str(source), "--output", str(output)]) == 2
    assert "choose a new file" in capsys.readouterr().err
    assert output.read_bytes() == b"EXTERNAL ARRIVAL"
    assert source.read_text() == TEXT


@pytest.mark.parametrize("target", ["source", "allowlist", "directory", "missing-parent"])
def test_output_alias_and_bad_destinations(tmp_path, capsys, target):
    source = tmp_path / "story.txt"
    source.write_text(TEXT)
    allowed = tmp_path / "allow.json"
    allowed.write_text('["intentional other phrase"]')
    output = {
        "source": source,
        "allowlist": allowed,
        "directory": tmp_path,
        "missing-parent": tmp_path / "absent" / "report.json",
    }[target]
    before = source.read_bytes(), allowed.read_bytes()
    assert cli.main([str(source), "--allowlist", str(allowed), "--output", str(output)]) == 2
    assert "error:" in capsys.readouterr().err
    assert (source.read_bytes(), allowed.read_bytes()) == before
    assert not (tmp_path / "absent").exists()


@pytest.mark.parametrize("dangling", [False, True])
def test_symlink_destination_is_preserved(tmp_path, dangling):
    source = tmp_path / "story.txt"
    source.write_text(TEXT)
    target = tmp_path / "target"
    if not dangling:
        target.write_bytes(b"KEEP")
    link = tmp_path / "report"
    try:
        link.symlink_to(target)
    except OSError:
        pytest.skip("This host does not permit creating test symlinks")
    assert cli.main([str(source), "--output", str(link)]) == 2
    assert link.is_symlink()
    assert target.read_bytes() == b"KEEP" if not dangling else not target.exists()


@pytest.mark.parametrize("error", [PermissionError("not writable"), OSError("disk full")])
def test_output_open_failure_is_actionable(tmp_path, monkeypatch, capsys, error):
    source = tmp_path / "story.txt"
    source.write_text(TEXT)
    output = tmp_path / "report"
    original = Path.open

    def fail(path, mode="r", *args, **kwargs):
        if path == output and mode == "x":
            raise error
        return original(path, mode, *args, **kwargs)

    monkeypatch.setattr(Path, "open", fail)
    assert cli.main([str(source), "--output", str(output)]) == 2
    assert str(error) in capsys.readouterr().err
    assert not output.exists() and source.read_text() == TEXT


@pytest.mark.parametrize("phase", ["write", "close"])
def test_new_file_write_failure_preserves_partial_report(tmp_path, monkeypatch, capsys, phase):
    source = tmp_path / "story.txt"
    source.write_text(TEXT)
    output = tmp_path / "report"
    original = Path.open

    class FailingReport:
        def __init__(self, stream):
            self.stream = stream

        def __enter__(self):
            return self

        def write(self, text):
            self.stream.write(text[:8])
            if phase == "write":
                raise OSError("injected report write failure")

        def __exit__(self, *args):
            self.stream.close()
            if phase == "close":
                raise OSError("injected report close failure")

    def wrap(path, mode="r", *args, **kwargs):
        stream = original(path, mode, *args, **kwargs)
        return FailingReport(stream) if path == output and mode == "x" else stream

    monkeypatch.setattr(Path, "open", wrap)
    assert cli.main([str(source), "--output", str(output)]) == 2
    assert "injected report" in capsys.readouterr().err
    assert output.read_text() == "# Phrase"
    assert source.read_text() == TEXT


@pytest.mark.parametrize("kind", ["invalid-utf8", "malformed-json", "missing-input"])
def test_bad_inputs_never_create_report(tmp_path, capsys, kind):
    source = tmp_path / "story.txt"
    source.write_bytes(b"\xff" if kind == "invalid-utf8" else TEXT.encode())
    allowed = tmp_path / "allow.json"
    allowed.write_text("[")
    output = tmp_path / "report"
    args = [str(tmp_path / "missing" if kind == "missing-input" else source)]
    if kind == "malformed-json":
        args += ["--allowlist", str(allowed)]
    before = source.read_bytes(), allowed.read_bytes()
    assert cli.main(args + ["--output", str(output)]) == 2
    assert "error:" in capsys.readouterr().err
    assert not output.exists() and (source.read_bytes(), allowed.read_bytes()) == before


@pytest.mark.parametrize(
    "threshold", ["min_words", "max_words", "min_characters", "max_gap_words", "limit"]
)
@pytest.mark.parametrize("bad", [True, 1.5, "3", None])
def test_api_thresholds_must_be_integers(threshold, bad):
    with pytest.raises(ValueError, match="thresholds must be integers"):
        analyze(TEXT, **{threshold: bad})


@pytest.mark.parametrize(
    "kwargs",
    [
        {"min_words": 1},
        {"min_words": 4, "max_words": 3},
        {"min_characters": 0},
        {"max_gap_words": 0},
        {"limit": 0},
    ],
)
def test_api_threshold_ranges(kwargs):
    with pytest.raises(ValueError, match="thresholds are invalid"):
        analyze(TEXT, **kwargs)


def test_gap_frequency_characters_and_limit_boundaries():
    pair = "silver rain filler filler silver rain"
    args = {"min_words": 2, "max_words": 2, "min_characters": 11}
    assert analyze(pair, **args, max_gap_words=4)["echo_count"] == 1
    assert analyze(pair, **args, max_gap_words=3)["echo_count"] == 0
    assert analyze(pair, min_words=2, max_words=2, min_characters=12)["echo_count"] == 0
    triple = pair + " filler filler silver rain"
    result = analyze(triple, **args, max_gap_words=1, limit=1)
    assert result["echo_count"] == 1 and result["echoes"][0]["count"] == 3


def test_locations_blank_lines_tabs_and_cross_line_phrases():
    result = analyze("\tSilver rain.\n\n  SILVER rain.", min_words=2, max_words=2, min_characters=1)
    assert result["echoes"][0]["occurrences"] == [
        {"word": 1, "line": 1, "column": 2},
        {"word": 3, "line": 3, "column": 3},
    ]
    cross = analyze("Silver\nrain. silver\nrain.", min_words=2, max_words=2, min_characters=1)
    assert cross["echoes"][0]["occurrences"] == [
        {"word": 1, "line": 1, "column": 1},
        {"word": 3, "line": 2, "column": 7},
    ]


def test_overlap_ascii_boundary_and_large_width():
    overlap = analyze("silver silver silver", min_words=2, max_words=2, min_characters=1)
    assert overlap["echoes"][0]["closest_gap_words"] == 1
    assert overlap["echoes"][0]["count"] == 2
    limited = analyze(
        "café silver bell. CAFÉ silver bell.", min_words=3, max_words=3, min_characters=1
    )
    assert limited["word_count"] == 6 and limited["echoes"][0]["phrase"] == "caf silver bell"
    assert analyze(TEXT, max_words=10**12) == analyze(TEXT, max_words=100)
    assert analyze("!!!", max_words=10**12)["word_count"] == 0


@pytest.mark.parametrize("progress", ["partial", "zero", "broken"])
def test_descriptor_stdout_short_write_or_failure(tmp_path, monkeypatch, capsys, progress):
    source = tmp_path / "story.txt"
    source.write_text(TEXT)
    received = bytearray()

    class DescriptorStream:
        encoding = "utf-8"
        errors = "strict"

        def fileno(self):
            return 12345

    def write(descriptor, data):
        assert descriptor == 12345
        if progress == "broken":
            raise BrokenPipeError("consumer closed")
        if progress == "zero":
            return 0
        count = min(7, len(data))
        received.extend(data[:count])
        return count

    monkeypatch.setattr(cli.sys, "stdout", DescriptorStream())
    monkeypatch.setattr(cli.os, "write", write)
    assert cli.main([str(source), "--format", "json"]) == (0 if progress == "partial" else 2)
    if progress == "partial":
        assert json.loads(received)["echo_count"] >= 1
    else:
        assert "error:" in capsys.readouterr().err
    assert source.read_text() == TEXT


def test_fallback_stdout_flush_error(tmp_path, monkeypatch, capsys):
    source = tmp_path / "story.txt"
    source.write_text(TEXT)

    class FlushError(io.StringIO):
        def flush(self):
            raise OSError("flush failed")

    monkeypatch.setattr(cli.sys, "stdout", FlushError())
    assert cli.main([str(source)]) == 2
    assert "flush failed" in capsys.readouterr().err


def test_real_closed_pipe_exits_two_without_shutdown_error(tmp_path):
    source = tmp_path / "story.txt"
    source.write_text(TEXT)
    reader, writer = os.pipe()
    os.close(reader)
    try:
        result = subprocess.run(
            [sys.executable, "-m", "phrase_echo_finder", str(source)],
            check=False,
            stdout=writer,
            stderr=subprocess.PIPE,
            text=True,
        )
    finally:
        os.close(writer)
    assert result.returncode == 2
    assert "error:" in result.stderr and "Exception ignored" not in result.stderr
    assert source.read_text() == TEXT
