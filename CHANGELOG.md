# Changelog

## 1.1.1 - 2026-10-19

- Create reports exclusively so existing files, source aliases and destinations arriving during export are preserved.
- Report output and stdout write failures with exit status 2.
- Reject non-integer Python API thresholds, including boolean values, and skip phrase widths larger than the recognized word count.
- Verify threshold boundaries, source locations and the existing exact allowlist/tokenizer behavior; include distribution checksums in release artifacts.

## 1.1.0 - 2026-10-16

- Reject explicitly supplied JSON null allowlists before analysis or report creation.

- Added a local JSON intentional-repeat allowlist using exact normalized token sequences.
- Suppressed allowlisted phrases before report limiting; preserved default output, longer/different matches and source manuscripts.

## 1.0.0 - 2026-07-26

- Added configurable multi-word phrase echo detection.
- Added closest-gap and line, column, and word-position evidence.
- Added longest-match prioritization and Markdown or JSON reports.
