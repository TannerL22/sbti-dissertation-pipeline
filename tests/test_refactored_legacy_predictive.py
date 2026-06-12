from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def test_refactored_predictive_model_ns_match_legacy():
    registry = pd.read_csv(ROOT / "outputs/refactored_legacy/diagnostics/predictive_model_registry.csv")
    ns = dict(zip(registry["outcome"], registry["nobs"]))

    assert ns["Positive_ROA_Outcome"] == 1_477
    assert ns["Positive_OP_MARGIN_Outcome"] == 1_447
    assert ns["Positive_REVENUE_GROWTH_Outcome"] == 1_744
    assert ns["Positive_TOBINS_Q_Outcome"] == 1_022


def test_predictive_output_preserves_legacy_success_definition_note():
    registry = pd.read_csv(ROOT / "outputs/refactored_legacy/diagnostics/predictive_model_registry.csv")

    assert registry["success_definition"].str.contains(
        "post-event average greater than pre-event average", regex=False
    ).all()
