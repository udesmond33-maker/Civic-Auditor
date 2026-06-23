"""Basic tests for the CivicQA Auditor."""
import pandas as pd
import numpy as np

from civicqa import CivicQAAuditor
from civicqa.dimensions import (
    completeness, uniqueness, consistency, representativeness,
)


def _clean_df():
    return pd.DataFrame({
        "id": [1, 2, 3, 4],
        "region": ["A", "B", "A", "B"],
        "value": [10, 20, 30, 40],
    })


def test_completeness_perfect():
    r = completeness(_clean_df())
    assert r.score == 1.0


def test_completeness_with_missing():
    df = _clean_df()
    df.loc[0, "value"] = None
    r = completeness(df)
    assert r.score < 1.0
    assert r.evidence["missing_cells"] == 1


def test_uniqueness_detects_duplicates():
    df = _clean_df()
    df = pd.concat([df, df.iloc[[0]]], ignore_index=True)
    r = uniqueness(df)
    assert r.evidence["duplicate_rows"] == 1
    assert r.score < 1.0


def test_consistency_flags_mixed_types():
    df = pd.DataFrame({"col": [1, "two", 3]})
    r = consistency(df)
    assert r.score < 1.0


def test_representativeness_even_vs_skewed():
    even = pd.DataFrame({"region": ["A", "B", "A", "B"]})
    skew = pd.DataFrame({"region": ["A"] * 19 + ["B"]})
    r_even = representativeness(even, protected_columns=["region"])
    r_skew = representativeness(skew, protected_columns=["region"])
    assert r_even.score > r_skew.score


def test_auditor_end_to_end():
    auditor = CivicQAAuditor()
    report = auditor.audit(_clean_df(), dataset_name="test",
                           config={"protected_columns": ["region"]})
    assert 0.0 <= report.overall_score <= 1.0
    assert report.grade
    assert report.record_count == 4
    # report serialises cleanly
    assert "civicqa_audit" in report.as_dict()
    assert isinstance(report.to_markdown(), str)
