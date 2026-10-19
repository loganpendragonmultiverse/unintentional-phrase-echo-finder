from __future__ import annotations

import argparse
import io
import json
import os
import sys
from pathlib import Path

from .core import analyze, render_json, render_markdown


def _write_stdout(rendered: str) -> None:
    """Avoid retaining report bytes in a buffer after a closed-pipe failure."""
    try:
        descriptor = sys.stdout.fileno()
    except (AttributeError, io.UnsupportedOperation):
        sys.stdout.write(rendered)
        sys.stdout.flush()
        return
    pending = memoryview(
        rendered.encode(sys.stdout.encoding or "utf-8", sys.stdout.errors or "strict")
    )
    while pending:
        count = os.write(descriptor, pending)
        if count <= 0:
            raise OSError("stdout accepted no report bytes")
        pending = pending[count:]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Find repeated multi-word phrases in UTF-8 prose.")
    parser.add_argument("input", type=Path)
    parser.add_argument("--min-words", type=int, default=3)
    parser.add_argument("--max-words", type=int, default=7)
    parser.add_argument("--min-characters", type=int, default=14)
    parser.add_argument("--max-gap-words", type=int, default=250)
    parser.add_argument("--allowlist", type=Path, help="Local JSON array of intentional phrases")
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        text = args.input.read_text(encoding="utf-8")
        allowlist = None
        if args.allowlist is not None:
            allowlist = json.loads(args.allowlist.read_text(encoding="utf-8"))
            if not isinstance(allowlist, list):
                raise ValueError("allowlist must be a JSON array of non-empty phrase strings")
        report = analyze(
            text,
            args.min_words,
            args.max_words,
            args.min_characters,
            args.max_gap_words,
            args.limit,
            allowlist=allowlist,
        )
        rendered = render_json(report) if args.format == "json" else render_markdown(report)
        if args.output:
            try:
                with args.output.open("x", encoding="utf-8", newline="") as stream:
                    stream.write(rendered)
            except FileExistsError as exc:
                raise ValueError(
                    f"output already exists: {args.output}; choose a new file"
                ) from exc
        else:
            _write_stdout(rendered)
    except (OSError, UnicodeError, TypeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0
