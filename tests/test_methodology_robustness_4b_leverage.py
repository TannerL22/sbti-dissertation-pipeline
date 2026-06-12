import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sbti_pipeline.methodology_robustness_4b import prepare_4b_data


def test_leverage_squared_terms_are_constructed_correctly():
    df = pd.DataFrame(
        {
            "firm_type": ["public", "private"],
            "post_event": [0, 1],
            "s1s2_annual_reduction_rate": [2.0, 3.0],
            "post_event_x_s1s2_rate": [0.0, 3.0],
            "leverage_winsorized": [0.2, 0.5],
        }
    )
    out = prepare_4b_data(df)

    assert out.loc[0, "leverage_sq"] == pytest.approx(0.04)
    assert out.loc[1, "leverage_sq"] == pytest.approx(0.25)
    assert out.loc[0, "post_event_x_leverage_sq"] == 0.0
    assert out.loc[1, "post_event_x_leverage_sq"] == pytest.approx(0.25)


def test_centered_leverage_outputs_include_centered_and_uncentered_terms():
    results = pd.read_csv(ROOT / "outputs/methodology_robustness_4b/tables/leverage_trap_robustness_results.csv")
    terms = set(results["term"])

    assert "post_event_x_leverage_sq" in terms
    assert "post_event_x_leverage_centered_sq" in terms
    assert "leverage_centered_sq" in terms


def test_leverage_exclusion_scenarios_do_not_increase_n():
    registry = pd.read_csv(ROOT / "outputs/methodology_robustness_4b/diagnostics/leverage_trap_model_registry.csv")
    roa = registry[registry["dependent_variable"].eq("roa_winsorized")].set_index("scenario")

    assert roa.loc["exclude_financial_institutions_legacy_leverage", "starting_rows"] <= roa.loc["matched_overlay_all_legacy_leverage", "starting_rows"]
    assert roa.loc["exclude_all_standard_sensitive_legacy_leverage", "starting_rows"] <= roa.loc["matched_overlay_all_legacy_leverage", "starting_rows"]


def test_leverage_outputs_are_in_phase4b_folder():
    assert (ROOT / "outputs/methodology_robustness_4b/tables/leverage_trap_robustness_results.csv").exists()
    assert not (ROOT / "outputs/methodology_robustness/tables/leverage_trap_robustness_results.csv").exists()
