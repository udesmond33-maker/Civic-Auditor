# CivicQA Auditor

**Open-source data-quality auditing for civic and eGovernment AI.**

CivicQA operationalises the data-quality dimensions of **ISO/IEC 5259** and
produces explainable, **EU AI Act-aligned** audit reports — with a novel
**representativeness / demographic-parity** dimension designed for civic
datasets, where conventional quality checks miss systematic under-representation
of groups.

Built under the **StandICT.eu 2029 fellowship** (Application ID 2029-02-1734),
contributing to ISO/IEC JTC 1/SC 42 and CEN/CENELEC JTC 21.

---

## Why

The EU AI Act (Article 10) requires high-risk AI — including civic and
eGovernment systems — to be trained on data that is relevant, representative,
and free of errors. ISO/IEC 5259 defines data-quality dimensions generically,
but offers no civic-domain implementation. CivicQA fills that gap: a runnable
tool that scores a dataset against the 5259 dimensions **and** flags
demographic skew that would otherwise pass every conventional quality check.

## What it measures

| Dimension | What it checks | Basis |
|-----------|----------------|-------|
| Completeness | Missing values | ISO/IEC 5259-2 |
| Uniqueness | Duplicate records | ISO/IEC 5259-2 |
| Consistency | Mixed/contradictory value types | ISO/IEC 5259-2 |
| Accuracy | Syntactic validity (optional rules) | ISO/IEC 5259-2 |
| Currentness | Freshness / staleness | ISO/IEC 5259-2 |
| Accessibility | Documented schema / metadata (DCAT-AP-lite) | ISO/IEC 5259-2 |
| **Representativeness** | **Demographic parity / group coverage** | **ISO/IEC 5259-1 (proposed extension)** |

## Install

```bash
pip install -r requirements.txt
```

## Use — command line

```bash
python -m civicqa.cli audit examples/civic_requests.csv \
    --metadata examples/civic_requests.meta.json \
    --date-column reported_at \
    --protected region language \
    --format markdown
```

## Use — Python

```python
from civicqa import CivicQAAuditor
from civicqa.ingestion import load_dataset

df, metadata = load_dataset("examples/civic_requests.csv",
                            "examples/civic_requests.meta.json")
report = CivicQAAuditor().audit(df, dataset_name="civic_requests", config={
    "metadata": metadata,
    "date_column": "reported_at",
    "protected_columns": ["region", "language"],
    # optional census reference for parity scoring:
    # "reference_distribution": {"region": {"Lagos": 0.4, "Abuja": 0.2, ...}},
})
print(report.to_markdown())
report.to_json("audit.json")
```

## Example output

The bundled sample dataset scores well on conventional dimensions but the
representativeness check flags severe under-representation of some regions and
languages — exactly the failure mode civic AI must catch.

## EU AI Act alignment

Reports reference Article 10 (data governance) and Article 12 (record-keeping),
producing a traceable, timestamped quality record suitable for compliance logs.

## Status

`v0.1.0` — core dimensions, ingestion, CLI, audit report (JSON + Markdown).
Roadmap: extended bias indicators, provenance, JSON-LD output, validation
against live European open-data platforms.

## Licence

Apache-2.0. See `LICENSE`.

## Funding & acknowledgement

This work was developed under the **StandICT.eu 2029** fellowship programme
(Application ID 2029-02-1734). StandICT.eu 2029 has received funding from the
European Union's Horizon Europe research and innovation programme under grant
agreement No 101213612. Views and opinions expressed are those of the author
only and do not necessarily reflect those of the European Union or StandICT.eu.
Neither the European Union nor the granting authority can be held responsible
for them.
