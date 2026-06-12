from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
import statsmodels.formula.api as smf


@dataclass(frozen=True)
class FilterResult:
    data: pd.DataFrame
    initial_rows: int
    dropped_missing: int
    dropped_constant_dv: int
    dropped_singletons: int


def filter_model_data(
    df: pd.DataFrame,
    variables: list[str],
    dep_var: str,
    firm_col: str = "sbti_id",
    remove_constant_dv: bool = True,
    remove_singletons: bool = True,
) -> FilterResult:
    initial_rows = len(df)
    filtered = df.dropna(subset=variables).copy()
    after_missing = len(filtered)

    if remove_constant_dv and not filtered.empty:
        dv_std = filtered.groupby(firm_col, observed=True)[dep_var].transform("std")
        constant_ids = filtered.loc[dv_std.fillna(1) == 0, firm_col].unique()
        filtered = filtered[~filtered[firm_col].isin(constant_ids)].copy()
    after_constant = len(filtered)

    if remove_singletons and not filtered.empty:
        counts = filtered[firm_col].value_counts()
        singleton_ids = counts[counts == 1].index
        filtered = filtered[~filtered[firm_col].isin(singleton_ids)].copy()
        if hasattr(filtered[firm_col], "cat"):
            filtered[firm_col] = filtered[firm_col].cat.remove_unused_categories()
    final_rows = len(filtered)

    return FilterResult(
        data=filtered,
        initial_rows=initial_rows,
        dropped_missing=initial_rows - after_missing,
        dropped_constant_dv=after_missing - after_constant,
        dropped_singletons=after_constant - final_rows,
    )


def fit_legacy_ols(formula: str, data: pd.DataFrame, cluster_col: str = "sbti_id"):
    if len(data) == 0:
        return None
    return smf.ols(formula, data=data).fit(
        cov_type="cluster",
        cov_kwds={"groups": data[cluster_col]},
        drop_omitted=True,
    )


def registry_row(
    *,
    dep_var: str,
    model_name: str,
    formula: str,
    filter_result: FilterResult,
    result,
    controls: str,
    fixed_effects: str = "Firm & Year",
    cluster: str = "sbti_id",
) -> dict:
    data = filter_result.data
    return {
        "dependent_variable": dep_var,
        "model_name": model_name,
        "nobs": int(result.nobs) if result is not None else 0,
        "firm_count": int(data["sbti_id"].nunique()) if "sbti_id" in data else 0,
        "initial_rows": filter_result.initial_rows,
        "dropped_missing": filter_result.dropped_missing,
        "dropped_constant_dv": filter_result.dropped_constant_dv,
        "dropped_singletons": filter_result.dropped_singletons,
        "controls": controls,
        "fixed_effects": fixed_effects,
        "cluster": cluster,
        "formula": formula,
    }


def coefficient_rows(dep_var: str, model_name: str, result) -> list[dict]:
    rows = []
    if result is None:
        return rows
    for term in result.params.index:
        if term.startswith("C(sbti_id)") or term.startswith("C(fyear)"):
            continue
        rows.append(
            {
                "dependent_variable": dep_var,
                "model_name": model_name,
                "term": term,
                "coef": result.params[term],
                "std_error": result.bse[term],
                "p_value": result.pvalues[term],
            }
        )
    return rows
