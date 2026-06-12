from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_refactored_legacy_outputs_exist():
    expected = [
        "outputs/refactored_legacy/tables/regression_results_refactored.txt",
        "outputs/refactored_legacy/tables/dynamic_event_study_regression_tables_refactored.txt",
        "outputs/refactored_legacy/tables/predictive_logit_results_final_refactored.txt",
        "outputs/refactored_legacy/diagnostics/main_model_registry.csv",
        "outputs/refactored_legacy/diagnostics/event_study_model_registry.csv",
        "outputs/refactored_legacy/diagnostics/predictive_model_registry.csv",
        "outputs/refactored_legacy/comparisons/refactored_legacy_comparison.md",
    ]

    for rel in expected:
        path = ROOT / rel
        assert path.exists(), rel
        assert path.stat().st_size > 0, rel


def test_refactored_comparison_report_records_phase_2a_boundaries():
    report = (
        ROOT / "outputs/refactored_legacy/comparisons/refactored_legacy_comparison.md"
    ).read_text(encoding="utf-8")

    assert "Legacy compatibility mode is applied" in report
    assert "Current SBTi metadata is not merged" in report
    assert "overlapping dummies are intentionally preserved" in report
