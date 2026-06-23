"""
CivicQA Auditor — open-source data-quality auditing for civic / eGovernment AI.

Operationalises ISO/IEC 5259 data-quality dimensions and produces
EU-AI-Act-aligned audit reports. Built under the StandICT.eu 2029 fellowship
(Application ID 2029-02-1734).

Licensed under Apache-2.0.
"""

from .auditor import CivicQAAuditor, AuditReport, __version__
from .dimensions import DimensionResult, ALL_DIMENSIONS

__all__ = [
    "CivicQAAuditor",
    "AuditReport",
    "DimensionResult",
    "ALL_DIMENSIONS",
    "__version__",
]
