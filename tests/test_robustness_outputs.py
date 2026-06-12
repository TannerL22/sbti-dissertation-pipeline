from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def test_methodology_robustness_outputs_are_written_to_dedicated_folder():
    required = [
        "outputs/methodology_robustness/tables/robustness_results_long.csv",
        "outputs/methodology_robustness/tables/robustness_results_wide.csv",
        "outputs/methodology_robustness/diagnostics/robustness_model_registry.csv",
        "outputs/methodology_robustness/comparisons/robustness_conclusion_matrix.md",
        "outputs/methodology_robustness/methodology_robustness_summary.md",
    ]

    for rel in required:
        assert (ROOT / rel).exists()


def test_robustness_result_paths_do_not_point_to_legacy_output_folders():
    registry = pd.read_csv(ROOT / "outputs/methodology_robustness/diagnostics/robustness_model_registry.csv")

    assert not registry.astype(str).apply(lambda col: col.str.contains("outputs/refactored_legacy|outputs/refactored_clean|outputs/legacy_reproduction", regex=True)).any().any()


def test_robustness_outputs_have_completed_models():
    results = pd.read_csv(ROOT / "outputs/methodology_robustness/tables/robustness_results_long.csv")
    registry = pd.read_csv(ROOT / "outputs/methodology_robustness/diagnostics/robustness_model_registry.csv")

    assert len(results) > 0
    assert (registry["final_n"] > 0).sum() > 0
