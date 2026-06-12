from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

PROTECTED_LEGACY_COLUMNS = {
    "earliest_near_term_validation_date",
    "first_commitment_date",
    "post_event",
    "post_commitment",
    "s1s2_annual_reduction_rate",
    "has_s3_absolute_target",
    "s3_annual_reduction_rate",
}


def test_current_overlay_variables_are_prefixed_and_do_not_overwrite_legacy_treatment_columns():
    overlay = pd.read_csv(ROOT / "outputs/current_sbti_overlay/current_sbti_firm_overlay.csv", nrows=1)
    allowed = {"sbti_id", "overlay_is_current_metadata", "overlay_source_company_file", "overlay_snapshot_date"}

    assert PROTECTED_LEGACY_COLUMNS.isdisjoint(overlay.columns)
    assert all(col in allowed or col.startswith("current_") for col in overlay.columns)


def test_current_status_fields_are_only_current_metadata():
    overlay = pd.read_csv(ROOT / "outputs/current_sbti_overlay/current_sbti_firm_overlay.csv", nrows=1)
    current_status_cols = [col for col in overlay.columns if "status" in col.lower()]

    assert current_status_cols
    assert all(col.startswith("current_") for col in current_status_cols)
    assert "post_event" not in overlay.columns
