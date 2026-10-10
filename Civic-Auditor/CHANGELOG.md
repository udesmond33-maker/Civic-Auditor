# Changelog

## 0.2.0 — 2026-10-07
- Reference-parity mode now flags strata that are **absent** from the dataset and strata
  whose observed share is below half their expected share (observed/expected ratio reported
  in evidence). Previously, an absent group could lower the score without being named.
- Added `examples/berlin/`: first audit on real public civic data — Berlin
  "Ordnungsamt-Online" citizen reports, Q1 2017 (25,630 records, 11 districts), compared
  against registered population per district on 31.12.2016. Sources: Abgeordnetenhaus Berlin
  Drucksache 18/10900 (report counts) and 18/28582 (population). Audit reports for both
  scoring modes included.
- Clarified that `examples/civic_requests.csv` is a synthetic demonstration dataset.

## 0.1.0 — 2026-07
- Initial release.
