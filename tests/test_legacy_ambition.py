import numpy as np
import pandas as pd


def annual_reduction_rate(reduction_percent, base_year, target_year):
    horizon = target_year - base_year
    if horizon <= 0:
        return np.nan
    return reduction_percent / horizon


def most_ambitious_s1s2_rate(targets, event_date):
    df = targets.copy()
    df["validation_date"] = pd.to_datetime(df["validation_date"], errors="coerce")
    event_date = pd.Timestamp(event_date)
    eligible = df[
        (df["scope"].isin(["1+2", "1+2+3"]))
        & (df["type"].str.lower() == "absolute")
        & (df["validation_date"] <= event_date)
    ].copy()
    eligible["rate"] = eligible.apply(
        lambda row: annual_reduction_rate(
            row["reduction_percent"], row["base_year"], row["target_year"]
        ),
        axis=1,
    )
    return eligible["rate"].max()


def test_s1s2_annual_reduction_rate_divides_absolute_reduction_by_horizon():
    assert annual_reduction_rate(50, 2020, 2030) == 5


def test_only_targets_validated_on_or_before_main_event_are_eligible():
    targets = pd.DataFrame(
        [
            {"scope": "1+2", "type": "Absolute", "validation_date": "2021-01-01", "reduction_percent": 20, "base_year": 2020, "target_year": 2030},
            {"scope": "1+2", "type": "Absolute", "validation_date": "2022-01-01", "reduction_percent": 90, "base_year": 2020, "target_year": 2030},
        ]
    )

    assert most_ambitious_s1s2_rate(targets, "2021-06-01") == 2


def test_most_ambitious_qualifying_target_is_selected():
    targets = pd.DataFrame(
        [
            {"scope": "1+2", "type": "Absolute", "validation_date": "2021-01-01", "reduction_percent": 20, "base_year": 2020, "target_year": 2030},
            {"scope": "1+2", "type": "Absolute", "validation_date": "2021-02-01", "reduction_percent": 60, "base_year": 2020, "target_year": 2030},
        ]
    )

    assert most_ambitious_s1s2_rate(targets, "2021-06-01") == 6


def test_zero_or_invalid_target_horizons_are_handled_safely():
    assert np.isnan(annual_reduction_rate(50, 2030, 2030))
    assert np.isnan(annual_reduction_rate(50, 2031, 2030))
