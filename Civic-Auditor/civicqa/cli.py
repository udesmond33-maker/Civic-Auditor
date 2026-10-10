"""
civicqa.cli
===========

Command-line interface:

    python -m civicqa.cli audit data.csv \\
        --metadata data.meta.json \\
        --date-column reported_at \\
        --protected region language \\
        --format markdown

Outputs an audit report to stdout (or --out file).
"""

from __future__ import annotations
import argparse
import sys

from .ingestion import load_dataset
from .auditor import CivicQAAuditor


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="civicqa", description="CivicQA data-quality auditor")
    sub = parser.add_subparsers(dest="command", required=True)

    a = sub.add_parser("audit", help="Audit a dataset")
    a.add_argument("dataset", help="Path to .csv or .json dataset")
    a.add_argument("--metadata", help="Path to metadata JSON sidecar")
    a.add_argument("--date-column", help="Column to assess currentness")
    a.add_argument("--max-age-days", type=int, default=365)
    a.add_argument("--protected", nargs="*", help="Protected columns for representativeness")
    a.add_argument("--format", choices=["json", "markdown"], default="markdown")
    a.add_argument("--out", help="Write report to this file instead of stdout")

    args = parser.parse_args(argv)

    if args.command == "audit":
        df, metadata = load_dataset(args.dataset, args.metadata)
        config = {
            "metadata": metadata,
            "date_column": args.date_column,
            "max_age_days": args.max_age_days,
            "protected_columns": args.protected,
        }
        report = CivicQAAuditor().audit(df, dataset_name=args.dataset, config=config)
        text = report.to_json() if args.format == "json" else report.to_markdown()
        if args.out:
            with open(args.out, "w", encoding="utf-8") as fh:
                fh.write(text)
            print(f"Report written to {args.out}")
        else:
            print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
