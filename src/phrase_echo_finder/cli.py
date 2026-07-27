from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .core import analyze, render_json, render_markdown


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Find repeated multi-word phrases in UTF-8 prose.")
    parser.add_argument("input", type=Path)
    parser.add_argument("--min-words", type=int, default=3)
    parser.add_argument("--max-words", type=int, default=7)
    parser.add_argument("--min-characters", type=int, default=14)
    parser.add_argument("--max-gap-words", type=int, default=250)
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        text = args.input.read_text(encoding="utf-8")
        report = analyze(
            text,
            args.min_words,
            args.max_words,
            args.min_characters,
            args.max_gap_words,
            args.limit,
        )
        rendered = render_json(report) if args.format == "json" else render_markdown(report)
        if args.output:
            if args.output.exists():
                raise ValueError(f"output already exists: {args.output}")
            args.output.write_text(rendered, encoding="utf-8")
        else:
            sys.stdout.write(rendered)
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0
