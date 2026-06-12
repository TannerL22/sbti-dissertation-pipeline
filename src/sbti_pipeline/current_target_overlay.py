from __future__ import annotations

import pandas as pd

from .config import LegacyConfig


TARGET_RENAME = {
    "company_name": "company_name_current_target",
    "organization_type": "organization_type_current_target",
    "validation_route": "validation_route_current",
    "action": "action_current",
    "commitment_type": "commitment_type_current",
    "commitment_deadline": "commitment_deadline_current",
    "status": "status_current",
    "reason_for_commitment_extension_or_removal": "reason_for_commitment_extension_or_removal_current",
    "company_temperature_alignment": "company_temperature_alignment_current",
    "target": "target_current",
    "target_wording": "target_wording_current",
    "scope": "scope_current",
    "target_value": "target_value_current",
    "type": "type_current",
    "sub_type": "sub_type_current",
    "target_classification_short": "target_classification_short_current",
    "base_year": "base_year_current",
    "target_year": "target_year_current",
    "year_type": "year_type_current",
    "date_published": "date_published_current",
    "date_published_parsed": "date_published_current_parsed",
}


def normalize_target_rows(config: LegacyConfig, target: pd.DataFrame) -> pd.DataFrame:
    cols = ["row_entry_id", "sbti_id"] + [col for col in TARGET_RENAME if col in target.columns]
    rows = target[cols].copy().rename(columns=TARGET_RENAME)
    if "date_published_current_parsed" not in rows.columns and "date_published_current" in rows.columns:
        rows["date_published_current_parsed"] = pd.to_datetime(rows["date_published_current"], errors="coerce")

    action = _lower(rows["action_current"])
    target_kind = _lower(rows.get("target_current", pd.Series(index=rows.index, dtype=object)))
    status = _lower(rows.get("status_current", pd.Series(index=rows.index, dtype=object)))
    target_type = _lower(rows.get("type_current", pd.Series(index=rows.index, dtype=object)))
    scope = _scope_text(rows.get("scope_current", pd.Series(index=rows.index, dtype=object)))

    rows["is_commitment_row_current"] = action.eq("commitment").astype(int)
    rows["is_target_row_current"] = action.eq("target").astype(int)
    rows["is_near_term_target_row_current"] = (action.eq("target") & target_kind.eq("near-term")).astype(int)
    rows["is_long_term_target_row_current"] = (action.eq("target") & target_kind.eq("long-term")).astype(int)
    rows["is_net_zero_target_row_current"] = (action.eq("target") & target_kind.eq("net-zero")).astype(int)
    rows["is_long_term_pre_cnzs_row_current"] = (action.eq("target") & target_kind.eq("long-term pre-cnzs")).astype(int)
    rows["is_active_commitment_current"] = (action.eq("commitment") & status.eq("active")).astype(int)
    rows["is_removed_commitment_current"] = (action.eq("commitment") & status.eq("removed")).astype(int)
    rows["is_extended_commitment_current"] = (action.eq("commitment") & status.eq("extended")).astype(int)
    rows["is_target_set_commitment_current"] = (action.eq("commitment") & status.eq("target set")).astype(int)

    rows["is_absolute_target_current"] = target_type.eq("absolute").astype(int)
    rows["is_intensity_target_current"] = target_type.eq("intensity").astype(int)
    rows["is_engagement_target_current"] = target_type.eq("engagement").astype(int)
    rows["is_renewable_electricity_target_current"] = target_type.eq("renewable electricity").astype(int)
    rows["is_no_deforestation_target_current"] = target_type.str.contains("deforestation", na=False).astype(int)
    rows["is_fossil_fuel_finance_target_current"] = target_type.eq("fossil fuel finance").astype(int)
    rows["is_fossil_fuel_equipment_target_current"] = target_type.eq("fossil fuel equipment").astype(int)
    rows["is_ice_phaseout_target_current"] = target_type.eq("ice phaseout").astype(int)
    rows["is_portfolio_alignment_target_current"] = target_type.str.contains("portfolio", na=False).astype(int)

    rows["scope_is_1_current"] = scope.eq("1").astype(int)
    rows["scope_is_2_current"] = scope.eq("2").astype(int)
    rows["scope_is_3_current"] = scope.eq("3").astype(int)
    rows["scope_includes_1_current"] = scope.str.contains("1", regex=False, na=False).astype(int)
    rows["scope_includes_2_current"] = scope.str.contains("2", regex=False, na=False).astype(int)
    rows["scope_includes_3_current"] = scope.str.contains("3", regex=False, na=False).astype(int)
    rows["scope_is_combined_1_2_current"] = scope.eq("1+2").astype(int)
    rows["scope_is_combined_1_2_3_current"] = scope.eq("1+2+3").astype(int)

    rows["has_valid_target_value_current"] = pd.to_numeric(rows.get("target_value_current"), errors="coerce").notna().astype(int)
    rows["has_valid_base_year_current"] = pd.to_numeric(rows.get("base_year_current"), errors="coerce").notna().astype(int)
    rows["has_valid_target_year_current"] = pd.to_numeric(rows.get("target_year_current"), errors="coerce").notna().astype(int)
    rows["target_horizon_current"] = (
        pd.to_numeric(rows.get("target_year_current"), errors="coerce")
        - pd.to_numeric(rows.get("base_year_current"), errors="coerce")
    )

    rows.to_csv(config.output_dir / "tables/current_target_rows_normalized.csv", index=False)
    return rows


