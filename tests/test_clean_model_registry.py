from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def test_clean_model_registry_has_required_counts():
    registry = pd.read_csv(ROOT / "outputs/refactored_clean/diagnostics/model_registry.csv")

    assert registry["final_n"].notna().all()
    assert registry["firm_count"].notna().all()
    assert (registry["final_n"] > 0).all()
    assert (registry["firm_count"] > 0).all()


def test_clean_model_registry_records_event_and_leverage_families():
    registry = pd.read_csv(ROOT / "outputs/refactored_clean/diagnostics/model_registry.csv")

    assert "clean_event_study" in set(registry["model_family"])
    assert "clean_event_study_diagnostic" in set(registry["model_family"])
    assert "centered_leverage" in set(registry["model_family"])


def test_clean_outputs_do_not_overwrite_legacy_outputs():
    clean_report = ROOT / "outputs/refactored_clean/comparisons/refactored_clean_vs_legacy.md"
    legacy_report = ROOT / "outputs/refactored_legacy/comparisons/refactored_legacy_comparison.md"

    assert clean_report.exists()
    assert legacy_report.exists()
    assert clean_report.read_text(encoding="utf-8") != legacy_report.read_text(encoding="utf-8")
