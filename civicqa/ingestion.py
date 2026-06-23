"""
civicqa.ingestion
=================

Lightweight loaders that turn common civic open-data formats into a pandas
DataFrame plus optional metadata, ready for the auditor.

Supported: CSV, JSON (records or {"data": [...]}), and a sidecar metadata
JSON (title / description / column descriptions) following a DCAT-AP-lite
shape for the accessibility dimension.
"""

from __future__ import annotations
from typing import Optional
import json
import os

import pandas as pd


def load_dataset(path: str, metadata_path: Optional[str] = None
                 ) -> tuple[pd.DataFrame, dict]:
    """Load a dataset and optional metadata sidecar."""
    ext = os.path.splitext(path)[1].lower()
    if ext == ".csv":
        df = pd.read_csv(path)
    elif ext == ".json":
        with open(path, encoding="utf-8") as fh:
            raw = json.load(fh)
        if isinstance(raw, dict) and "data" in raw:
            df = pd.DataFrame(raw["data"])
        else:
            df = pd.DataFrame(raw)
    else:
        raise ValueError(f"Unsupported file type: {ext} (use .csv or .json)")

    metadata: dict = {}
    if metadata_path and os.path.exists(metadata_path):
        with open(metadata_path, encoding="utf-8") as fh:
            metadata = json.load(fh)
    return df, metadata
