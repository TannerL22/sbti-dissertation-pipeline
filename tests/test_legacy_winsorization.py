import pandas as pd


def winsorize_by_source(df, column, source_col, lower=0.01, upper=0.99):
    out = df.copy()
    out[column] = out.groupby(source_col, group_keys=False)[column].transform(
        lambda s: s.clip(s.quantile(lower), s.quantile(upper))
    )
    return out


def winsorize_global(df, column, lower=0.01, upper=0.99):
    out = df.copy()
    out[column] = out[column].clip(out[column].quantile(lower), out[column].quantile(upper))
    return out


def test_legacy_winsorization_is_source_specific():
    df = pd.DataFrame(
        {
            "source": ["public"] * 5 + ["private"] * 5,
            "metric": [1, 2, 3, 4, 1000, 10, 20, 30, 40, 50],
        }
    )

    source_specific = winsorize_by_source(df, "metric", "source")
    global_winsorized = winsorize_global(df, "metric")

    assert source_specific.loc[4, "metric"] < 1000
    assert source_specific.loc[9, "metric"] == 49.6
    assert source_specific["metric"].tolist() != global_winsorized["metric"].tolist()


def test_legacy_mode_does_not_replace_source_specific_with_global_winsorization():
    df = pd.DataFrame(
        {
            "source": ["public"] * 5 + ["private"] * 5,
            "metric": [1, 2, 3, 4, 1000, 10, 20, 30, 40, 50],
        }
    )

    legacy = winsorize_by_source(df, "metric", "source")
    robustness_candidate = winsorize_global(df, "metric")

    assert not legacy.equals(robustness_candidate)
