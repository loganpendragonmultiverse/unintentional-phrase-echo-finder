from __future__ import annotations

import json
import re
from collections import defaultdict
from itertools import pairwise
from typing import Any

WORD = re.compile(r"[A-Za-z0-9]+(?:['’][A-Za-z0-9]+)?")


def analyze(
    text: str,
    min_words: int = 3,
    max_words: int = 7,
    min_characters: int = 14,
    max_gap_words: int = 250,
    limit: int = 100,
) -> dict[str, Any]:
    if (
        min_words < 2
        or max_words < min_words
        or min_characters < 1
        or max_gap_words < 1
        or limit < 1
    ):
        raise ValueError("analysis thresholds are invalid")
    matches = list(WORD.finditer(text))
    words = [match.group(0).casefold().replace("’", "'") for match in matches]
    line_starts = [0]
    line_starts.extend(match.end() for match in re.finditer("\n", text))

    def location(match_index: int) -> dict[str, int]:
        position = matches[match_index].start()
        line = 1
        for index, start in enumerate(line_starts):
            if start > position:
                break
            line = index + 1
        column = position - line_starts[line - 1] + 1
        return {"word": match_index + 1, "line": line, "column": column}

    candidates: list[dict[str, Any]] = []
    for size in range(max_words, min_words - 1, -1):
        groups: dict[tuple[str, ...], list[int]] = defaultdict(list)
        for start in range(len(words) - size + 1):
            phrase = tuple(words[start : start + size])
            if len(" ".join(phrase)) >= min_characters:
                groups[phrase].append(start)
        for phrase, starts in groups.items():
            if len(starts) < 2:
                continue
            gaps = [right - left for left, right in pairwise(starts)]
            if len(starts) < 3 and min(gaps) > max_gap_words:
                continue
            candidates.append(
                {
                    "phrase": " ".join(phrase),
                    "words": size,
                    "count": len(starts),
                    "closest_gap_words": min(gaps),
                    "occurrences": [location(start) for start in starts],
                }
            )
    candidates.sort(
        key=lambda item: (-item["words"], -item["count"], item["closest_gap_words"], item["phrase"])
    )
    selected: list[dict[str, Any]] = []
    for candidate in candidates:
        if any(
            candidate["phrase"] in existing["phrase"]
            and candidate["occurrences"] == existing["occurrences"]
            for existing in selected
        ):
            continue
        selected.append(candidate)
        if len(selected) == limit:
            break
    return {"version": 1, "word_count": len(words), "echo_count": len(selected), "echoes": selected}


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Phrase Echo Report",
        "",
        f"Words analyzed: **{report['word_count']:,}** · Echoes found: **{report['echo_count']}**",
        "",
    ]
    for echo in report["echoes"]:
        locations = ", ".join(f"line {item['line']}" for item in echo["occurrences"])
        lines.append(
            f"- **{echo['phrase']}** — {echo['count']} occurrences ({locations}); closest gap: {echo['closest_gap_words']} words"
        )
    return "\n".join(lines).rstrip() + "\n"


def render_json(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, ensure_ascii=False) + "\n"
