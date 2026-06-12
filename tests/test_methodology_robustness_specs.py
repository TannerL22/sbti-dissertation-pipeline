from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def test_finance_exclusion_and_subsample_partition_matched_overlay_rows():
    scenarios = pd.read_csv(ROOT / "outputs/methodology_robustness/diagnostics/robustness_scenario_samples.csv")
    rows = scenarios.set_index("scenario")["starting_rows"]

    assert rows["exclude_financial_institutions"] + rows["financial_institutions_only"] == rows["matched_overlay_all"]


def test_sample_exclusions_do_not_increase_n():
    scenarios = pd.read_csv(ROOT / "outputs/methodology_robustness/diagnostics/robustness_scenario_samples.csv")
    matched = int(scenarios.loc[scenarios["scenario"].eq("matched_overlay_all"), "starting_rows"].iloc[0])
    excluded = scenarios[scenarios["scenario"].str.startswith("exclude_")]

    assert (excluded["starting_rows"] <= matched).all()


def test_current_status_scenarios_are_labeled_post_treatment_current_metadata():
    scenarios = pd.read_csv(ROOT / "outputs/methodology_robustness/diagnostics/robustness_scenario_samples.csv")
    status_rows = scenarios[scenarios["scenario"].str.contains("current_near_term|current_net_zero|commitment_removed")]

    assert not status_rows.empty
    assert status_rows["caveat_category"].eq("post_treatment_current_status_sensitivity").all()
