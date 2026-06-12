import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sbti_pipeline.methodology_robustness_4b import prepare_4b_data


def test_public_private_split_samples_do_not_overlap():
    panel = pd.read_parquet(
        ROOT / "outputs/methodology_robustness/diagnostics/historical_panel_with_current_overlay_for_robustness.parquet"
    )
    prepared = prepare_4b_data(panel[panel["earliest_near_term_validation_date"].notna()].copy())
    matched = prepared[prepared["matched_overlay"].eq(1)]
    public_ids = set(matched.loc[matched["firm_type"].eq("public"), "_historical_row_id"])
    private_ids = set(matched.loc[matched["firm_type"].eq("private"), "_historical_row_id"])

    assert public_ids.isdisjoint(private_ids)
    assert len(public_ids) + len(private_ids) == len(matched)


def test_public_private_split_sample_sizes_sum_to_matched_sample():
    registry = pd.read_csv(ROOT / "outputs/methodology_robustness_4b/diagnostics/public_private_model_registry.csv")
    roa = registry[registry["dependent_variable"].eq("roa_winsorized")]
    public_rows = int(roa.loc[roa["scenario"].eq("matched_overlay_all_public"), "starting_rows"].iloc[0])
    private_rows = int(roa.loc[roa["scenario"].eq("matched_overlay_all_private"), "starting_rows"].iloc[0])

    assert public_rows + private_rows == 32400


def test_pooled_interaction_excludes_private_main_effect_under_firm_fe():
    interactions = pd.read_csv(ROOT / "outputs/methodology_robustness_4b/tables/public_private_interaction_results.csv")
    terms = set(interactions["term"].dropna())

    assert "private_dummy" not in terms
    assert "post_event_x_private_dummy" in terms
    assert "post_event_x_s1s2_rate_x_private_dummy" in terms


def test_public_private_outputs_are_in_phase4b_folder():
    assert (ROOT / "outputs/methodology_robustness_4b/tables/public_private_robustness_results_long.csv").exists()
    assert not (ROOT / "outputs/methodology_robustness/tables/public_private_robustness_results_long.csv").exists()
