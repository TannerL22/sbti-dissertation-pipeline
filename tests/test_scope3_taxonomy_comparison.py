from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def test_scope3_taxonomy_outputs_exist_and_include_legacy_and_current_definitions():
    counts = pd.read_csv(ROOT / "outputs/methodology_robustness/comparisons/scope3_taxonomy_counts.csv")
    names = set(counts["scope3_definition"])

    assert "has_s3_absolute_target" in names
    assert "current_has_legacy_like_absolute_scope3_target" in names
    assert "current_has_any_target_including_scope3" in names


def test_scope3_overlap_matrix_is_two_by_two_or_subset_with_counts():
    overlap = pd.read_csv(ROOT / "outputs/methodology_robustness/comparisons/scope3_taxonomy_overlap_matrix.csv")

    assert "legacy_absolute_s3" in overlap.columns
    assert len(overlap) >= 1
