# Testing

## 1.1.0 - 2026-10-16

Run `python -m pip install -e ".[dev]"`, `ruff format --check .`, `ruff check .`, `pytest`, and `python -m build`. Keep regression fixtures synthetic and source inputs unchanged. `tests/test_feature_wave.py` covers the new behavior, malformed inputs and compatibility defaults. Verify README and CHANGELOG in wheel metadata/documentation and in the source archive before release. Protected cross-platform CI and CodeQL remain required; draft PR preparation does not authorize a merge or release.

The null-allowlist regression must exit with code 2, create no report, and leave both source and allowlist files unchanged.

## 1.1.1 output and qualification checks

Run Ruff formatting/lint, `mypy --strict src`, branch-covered pytest and a wheel/source build.
Keep synthetic manuscripts and allowlists byte-identical. Cover exclusive output creation including
an arriving destination, source/allowlist aliases, symlinks, missing parents, real unprivileged
permission errors, and handled write/flush failures. A failed new-file write may leave a partial
report; this is not a crash-atomic export guarantee.

Verify exact threshold boundaries, one-based word/line/column evidence, overlapping occurrences,
three distant repeats, case/apostrophe normalization, allowlist suppression before limiting and the
ASCII tokenizer boundary. Non-integer API thresholds must fail before analysis. Widths exceeding the
recognized word count must not add empty work or change results.

For release, generate SHA256SUMS.txt for both distributions, bind package/version/docs to the reviewed
source, install each distribution into an isolated environment, run the complete suite without source
shadowing and exercise both entrypoints and new JSON/Markdown exports. Require protected PR/main CI,
CodeQL, the actual tagged distributions and public checksum verification before Gold publication.
