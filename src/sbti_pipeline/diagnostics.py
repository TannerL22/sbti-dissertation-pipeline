from __future__ import annotations

import pandas as pd


def panel_diagnostics(df: pd.DataFrame) -> dict:
    gvkey_dups = 0
    if {"gvkey", "fyear"}.issubset(df.columns):
        nonnull = df[df["gvkey"].notna()]
        counts = nonnull.groupby(["gvkey", "fyear"], dropna=False).size()
        gvkey_dups = int((counts > 1).sum())

    adopters = df[df["earliest_near_term_validation_date"].notna()]
    return {
        "rows": len(df),
        "columns": df.shape[1],
        "adopter_firm_years": len(adopters),
        "missing_sbti_id_rows": int(df["sbti_id"].isna().sum()) if "sbti_id" in df else None,
        "unique_sbti_id": int(df["sbti_id"].dropna().nunique()) if "sbti_id" in df else None,
        "duplicate_non_null_gvkey_fyear_groups": gvkey_dups,
    }
