import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sbti_pipeline.diagnostics import panel_diagnostics


def test_refactored_panel_golden_counts():
    df = pd.read_parquet(ROOT / "data/derived/final_analytical_panel_v3.parquet")
    diag = panel_diagnostics(df)

    assert diag["rows"] == 59_496
    assert diag["adopter_firm_years"] == 32_484
    assert diag["duplicate_non_null_gvkey_fyear_groups"] == 13


def test_refactored_main_roa_model1_matches_legacy_n_and_signs():
    registry = pd.read_csv(ROOT / "outputs/refactored_legacy/diagnostics/main_model_registry.csv")
    coefs = pd.read_csv(ROOT / "outputs/refactored_legacy/diagnostics/main_coefficients.csv")

    row = registry[
        (registry["dependent_variable"] == "roa_winsorized")
        & (registry["model_name"] == "Model 1: Full Sample")
    ].iloc[0]
    assert int(row["nobs"]) == 23_141

    post_event = coefs[
        (coefs["dependent_variable"] == "roa_winsorized")
        & (coefs["model_name"] == "Model 1: Full Sample")
        & (coefs["term"] == "post_event")
    ].iloc[0]
    ambition = coefs[
        (coefs["dependent_variable"] == "roa_winsorized")
        & (coefs["model_name"] == "Model 1: Full Sample")
        & (coefs["term"] == "post_event_x_s1s2_rate")
    ].iloc[0]

    assert round(post_event["coef"], 3) == -0.006
    assert round(ambition["coef"], 3) == 0.000
