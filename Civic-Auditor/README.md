# CivicQA Auditor

**Open-source data-quality auditing for civic and eGovernment AI.**

CivicQA operationalises the data-quality dimensions of **ISO/IEC 5259** and
produces explainable, **EU AI Act-aligned** audit reports, with a novel
**representativeness / demographic-parity** dimension designed for civic
datasets, where conventional quality checks miss systematic under-representation
of groups.

Built under the **StandICT.eu 2029 fellowship** (Application ID 2029-02-1734),
contributing to ISO/IEC JTC 1/SC 42 and CEN/CENELEC JTC 21.

---

## Why

The EU AI Act (Article 10) requires high-risk AI , including civic and
eGovernment systems, to be trained on data that is relevant, representative,
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

## Use : command line

```bash
python -m civicqa.cli audit examples/civic_requests.csv \
    --metadata examples/civic_requests.meta.json \
    --date-column reported_at \
    --protected region language \
    --format markdown
```

## Use : Python

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

### Real data: Berlin citizen reports (v0.2.0)

`examples/berlin/` audits 25,630 official Ordnungsamt-Online reports (Q1 2017) against
Berlin's registered population by district. Conventional quality dimensions score 100%,
but against the population reference representativeness falls to 77%: Steglitz-Zehlendorf
(8.3% of residents) is **absent** from the data, and Marzahn-Hellersdorf appears at 0.43x its
population share, while Friedrichshain-Kreuzberg and Neukölln appear at ~2x. The same data
scores 94% under the reference-free (entropy) mode, showing that the choice of method alone
changes the result. See `examples/berlin/audit_reference.md`.

### Real data: Bonn citizen reports (v0.2.0)

`examples/bonn/` audits 10,361 Mängelmelder reports (Jan 2018–Feb 2020, after removal of 870
exact-duplicate rows from the published export) against Bonn's registered population by
Stadtbezirk on 31.12.2018. Reports carry coordinates only, so each is assigned to a district by
point-in-polygon against the city's official boundary file. Conventional dimensions again score
100%; against the population reference, the central district is recorded at 1.19x its share and
Hardtberg at 0.72x. With the default flag threshold (0.5) this raised no issue, which is why the
threshold is now configurable and all ratios are always reported. Entropy mode scores 83%,
reference mode 91% — the method divergence runs the opposite way to Berlin, so method choice
alone can raise or lower a reported score. See `examples/bonn/build.py`.

### Synthetic demonstration

The bundled synthetic sample dataset scores well on conventional dimensions but the
representativeness check flags severe under-representation of some regions and
languages  exactly the failure mode civic AI must catch.

## EU AI Act alignment

Reports reference Article 10 (data governance) and Article 12 (record-keeping),
producing a traceable, timestamped quality record suitable for compliance logs.

## Status

`v0.1.0`  core dimensions, ingestion, CLI, audit report (JSON + Markdown).
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
