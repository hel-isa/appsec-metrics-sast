from src.app.metrics.severity import band_from_score, band_from_level, normalize_severity
from src.app.metrics.sarif_metrics import compute_metrics
from src.infra_adapters.sarif.local_sarif_source import LocalSarifSource


def test_band_from_score_boundaries():
    assert band_from_score(9.0) == "critical"
    assert band_from_score(8.9) == "high"
    assert band_from_score(7.0) == "high"
    assert band_from_score(4.0) == "medium"
    assert band_from_score(0.1) == "low"
    assert band_from_score(0.0) == "none"


def test_normalize_prefers_score_over_level():
    # error level would map to high, but score 9.1 wins -> critical
    assert normalize_severity("9.1", "error") == "critical"
    # no score -> fall back to level
    assert normalize_severity(None, "warning") == "medium"
    assert band_from_level("note") == "low"


def test_compute_metrics_on_samples():
    docs = LocalSarifSource(sarif_dir="samples").load_documents()
    m = compute_metrics(docs)

    # 4 (codeql) + 3 (semgrep) = 7 findings
    assert m["summary"]["total_findings"] == 7
    assert set(m["summary"]["tools"]) == {"CodeQL", "Semgrep"}

    # severity bands: sql-injection x2 (9.1->crit), dangerous-eval (9.8->crit) = 3 critical
    assert m["by_severity"]["critical"] == 3
    # clear-text-logging 7.5 -> high = 1 high
    assert m["by_severity"]["high"] == 1
    # weak-crypto 5.9 -> medium, hardcoded-secret 6.5 x2 -> medium = 3 medium
    assert m["by_severity"]["medium"] == 3

    # most frequent rule should be hardcoded-secret or sql-injection (2 each)
    top_counts = {r["rule_id"]: r["count"] for r in m["top_rules"]}
    assert top_counts["py/sql-injection"] == 2
    assert top_counts["python.lang.security.hardcoded-secret"] == 2

    # by tool
    assert m["by_tool"]["CodeQL"] == 4
    assert m["by_tool"]["Semgrep"] == 3


def test_empty_input():
    m = compute_metrics([])
    assert m["summary"]["total_findings"] == 0
    assert m["by_severity"]["critical"] == 0
