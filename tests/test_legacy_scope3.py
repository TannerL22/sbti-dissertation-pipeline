import pandas as pd


def legacy_scope3_absolute_targets(targets, event_date):
    df = targets.copy()
    df["validation_date"] = pd.to_datetime(df["validation_date"], errors="coerce")
    event_date = pd.Timestamp(event_date)
    return df[
        (df["scope"].astype(str).str.strip() == "3")
        & (df["type"].astype(str).str.strip().str.lower() == "absolute")
        & (df["validation_date"] <= event_date)
    ]


def test_legacy_scope3_flag_requires_standalone_scope_3_and_absolute_type():
    targets = pd.DataFrame(
        [
            {"scope": "3", "type": "Absolute", "validation_date": "2021-01-01"},
            {"scope": "3", "type": "Intensity", "validation_date": "2021-01-01"},
            {"scope": "1+2+3", "type": "Absolute", "validation_date": "2021-01-01"},
        ]
    )

    eligible = legacy_scope3_absolute_targets(targets, "2021-06-01")

    assert len(eligible) == 1
    assert eligible.iloc[0]["scope"] == "3"
    assert eligible.iloc[0]["type"] == "Absolute"


def test_combined_scope_1_2_3_is_not_counted_in_legacy_scope3_variable():
    targets = pd.DataFrame(
        [{"scope": "1+2+3", "type": "Absolute", "validation_date": "2021-01-01"}]
    )

    eligible = legacy_scope3_absolute_targets(targets, "2021-06-01")

    assert eligible.empty


def test_broader_scope3_flags_are_not_used_in_legacy_replication():
    targets = pd.DataFrame(
        [
            {"scope": "1+2+3", "type": "Absolute", "validation_date": "2021-01-01", "scope_includes_3": True},
            {"scope": "3", "type": "Engagement", "validation_date": "2021-01-01", "any_scope3_target": True},
        ]
    )

    eligible = legacy_scope3_absolute_targets(targets, "2021-06-01")

    assert eligible.empty


def test_scope3_targets_after_main_validation_event_are_excluded():
    targets = pd.DataFrame(
        [
            {"scope": "3", "type": "Absolute", "validation_date": "2022-01-01"},
            {"scope": "3", "type": "Absolute", "validation_date": "2020-01-01"},
        ]
    )

    eligible = legacy_scope3_absolute_targets(targets, "2021-06-01")

    assert len(eligible) == 1
    assert eligible.iloc[0]["validation_date"] == pd.Timestamp("2020-01-01")
