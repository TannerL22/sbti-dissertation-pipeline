import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sbti_pipeline.clean_event_study import add_clean_event_bins


BIN_COLUMNS = [
    "clean_event_pre3_or_less",
    "clean_event_pre2",
    "reference_t_minus_1",
    "clean_event_0",
    "clean_event_1",
    "clean_event_2",
    "clean_event_3plus",
]


def test_clean_event_study_bins_are_mutually_exclusive():
    df = pd.DataFrame(
        {
            "fyear": [2017, 2018, 2019, 2020, 2021, 2022, 2023],
            "event_year": [2020] * 7,
        }
    )

    binned = add_clean_event_bins(df)

    assert (binned[BIN_COLUMNS].sum(axis=1) == 1).all()


def test_t_minus_one_is_reference_and_not_model_term():
    registry = pd.read_csv(ROOT / "outputs/refactored_clean/diagnostics/model_registry.csv")
    event_rows = registry[registry["model_family"] == "clean_event_study"]

    assert event_rows["formula"].str.contains("reference_t_minus_1").sum() == 0
    assert event_rows["formula"].str.contains("clean_event_pre2").all()


def test_broad_post_event_not_in_clean_event_study_formula():
    registry = pd.read_csv(ROOT / "outputs/refactored_clean/diagnostics/model_registry.csv")
    event_rows = registry[registry["model_family"] == "clean_event_study"]

    assert event_rows["formula"].str.contains("post_event").sum() == 0
