from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

PROTECTED = {
    "earliest_near_term_validation_date",
    "earliest_commitment_date",
    "event_year",
    "event_year_commit",
    "post_event",
    "post_event_commit",
    "s1s2_annual_reduction_rate",
    "has_s3_absolute_target",
    "s3_annual_reduction_rate",
}


def test_overlay_merge_does_not_duplicate_historical_rows():
    panel = pd.read_parquet(ROOT / "data/derived/final_analytical_panel_v3.parquet")
    robust = pd.read_parquet(
        ROOT / "outputs/methodology_robustness/diagnostics/historical_panel_with_current_overlay_for_robustness.parquet"
    )

    assert len(robust) == len(panel)
    assert robust["_historical_row_id"].is_unique


def test_unmatched_historical_firms_are_documented():
    diagnostics = (ROOT / "outputs/methodology_robustness/diagnostics/overlay_merge_diagnostics.md").read_text(
        encoding="utf-8"
    )

    assert "Unmatched firms:" in diagnostics
    assert "Unmatched Historical `sbti_id` Values" in diagnostics


def test_current_overlay_does_not_overwrite_historical_event_or_ambition_columns():
    robust = pd.read_parquet(
        ROOT / "outputs/methodology_robustness/diagnostics/historical_panel_with_current_overlay_for_robustness.parquet"
    )
    current_cols = {col for col in robust.columns if col.startswith("current_")}

    assert PROTECTED.issubset(robust.columns)
    assert PROTECTED.isdisjoint(current_cols)
