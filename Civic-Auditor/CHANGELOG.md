# Changelog

## 0.2.0 — 2026-10-11
- Added `examples/bonn/`: second audit on real public civic data — Bonn "Mängelmelder"
  citizen reports, Jan 2018–Feb 2020 (10,361 records after exact-duplicate removal, 4 Stadtbezirke),
  assigned to districts by point-in-polygon against the city's official boundary polygons and compared
  against registered population per Stadtbezirk on 31.12.2018. Sources: opendata.bonn.de (reports and
  boundaries, CC0) and Bundesstadt Bonn Statistikstelle, *Statistik aktuell* Feb 2021, Tab. 8.
  Replicates the Berlin pattern: centre over-recorded (1.19), outer district under-recorded (0.72).
- Flag threshold for under-representation is now configurable (`flag_ratio`, default 0.5) and every
  observed/expected ratio is reported in evidence regardless of the threshold, including a
  `below_expected` map. Motivation: with the default threshold the Bonn audit raised no issue
  although Hardtberg sat at 0.72 of its expected share.
- Fixed `examples/berlin/` and `examples/bonn/` as the two real-data case studies referenced in the
  published use case; `examples/civic_requests.csv` remains synthetic.
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
