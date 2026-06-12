import pandas as pd


def legacy_model_filter(df, variables, dep_var):
    filtered = df.dropna(subset=variables).copy()
    dv_std = filtered.groupby("sbti_id", observed=True)[dep_var].transform("std")
    constant_ids = filtered.loc[dv_std.fillna(1) == 0, "sbti_id"].unique()
    filtered = filtered[~filtered["sbti_id"].isin(constant_ids)].copy()
    obs_counts = filtered["sbti_id"].value_counts()
    singleton_ids = obs_counts[obs_counts == 1].index
    return filtered[~filtered["sbti_id"].isin(singleton_ids)].copy()


def test_singleton_firms_are_removed_where_legacy_model_removes_them():
    df = pd.DataFrame(
        [
            {"sbti_id": "A", "y": 1.0, "x": 1.0},
            {"sbti_id": "A", "y": 2.0, "x": 1.0},
            {"sbti_id": "B", "y": 3.0, "x": 1.0},
        ]
    )

    filtered = legacy_model_filter(df, ["y", "x"], "y")

    assert set(filtered["sbti_id"]) == {"A"}


def test_constant_dv_firms_are_removed_where_legacy_model_removes_them():
    df = pd.DataFrame(
        [
            {"sbti_id": "A", "y": 1.0, "x": 1.0},
            {"sbti_id": "A", "y": 2.0, "x": 1.0},
            {"sbti_id": "B", "y": 5.0, "x": 1.0},
            {"sbti_id": "B", "y": 5.0, "x": 1.0},
        ]
    )

    filtered = legacy_model_filter(df, ["y", "x"], "y")

    assert set(filtered["sbti_id"]) == {"A"}


def test_model_specific_listwise_deletion_is_preserved():
    df = pd.DataFrame(
        [
            {"sbti_id": "A", "y": 1.0, "x": 1.0},
            {"sbti_id": "A", "y": 2.0, "x": None},
            {"sbti_id": "A", "y": 3.0, "x": 1.0},
            {"sbti_id": "B", "y": 1.0, "x": 1.0},
            {"sbti_id": "B", "y": 2.0, "x": 1.0},
        ]
    )

    filtered = legacy_model_filter(df, ["y", "x"], "y")

    assert len(filtered) == 4
    assert filtered["x"].isna().sum() == 0
