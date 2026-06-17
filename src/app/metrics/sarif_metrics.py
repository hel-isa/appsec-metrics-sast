"""Pure functions that turn parsed SARIF documents into AppSec metrics.

No I/O here on purpose: this is the part worth unit-testing.
"""
from collections import Counter
from typing import Any, Dict, List

from src.app.metrics.severity import SEVERITIES, normalize_severity
from src.utils.time import utc_now_iso


def _rule_index(run: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """rule_id -> {security_severity, description} from a run's tool driver."""
    driver = run.get("tool", {}).get("driver", {})
    index: Dict[str, Dict[str, Any]] = {}
    for rule in driver.get("rules", []) or []:
        rid = rule.get("id")
        if not rid:
            continue
        props = rule.get("properties", {}) or {}
        desc = (rule.get("shortDescription", {}) or {}).get("text", "")
        index[rid] = {
            "security_severity": props.get("security-severity"),
            "description": desc,
        }
    return index


def _result_file(result: Dict[str, Any]) -> str:
    locations = result.get("locations") or []
    if not locations:
        return "(unknown)"
    phys = locations[0].get("physicalLocation", {}) or {}
    return (phys.get("artifactLocation", {}) or {}).get("uri", "(unknown)")


def compute_metrics(documents: List[Dict[str, Any]], top_n: int = 10) -> Dict[str, Any]:
    by_severity: Counter = Counter({s: 0 for s in SEVERITIES})
    by_tool: Counter = Counter()
    rule_counter: Counter = Counter()
    file_counter: Counter = Counter()
    rule_meta: Dict[str, Dict[str, str]] = {}
    total = 0

    for doc in documents:
        for run in doc.get("runs", []) or []:
            tool_name = run.get("tool", {}).get("driver", {}).get("name", "unknown")
            rules = _rule_index(run)

            for result in run.get("results", []) or []:
                total += 1
                rule_id = result.get("ruleId", "(no-rule-id)")
                rprops = result.get("properties", {}) or {}

                sec_sev = rprops.get("security-severity")
                if sec_sev in (None, ""):
                    sec_sev = rules.get(rule_id, {}).get("security_severity")

                severity = normalize_severity(sec_sev, result.get("level"))

                by_severity[severity] += 1
                by_tool[tool_name] += 1
                rule_counter[rule_id] += 1
                file_counter[_result_file(result)] += 1

                if rule_id not in rule_meta:
                    rule_meta[rule_id] = {
                        "severity": severity,
                        "description": rules.get(rule_id, {}).get("description", ""),
                    }

    top_rules = [
        {
            "rule_id": rid,
            "count": count,
            "severity": rule_meta.get(rid, {}).get("severity", "low"),
            "description": rule_meta.get(rid, {}).get("description", ""),
        }
        for rid, count in rule_counter.most_common(top_n)
    ]
    top_files = [{"file": f, "count": c} for f, c in file_counter.most_common(top_n)]

    return {
        "schema_version": "1.0",
        "generated_at": utc_now_iso(),
        "summary": {
            "total_findings": total,
            "unique_rules": len(rule_counter),
            "files_with_findings": len(file_counter),
            "tools": sorted(by_tool.keys()),
        },
        "by_severity": dict(by_severity),
        "by_tool": dict(by_tool),
        "top_rules": top_rules,
        "top_files": top_files,
    }
