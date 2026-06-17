"""Map raw SARIF signals to a normalized AppSec severity band.

Security tools express severity two ways in SARIF:
  1. A numeric `security-severity` (CVSS-like, 0-10) in rule or result properties.
  2. A coarse SARIF `level` (error / warning / note / none).

We prefer the numeric score (GitHub's banding) and fall back to `level`.
"""
from typing import Optional

SEVERITIES = ("critical", "high", "medium", "low", "none")


def band_from_score(score: float) -> str:
    if score >= 9.0:
        return "critical"
    if score >= 7.0:
        return "high"
    if score >= 4.0:
        return "medium"
    if score > 0.0:
        return "low"
    return "none"


def band_from_level(level: Optional[str]) -> str:
    mapping = {"error": "high", "warning": "medium", "note": "low", "none": "none"}
    return mapping.get((level or "").lower(), "low")


def normalize_severity(security_severity: Optional[str], level: Optional[str]) -> str:
    if security_severity not in (None, ""):
        try:
            return band_from_score(float(security_severity))
        except (TypeError, ValueError):
            pass
    return band_from_level(level)
