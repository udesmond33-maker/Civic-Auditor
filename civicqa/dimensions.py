"""
civicqa.dimensions
==================

Implements the data-quality dimensions defined in ISO/IEC 5259 (Data quality
for analytics and ML), adapted for civic-participation / eGovernment datasets.

Each dimension returns a DimensionResult: a normalised 0..1 score plus the
evidence behind it, so audit reports are explainable and AI-Act-aligned
(traceable logging per Article 12).

ISO/IEC 5259-aligned characteristics implemented here:
  - accuracy            (syntactic / value validity)
  - completeness        (missing values)
  - consistency         (internal contradiction / type uniformity)
  - currentness         (freshness / staleness of records)
  - uniqueness          (duplicate records)
  - accessibility       (presence of documented schema / metadata)
  - representativeness  (CIVIC EXTENSION — demographic parity / coverage)

The representativeness dimension is the novel contribution proposed to
ISO/IEC 5259-1 under the StandICT fellowship (representativeness & demographic
parity as a first-class data-quality dimension for civic AI).
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Optional
import math
import datetime as _dt

import pandas as pd
import numpy as np


@dataclass
class DimensionResult:
    """Explainable result for a single data-quality dimension."""
    dimension: str
    score: float                       # normalised 0..1 (1 = best)
    weight: float = 1.0                # relative weight in the composite
    evidence: dict[str, Any] = field(default_factory=dict)
    issues: list[str] = field(default_factory=list)
    iso_reference: str = ""            # e.g. "ISO/IEC 5259-2 §completeness"

    def as_dict(self) -> dict[str, Any]:
        return {
            "dimension": self.dimension,
            "score": round(float(self.score), 4),
            "weight": self.weight,
            "iso_reference": self.iso_reference,
            "evidence": self.evidence,
            "issues": self.issues,
        }


def _safe_ratio(numerator: float, denominator: float) -> float:
    return float(numerator) / float(denominator) if denominator else 1.0


# --------------------------------------------------------------------------- #
# Core dimensions
# --------------------------------------------------------------------------- #

def completeness(df: pd.DataFrame, **_) -> DimensionResult:
    """Fraction of non-missing cells across the dataset."""
    total = df.size
    missing = int(df.isna().sum().sum())
    score = _safe_ratio(total - missing, total)
    per_col = (df.isna().mean()).round(4).to_dict()
    worst = sorted(per_col.items(), key=lambda kv: kv[1], reverse=True)[:5]
    issues = [f"Column '{c}' is {p:.0%} missing" for c, p in worst if p > 0.1]
    return DimensionResult(
        dimension="completeness",
        score=score,
        evidence={"total_cells": total, "missing_cells": missing,
                  "missing_fraction_per_column": per_col},
        issues=issues,
        iso_reference="ISO/IEC 5259-2 — completeness",
    )


def uniqueness(df: pd.DataFrame, **_) -> DimensionResult:
    """Fraction of rows that are not exact duplicates."""
    n = len(df)
    dupes = int(df.duplicated().sum())
    score = _safe_ratio(n - dupes, n)
    issues = [f"{dupes} duplicate row(s) detected"] if dupes else []
    return DimensionResult(
        dimension="uniqueness",
        score=score,
        evidence={"rows": n, "duplicate_rows": dupes},
        issues=issues,
        iso_reference="ISO/IEC 5259-2 — uniqueness",
    )


def consistency(df: pd.DataFrame, **_) -> DimensionResult:
    """
    Internal consistency: penalise columns whose values mix incompatible
    types (e.g. numbers and free text in one column), which usually signals
    data-entry or pipeline errors.
    """
    n_cols = len(df.columns)
    if n_cols == 0:
        return DimensionResult("consistency", 1.0, iso_reference="ISO/IEC 5259-2 — consistency")
    inconsistent = []
    for col in df.columns:
        non_null = df[col].dropna()
        if non_null.empty:
            continue
        kinds = non_null.map(lambda v: type(v).__name__).nunique()
        if kinds > 1:
            inconsistent.append(col)
    score = _safe_ratio(n_cols - len(inconsistent), n_cols)
    issues = [f"Column '{c}' mixes multiple value types" for c in inconsistent]
    return DimensionResult(
        dimension="consistency",
        score=score,
        evidence={"columns": n_cols, "type_inconsistent_columns": inconsistent},
        issues=issues,
        iso_reference="ISO/IEC 5259-2 — consistency",
    )


def accuracy(df: pd.DataFrame, rules: Optional[dict[str, dict]] = None, **_) -> DimensionResult:
    """
    Syntactic accuracy against optional per-column validity rules.

    rules example:
        {"age": {"min": 0, "max": 120},
         "email": {"regex": r"[^@]+@[^@]+\\.[^@]+"}}

    Without rules, accuracy falls back to a light heuristic (no obviously
    invalid numerics such as infinities), scoring high by default so it does
    not unfairly penalise datasets the auditor has no rules for.
    """
    if not rules:
        # heuristic: penalise inf / impossible floats only
        bad = 0
        total = 0
        for col in df.select_dtypes(include=[np.number]).columns:
            vals = df[col].dropna()
            total += len(vals)
            bad += int(np.isinf(vals).sum())
        score = _safe_ratio(total - bad, total) if total else 1.0
        return DimensionResult(
            dimension="accuracy", score=score,
            evidence={"mode": "heuristic", "invalid_numeric_values": bad},
            issues=[f"{bad} non-finite numeric value(s)"] if bad else [],
            iso_reference="ISO/IEC 5259-2 — accuracy (syntactic)",
        )

    violations: dict[str, int] = {}
    checked = 0
    failed = 0
    import re
    for col, rule in rules.items():
        if col not in df.columns:
            continue
        vals = df[col].dropna()
        checked += len(vals)
        col_fail = 0
        if "min" in rule:
            col_fail += int((pd.to_numeric(vals, errors="coerce") < rule["min"]).sum())
        if "max" in rule:
            col_fail += int((pd.to_numeric(vals, errors="coerce") > rule["max"]).sum())
        if "regex" in rule:
            pattern = re.compile(rule["regex"])
            col_fail += int(sum(1 for v in vals if not pattern.fullmatch(str(v))))
        if "allowed" in rule:
            allowed = set(rule["allowed"])
            col_fail += int(sum(1 for v in vals if v not in allowed))
        if col_fail:
            violations[col] = col_fail
            failed += col_fail
    score = _safe_ratio(checked - failed, checked) if checked else 1.0
    issues = [f"Column '{c}': {v} value(s) violate accuracy rule" for c, v in violations.items()]
    return DimensionResult(
        dimension="accuracy", score=score,
        evidence={"mode": "rules", "checked_values": checked, "violations": violations},
        issues=issues,
        iso_reference="ISO/IEC 5259-2 — accuracy (syntactic)",
    )


def currentness(df: pd.DataFrame, date_column: Optional[str] = None,
                max_age_days: int = 365, **_) -> DimensionResult:
    """
    Freshness: fraction of records newer than max_age_days.
    Civic datasets (prices, service status, registers) lose value when stale.
    """
    if not date_column or date_column not in df.columns:
        return DimensionResult(
            dimension="currentness", score=1.0, weight=0.0,
            evidence={"note": "no date_column provided; dimension not assessed"},
            iso_reference="ISO/IEC 5259-2 — currentness",
        )
    parsed = pd.to_datetime(df[date_column], errors="coerce", utc=True)
    valid = parsed.dropna()
    if valid.empty:
        return DimensionResult(
            dimension="currentness", score=0.0,
            evidence={"note": f"could not parse dates in '{date_column}'"},
            issues=[f"No parseable dates in '{date_column}'"],
            iso_reference="ISO/IEC 5259-2 — currentness",
        )
    now = pd.Timestamp.now(tz="UTC")
    age_days = (now - valid).dt.total_seconds() / 86400.0
    fresh = int((age_days <= max_age_days).sum())
    score = _safe_ratio(fresh, len(valid))
    issues = []
    stale = len(valid) - fresh
    if stale:
        issues.append(f"{stale} record(s) older than {max_age_days} days")
    return DimensionResult(
        dimension="currentness", score=score,
        evidence={"date_column": date_column, "max_age_days": max_age_days,
                  "fresh_records": fresh, "stale_records": stale,
                  "median_age_days": round(float(age_days.median()), 1)},
        issues=issues,
        iso_reference="ISO/IEC 5259-2 — currentness",
    )


def accessibility(df: pd.DataFrame, metadata: Optional[dict] = None, **_) -> DimensionResult:
    """
    Accessibility / documentation: rewards datasets that ship a documented
    schema and basic metadata (title, description, column descriptions),
    aligned to open-data expectations (DCAT-AP) for civic publishing.
    """
    checks = {
        "has_title": bool(metadata and metadata.get("title")),
        "has_description": bool(metadata and metadata.get("description")),
        "has_column_descriptions": bool(metadata and metadata.get("columns")),
        "has_named_columns": all(not str(c).startswith("Unnamed") for c in df.columns),
    }
    score = sum(checks.values()) / len(checks)
    issues = [f"Missing: {k}" for k, ok in checks.items() if not ok]
    return DimensionResult(
        dimension="accessibility", score=score,
        evidence={"checks": checks},
        issues=issues,
        iso_reference="ISO/IEC 5259-2 — accessibility / portability",
    )


# --------------------------------------------------------------------------- #
# CIVIC EXTENSION — representativeness & demographic parity
# (the novel dimension proposed to ISO/IEC 5259-1 under the fellowship)
# --------------------------------------------------------------------------- #

def representativeness(df: pd.DataFrame,
                       protected_columns: Optional[list[str]] = None,
                       reference_distribution: Optional[dict[str, dict]] = None,
                       **_) -> DimensionResult:
    """
    Measures how evenly a dataset covers groups within protected/ demographic
    attributes (e.g. region, language, gender). Civic AI trained on skewed
    data systematically under-serves under-represented groups.

    Two modes:
      * If reference_distribution is given (e.g. census shares per group),
        score = 1 - total_variation_distance between dataset and reference.
      * Otherwise, score = normalised entropy of the group distribution
        (1.0 = perfectly even coverage, → 0 as one group dominates).
    """
    if not protected_columns:
        return DimensionResult(
            dimension="representativeness", score=1.0, weight=0.0,
            evidence={"note": "no protected_columns provided; not assessed"},
            iso_reference="ISO/IEC 5259-1 (PROPOSED extension) — representativeness",
        )

    per_attr = {}
    scores = []
    issues = []
    for col in protected_columns:
        if col not in df.columns:
            issues.append(f"Protected column '{col}' not found")
            continue
        counts = df[col].dropna().value_counts()
        if counts.empty:
            continue
        shares = (counts / counts.sum()).to_dict()

        if reference_distribution and col in reference_distribution:
            ref = reference_distribution[col]
            groups = set(shares) | set(ref)
            tvd = 0.5 * sum(abs(shares.get(g, 0.0) - ref.get(g, 0.0)) for g in groups)
            attr_score = max(0.0, 1.0 - tvd)
            mode = "reference_parity"
        else:
            k = len(shares)
            if k <= 1:
                attr_score = 0.0
            else:
                entropy = -sum(p * math.log(p) for p in shares.values() if p > 0)
                attr_score = entropy / math.log(k)   # normalised 0..1
            mode = "entropy_coverage"

        per_attr[col] = {"mode": mode, "score": round(attr_score, 4),
                         "group_shares": {str(k): round(v, 4) for k, v in shares.items()}}
        scores.append(attr_score)

        # flag severe under-representation
        for g, s in shares.items():
            if s < 0.05:
                issues.append(f"'{col}={g}' under-represented ({s:.1%} of records)")

    score = float(np.mean(scores)) if scores else 0.0
    return DimensionResult(
        dimension="representativeness", score=score, weight=1.5,
        evidence={"protected_columns": protected_columns, "per_attribute": per_attr},
        issues=issues,
        iso_reference="ISO/IEC 5259-1 (PROPOSED extension) — representativeness & demographic parity",
    )


# Registry of all dimensions for the auditor to iterate over
ALL_DIMENSIONS = [
    completeness,
    uniqueness,
    consistency,
    accuracy,
    currentness,
    accessibility,
    representativeness,
]
