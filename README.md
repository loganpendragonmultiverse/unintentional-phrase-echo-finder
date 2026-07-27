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

Requires Python 3.10 or newer. Development checks use Ruff, pytest with branch coverage, and package builds.

Part of the [Logan Pendragon Forge open-source collection](https://www.loganpendragonforge.com/open-source/). Licensed under the [MIT License](LICENSE).