def aggregate_target_overlay(config: LegacyConfig, rows: pd.DataFrame) -> pd.DataFrame:
    group = rows.groupby("sbti_id", dropna=True)
    overlay = pd.DataFrame(index=group.size().index)
    overlay["current_target_row_count"] = group["is_target_row_current"].sum()
    overlay["current_commitment_row_count"] = group["is_commitment_row_current"].sum()
    overlay["current_near_term_target_row_count"] = group["is_near_term_target_row_current"].sum()
    overlay["current_long_term_target_row_count"] = group["is_long_term_target_row_current"].sum()
    overlay["current_net_zero_target_row_count"] = group["is_net_zero_target_row_current"].sum()

    for kind, flag in [
        ("near_term", "is_near_term_target_row_current"),
        ("long_term", "is_long_term_target_row_current"),
        ("net_zero", "is_net_zero_target_row_current"),
    ]:
        overlay[f"current_first_{kind}_target_date_published"] = (
            rows.loc[rows[flag].eq(1)].groupby("sbti_id")["date_published_current_parsed"].min()
        )
    overlay["current_latest_target_date_published"] = group["date_published_current_parsed"].max()

    flag_map = {
        "current_has_near_term_target_row": "is_near_term_target_row_current",
        "current_has_long_term_target_row": "is_long_term_target_row_current",
        "current_has_net_zero_target_row": "is_net_zero_target_row_current",
        "current_has_absolute_target": "is_absolute_target_current",
        "current_has_intensity_target": "is_intensity_target_current",
        "current_has_engagement_target": "is_engagement_target_current",
        "current_has_renewable_electricity_target": "is_renewable_electricity_target_current",
        "current_has_no_deforestation_target": "is_no_deforestation_target_current",
        "current_has_fossil_fuel_finance_target": "is_fossil_fuel_finance_target_current",
        "current_has_fossil_fuel_equipment_target": "is_fossil_fuel_equipment_target_current",
        "current_has_ice_phaseout_target": "is_ice_phaseout_target_current",
        "current_has_portfolio_alignment_target": "is_portfolio_alignment_target_current",
        "current_has_any_scope1_target": "scope_includes_1_current",
        "current_has_any_scope2_target": "scope_includes_2_current",
        "current_has_any_scope3_target": "scope_includes_3_current",
        "current_has_scope1_only_target": "scope_is_1_current",
        "current_has_scope2_only_target": "scope_is_2_current",
        "current_has_scope3_only_target": "scope_is_3_current",
        "current_has_combined_scope1_2_target": "scope_is_combined_1_2_current",
        "current_has_combined_scope1_2_3_target": "scope_is_combined_1_2_3_current",
    }
    for out_col, in_col in flag_map.items():
        overlay[out_col] = group[in_col].max()

    scope3 = rows["scope_includes_3_current"].eq(1)
    standalone_scope3 = rows["scope_is_3_current"].eq(1)
    absolute = rows["is_absolute_target_current"].eq(1)
    intensity = rows["is_intensity_target_current"].eq(1)
    engagement = rows["is_engagement_target_current"].eq(1)
    no_deforest = rows["is_no_deforestation_target_current"].eq(1)

    overlay["current_has_legacy_like_absolute_scope3_target"] = rows.loc[standalone_scope3 & absolute].groupby("sbti_id").size().gt(0).astype(int)
    overlay["current_has_any_target_including_scope3"] = rows.loc[scope3].groupby("sbti_id").size().gt(0).astype(int)
    overlay["current_has_absolute_target_including_scope3"] = rows.loc[scope3 & absolute].groupby("sbti_id").size().gt(0).astype(int)
    overlay["current_has_intensity_target_including_scope3"] = rows.loc[scope3 & intensity].groupby("sbti_id").size().gt(0).astype(int)
    overlay["current_has_engagement_target_including_scope3"] = rows.loc[scope3 & engagement].groupby("sbti_id").size().gt(0).astype(int)
    overlay["current_has_no_deforestation_target_including_scope3"] = rows.loc[scope3 & no_deforest].groupby("sbti_id").size().gt(0).astype(int)

    type_lists = rows.loc[scope3].groupby("sbti_id")["type_current"].agg(lambda values: sorted({str(v) for v in values if pd.notna(v)}))
    overlay["current_scope3_target_types_observed"] = type_lists.map(lambda values: "; ".join(values) if isinstance(values, list) else "")
    overlay["current_scope3_target_type_count"] = type_lists.map(lambda values: len(values) if isinstance(values, list) else 0)

    overlay["current_min_target_year"] = group["target_year_current"].min()
    overlay["current_max_target_year"] = group["target_year_current"].max()
    overlay["current_missing_target_value_count"] = group["has_valid_target_value_current"].apply(lambda s: int((s == 0).sum()))
    overlay["current_missing_base_year_count"] = group["has_valid_base_year_current"].apply(lambda s: int((s == 0).sum()))
    overlay["current_missing_target_year_count"] = group["has_valid_target_year_current"].apply(lambda s: int((s == 0).sum()))

    statuses = rows.loc[rows["is_commitment_row_current"].eq(1)].copy()
    if not statuses.empty:
        pivot = pd.crosstab(statuses["sbti_id"], _lower(statuses["status_current"]))
        for status_col in pivot.columns:
            overlay[f"current_commitment_status_count_{_safe_suffix(status_col)}"] = pivot[status_col]

    overlay = overlay.fillna({col: 0 for col in overlay.columns if col.startswith("current_has_") or col.endswith("_count") or col.endswith("_row_count")})
    overlay = overlay.reset_index()
    overlay.to_csv(config.output_dir / "tables/current_target_firm_overlay.csv", index=False)
    return overlay


def _lower(series: pd.Series) -> pd.Series:
    return series.fillna("").astype(str).str.strip().str.lower()


def _scope_text(series: pd.Series) -> pd.Series:
    return series.fillna("").astype(str).str.strip().str.replace(" ", "", regex=False)


def _safe_suffix(value: object) -> str:
    return str(value).strip().lower().replace(" ", "_").replace("-", "_")
