# Unintentional Phrase Echo Finder

[![CI](https://github.com/loganpendragonmultiverse/unintentional-phrase-echo-finder/actions/workflows/ci.yml/badge.svg)](https://github.com/loganpendragonmultiverse/unintentional-phrase-echo-finder/actions/workflows/ci.yml)

Unintentional Phrase Echo Finder locates distinctive multi-word phrases repeated unusually close together or at least three times in UTF-8 prose. It reports normalized phrases, counts, closest word gaps, and line and column locations.

## Three-minute start

```bash
python -m pip install .
phrase-echo examples/sample.txt
phrase-echo manuscript.txt --min-words 4 --max-words 8 --max-gap-words 500 --format json
```

The longest matching phrases are prioritized, and shorter matches with identical occurrence locations are suppressed. Thresholds are explicit so writers can tune the report to different manuscript sizes.

## Interpretation boundary

Every result is a review prompt, not a style violation. Repetition can be deliberate, grammatically necessary, thematic, or part of dialogue. The tool performs case-insensitive token matching; it does not understand meaning, stemming, sentence boundaries, or manuscript formats other than supplied UTF-8 text.

Requires Python 3.10 or newer; there are no runtime dependencies. Development checks use Ruff, strict mypy, pytest with branch coverage, and package builds.

Part of the [Logan Pendragon Forge open-source collection](https://www.loganpendragonforge.com/open-source/). Licensed under the [MIT License](LICENSE).

## 1.1.0 - 2026-10-16

Use `phrase-echo manuscript.txt --allowlist intentional.json` with a local JSON array such as `["silver rain crossed the window"]`. Allowlisted phrases use exactly the detector's tokenization: ASCII letters/digits with an optional straight or curly apostrophe segment, case folding and curly-to-straight apostrophe normalization; punctuation and whitespace delimit tokens. Only an exact normalized token sequence is suppressed. A shorter phrase does not suppress a longer one, and a longer or different phrase does not suppress a shorter match. Suppression happens before longest-match selection and report limiting, so remaining results can fill the limit. The default and an empty list preserve the original output. Non-array files, non-string elements and entries with no recognized tokens produce errors. Source manuscripts are read only. This token rule is not broad multilingual language support.

## Reports and limits

Use `phrase-echo manuscript.txt --format json --output report.json` to create a new report.
Existing files, the manuscript, the allowlist and symlink destinations are refused. A file created
by another process during export is also preserved. Input, validation and output errors return exit
status 2. A write failure can leave a partial new report; inspect that file and choose a different
name when retrying. Source files are never edited.

Word, line and column positions are one-based. Columns count characters, including tabs as one
character. `closest_gap_words` measures the distance between phrase start-word positions; overlapping
occurrences count. Punctuation and line breaks delimit tokens but do not stop a phrase from spanning
them. Two occurrences qualify when their closest gap is at most `--max-gap-words`; three or more
occurrences qualify regardless of that gap. `--min-characters` counts the normalized phrase with
spaces. `--limit` applies after exact allowlist suppression and longest-match selection.

All five thresholds must be integers: minimum phrase size is 2, maximum size must be at least the
minimum, and the character, gap and report limits must be positive. These rules also apply to the
Python API; booleans and fractional values are rejected. The ASCII token rule above is deliberately
limited: accented and other non-ASCII letters are delimiters, not multilingual words. Repeated text
is evidence for your review, not proof that an echo is accidental.

## Verify a release

Download the wheel or source archive and `SHA256SUMS.txt` from the same release. Check its SHA-256
against the matching filename before installing, for example with `sha256sum -c SHA256SUMS.txt` on
systems with that command. To verify only a downloaded wheel or archive, hash that file and compare
its own entry; the checksum file lists both distributions. Install the wheel with
`python -m pip install ./unintentional_phrase_echo_finder-1.1.1-py3-none-any.whl`.

## Gold Star

I consider this project complete for its documented purpose: reviewing repeated normalized phrases
in supplied UTF-8 prose with configurable thresholds, exact allowlists and source locations.
Fixes, maintenance and good new ideas are still welcome.
