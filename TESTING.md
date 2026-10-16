# Testing

## 1.1.0 - 2026-10-16

Run `python -m pip install -e ".[dev]"`, `ruff format --check .`, `ruff check .`, `pytest`, and `python -m build`. Keep regression fixtures synthetic and source inputs unchanged. `tests/test_feature_wave.py` covers the new behavior, malformed inputs and compatibility defaults. Verify README and CHANGELOG in wheel metadata/documentation and in the source archive before release. Protected cross-platform CI and CodeQL remain required; draft PR preparation does not authorize a merge or release.

The null-allowlist regression must exit with code 2, create no report, and leave both source and allowlist files unchanged.
