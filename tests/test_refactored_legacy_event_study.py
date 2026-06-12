from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def _coef(df, dv, spec, term):
    row = df[
        (df["dependent_variable"] == dv)
        & (df["specification"] == spec)
        & (df["term"] == term)
    ].iloc[0]
    return row


def test_event_study_forces_legacy_no_size_fallback_for_revenue_growth_and_log_revenue():
    registry = pd.read_csv(ROOT / "outputs/refactored_legacy/diagnostics/event_study_model_registry.csv")

    revenue = registry[registry["dependent_variable"] == "revenue_growth_winsorized"].iloc[0]
    log_revt = registry[registry["dependent_variable"] == "log_revt"].iloc[0]

    assert revenue["model_name"] == "legacy_event_study_no_size_fallback"
    assert revenue["controls"] == "leverage_winsorized"
    assert int(revenue["nobs"]) == 23_155
    assert log_revt["model_name"] == "legacy_event_study_no_size_fallback"
    assert log_revt["controls"] == "leverage_winsorized"
    assert int(log_revt["nobs"]) == 25_437


def test_event_study_fallback_coefficients_match_legacy_stored_values():
    comparison = pd.read_csv(
        ROOT / "outputs/refactored_legacy/diagnostics/event_study_full_vs_fallback_coefficients.csv"
    )

    revenue_intercept = _coef(comparison, "revenue_growth_winsorized", "no_size_fallback", "Intercept")
    revenue_post = _coef(comparison, "revenue_growth_winsorized", "no_size_fallback", "post_event")
    log_revt_intercept = _coef(comparison, "log_revt", "no_size_fallback", "Intercept")
    log_revt_post = _coef(comparison, "log_revt", "no_size_fallback", "post_event")

    assert round(revenue_intercept["coef"], 4) == -0.0008
    assert round(revenue_post["coef"], 4) == 0.0020
    assert round(log_revt_intercept["coef"], 4) == 22.1259
    assert round(log_revt_post["coef"], 4) == -0.0502


def test_event_study_full_spec_is_selected_for_other_legacy_dvs():
    registry = pd.read_csv(ROOT / "outputs/refactored_legacy/diagnostics/event_study_model_registry.csv")
    selected = dict(zip(registry["dependent_variable"], registry["model_name"]))

    assert selected["roa_winsorized"] == "legacy_event_study_full"
    assert selected["op_margin_winsorized"] == "legacy_event_study_full"
    assert selected["log_ebitda"] == "legacy_event_study_full"
    assert selected["log_emp"] == "legacy_event_study_full"
