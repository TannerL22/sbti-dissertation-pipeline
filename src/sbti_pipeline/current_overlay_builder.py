from __future__ import annotations

from pathlib import Path

import pandas as pd

from .config import LegacyConfig
from .io import write_text

LEGACY_PROTECTED_COLUMNS = {
    "earliest_near_term_validation_date",
    "first_commitment_date",
    "post_event",
    "post_commitment",
    "s1s2_annual_reduction_rate",
    "has_s3_absolute_target",
    "s3_annual_reduction_rate",
}


def build_final_overlay(
    config: LegacyConfig,
    company_overlay: pd.DataFrame,
    target_firm_overlay: pd.DataFrame,
    sector_flags: pd.DataFrame,
) -> pd.DataFrame:
    overlay = company_overlay.merge(target_firm_overlay, on="sbti_id", how="left")
    overlay = overlay.merge(sector_flags, on="sbti_id", how="left", suffixes=("", "_sector"))
    overlay = overlay.rename(columns=_prefix_current_suffix_columns(overlay.columns))
    if overlay["sbti_id"].duplicated().any():
        dupes = overlay.loc[overlay["sbti_id"].duplicated(), "sbti_id"].head().tolist()
        raise ValueError(f"Final current overlay has duplicate sbti_id values, examples={dupes}")

    for col in overlay.columns:
        if col in {"sbti_id", "overlay_is_current_metadata", "overlay_source_company_file", "overlay_snapshot_date"}:
            continue
        if not col.startswith("current_"):
            raise ValueError(f"Overlay column lacks current_ prefix: {col}")
        if col in LEGACY_PROTECTED_COLUMNS:
            raise ValueError(f"Overlay column would overwrite protected legacy variable: {col}")

    flag_cols = [
        col
        for col in overlay.columns
        if col.startswith("current_is_")
        or col.startswith("current_has_")
        or col.startswith("current_near_term_")
        or col.startswith("current_long_term_")
        or col.startswith("current_net_zero_")
        or col == "current_company_in_dashboard"
    ]
    for col in flag_cols:
        if overlay[col].dtype.kind in "biufc":
            overlay[col] = overlay[col].fillna(0).astype(int)

    for col in [c for c in overlay.select_dtypes(include=["object"]).columns if c != "sbti_id"]:
        overlay[col] = overlay[col].where(overlay[col].isna(), overlay[col].astype(str))

    csv_path = config.output_dir / "current_sbti_firm_overlay.csv"
    parquet_path = config.output_dir / "current_sbti_firm_overlay.parquet"
    overlay.to_csv(csv_path, index=False)
    overlay.to_parquet(parquet_path, index=False)
    return overlay


def write_overlay_vs_legacy_diagnostics(config: LegacyConfig, overlay: pd.DataFrame) -> pd.DataFrame:
    panel = pd.read_parquet(config.root / config.raw["canonical_panel_path"])
    hist_firms = pd.DataFrame({"sbti_id": panel["sbti_id"].dropna().drop_duplicates()})
    hist_firms["sbti_id"] = hist_firms["sbti_id"].astype(str)
    overlay = overlay.copy()
    overlay["sbti_id"] = overlay["sbti_id"].astype(str)
    hist_firms["in_historical_panel"] = 1
    matched = hist_firms.merge(overlay, on="sbti_id", how="left", indicator=True)
    matched["matched_current_overlay"] = matched["_merge"].eq("both").astype(int)

    unique_hist = int(hist_firms["sbti_id"].nunique())
    matched_count = int(matched["matched_current_overlay"].sum())
    unmatched_count = unique_hist - matched_count
    current_not_hist = int((~overlay["sbti_id"].isin(hist_firms["sbti_id"])).sum())
    adopter_rows = panel.loc[panel["sbti_id"].notna()]
    adopter_firms = adopter_rows["sbti_id"].drop_duplicates()
    adopter_matched = int(adopter_firms.isin(overlay["sbti_id"]).sum())

    summary_rows = [
        {"metric": "unique_historical_sbti_id", "value": unique_hist},
        {"metric": "matched_to_current_overlay", "value": matched_count},
        {"metric": "not_matched_to_current_overlay", "value": unmatched_count},
        {"metric": "current_overlay_firms_not_in_historical_panel", "value": current_not_hist},
        {"metric": "match_rate_overall", "value": matched_count / unique_hist if unique_hist else 0},
        {"metric": "historical_adopter_firms_matched", "value": adopter_matched},
        {"metric": "historical_adopter_firm_years", "value": len(adopter_rows)},
    ]
    key_flags = [
        "current_is_financial_institution",
        "current_is_flag_relevant_any",
        "current_is_automotive_any",
        "current_is_oil_and_gas",
        "current_has_any_target_including_scope3",
        "current_has_legacy_like_absolute_scope3_target",
        "current_net_zero_targets_set",
        "current_near_term_targets_set",
    ]
    for flag in key_flags:
        if flag in matched.columns:
            summary_rows.append({"metric": f"matched_historical_{flag}", "value": int(matched[flag].fillna(0).sum())})

    summary = pd.DataFrame(summary_rows)
    summary.to_csv(config.output_dir / "comparisons/current_overlay_vs_legacy_panel.csv", index=False)

    lines = [
        "# Current Overlay Vs Legacy Panel",
        "",
        "These are diagnostics only. Current metadata classifications are not historical event-time classifications.",
        "",
        f"Unique historical `sbti_id`: {unique_hist:,}",
        f"Matched to current overlay: {matched_count:,}",
        f"Not matched to current overlay: {unmatched_count:,}",
        f"Current overlay firms not in historical panel: {current_not_hist:,}",
        f"Overall match rate: {matched_count / unique_hist:.1%}" if unique_hist else "Overall match rate: n/a",
        f"Historical adopter firm-years: {len(adopter_rows):,}",
        f"Historical adopter firms matched: {adopter_matched:,}",
        "",
        "## Matched Historical Current-Metadata Flag Counts",
    ]
    for flag in key_flags:
        if flag in matched.columns:
            lines.append(f"- `{flag}`: {int(matched[flag].fillna(0).sum()):,}")

    if "current_sector" in matched.columns:
        lines.extend(["", "## Top Sectors Among Matched Historical Firms"])
        for sector, count in matched.loc[matched["matched_current_overlay"].eq(1), "current_sector"].value_counts().head(15).items():
            lines.append(f"- {sector}: {count:,}")
    if "current_near_term_status" in matched.columns:
        lines.extend(["", "## Current Near-Term Status Distribution"])
        for status, count in matched.loc[matched["matched_current_overlay"].eq(1), "current_near_term_status"].value_counts(dropna=False).items():
            lines.append(f"- {status}: {count:,}")
    if "current_net_zero_status" in matched.columns:
        lines.extend(["", "## Current Net-Zero Status Distribution"])
        for status, count in matched.loc[matched["matched_current_overlay"].eq(1), "current_net_zero_status"].value_counts(dropna=False).items():
            lines.append(f"- {status}: {count:,}")

    write_text(config.output_dir / "comparisons/current_overlay_vs_legacy_panel.md", "\n".join(lines) + "\n")
    preview_path = config.output_dir / "diagnostics/historical_panel_with_current_overlay_preview.parquet"
    panel.merge(overlay, on="sbti_id", how="left").to_parquet(preview_path, index=False)
    return summary


def write_data_quality_report(
    config: LegacyConfig,
    company: pd.DataFrame,
    target_raw_rows: int,
    blank_target_rows_dropped: int,
    target_rows: pd.DataFrame,
    overlay: pd.DataFrame,
) -> None:
    lines = [
        "# Current Overlay Data Quality Report",
        "",
        f"By-company row count: {len(company):,}",
        f"By-company unique `sbti_id`: {company['sbti_id'].nunique(dropna=True):,}",
        f"By-target raw rows: {target_raw_rows:,}",
        f"Blank by-target rows dropped: {blank_target_rows_dropped:,}",
        f"By-target usable rows: {len(target_rows):,}",
        f"By-target unique `row_entry_id`: {target_rows['row_entry_id'].nunique(dropna=True):,}",
        f"By-target unique `sbti_id`: {target_rows['sbti_id'].nunique(dropna=True):,}",
        f"Final firm overlay rows: {len(overlay):,}",
        "",
        "## Target Row Counts",
        _counts_md(target_rows, "action_current"),
        _counts_md(target_rows, "target_current"),
        _counts_md(target_rows, "status_current"),
        _counts_md(target_rows, "type_current"),
        _counts_md(target_rows, "scope_current"),
        "",
        "## Date Ranges",
        _date_range_md(target_rows, "date_published_current_parsed"),
        _date_range_md(company, "date_updated_parsed"),
        "",
        f"Rows with `date_published` after 2025-06-30: {_after_date(target_rows, 'date_published_current_parsed', '2025-06-30'):,}",
        f"Rows with `date_published` after 2024-12-31: {_after_date(target_rows, 'date_published_current_parsed', '2024-12-31'):,}",
        "",
        "## Missingness",
        *[_missing_md(target_rows, col) for col in ["sbti_id", "action_current", "target_current", "scope_current", "type_current", "target_value_current", "base_year_current", "target_year_current", "date_published_current"]],
        "",
        "## Duplicate Checks",
        f"Duplicate company `sbti_id` rows: {int(company['sbti_id'].duplicated().sum()):,}",
        f"Duplicate target `row_entry_id` rows: {int(target_rows['row_entry_id'].duplicated().sum()):,}",
        f"Duplicate final overlay `sbti_id` rows: {int(overlay['sbti_id'].duplicated().sum()):,}",
        "",
        "## Ambiguity Notes",
        "- `status_current` primarily describes commitment rows and is not used to identify target rows.",
        "- `date_published_current` is retained as current tracker metadata and is not used to overwrite dissertation validation dates.",
        "- Current target-status changes may have occurred after the historical financial panel period.",
    ]
    write_text(config.output_dir / "diagnostics/current_overlay_data_quality_report.md", "\n".join(lines) + "\n")


def write_overlay_summary(config: LegacyConfig, overlay: pd.DataFrame, match_summary: pd.DataFrame) -> None:
    metrics = dict(zip(match_summary["metric"], match_summary["value"]))
    flag_counts = {}
    for flag in [
        "current_is_financial_institution",
        "current_is_flag_relevant_any",
        "current_is_automotive_any",
        "current_is_oil_and_gas",
        "current_has_any_target_including_scope3",
        "current_has_legacy_like_absolute_scope3_target",
        "current_net_zero_targets_set",
        "current_net_zero_commitment_removed",
        "current_near_term_targets_set",
        "current_near_term_commitment_removed",
    ]:
        if flag in overlay.columns:
            flag_counts[flag] = int(overlay[flag].fillna(0).sum())

    lines = [
        "# Current SBTi Overlay Summary",
        "",
        "Command: `python run_current_sbti_overlay.py --config configs/current_sbti_overlay.yaml`",
        "",
        "## Source Files",
        f"- `{config.raw['company_file']}`",
        f"- `{config.raw['target_file']}`",
        f"- `{config.raw['data_dictionary_file']}`",
        "",
        f"Overlay row count: {len(overlay):,}",
        f"Matched historical firm count: {int(metrics.get('matched_to_current_overlay', 0)):,}",
        f"Unmatched historical firm count: {int(metrics.get('not_matched_to_current_overlay', 0)):,}",
        f"Historical match rate: {float(metrics.get('match_rate_overall', 0)):.1%}",
        "",
        "## Key Current-Metadata Flag Counts",
    ]
    lines.extend(f"- `{flag}`: {count:,}" for flag, count in flag_counts.items())
    lines.extend(
        [
            "",
            "## Caveats",
            "- These are May 2026 current metadata overlays, not event-time treatment variables.",
            "- Current statuses do not change historical validation, commitment, ambition, or legacy Scope 3 variables.",
            "- Sector and target-type flags are prepared for Phase 4 robustness checks only.",
            "",
            "Safe to proceed to Phase 4 methodology-aware robustness checks: yes, subject to using these fields as overlay metadata only.",
        ]
    )
    write_text(config.output_dir / "current_overlay_summary.md", "\n".join(lines) + "\n")


def _counts_md(df: pd.DataFrame, col: str) -> str:
    if col not in df.columns:
        return f"`{col}`: missing"
    lines = [f"`{col}`:"]
    for value, count in df[col].value_counts(dropna=False).head(30).items():
        lines.append(f"  - {value}: {count:,}")
    return "\n".join(lines)


def _date_range_md(df: pd.DataFrame, col: str) -> str:
    if col not in df.columns:
        return f"`{col}`: missing"
    series = pd.to_datetime(df[col], errors="coerce")
    return f"`{col}`: {series.min()} to {series.max()} (non-null {series.notna().sum():,})"


def _after_date(df: pd.DataFrame, col: str, date: str) -> int:
    if col not in df.columns:
        return 0
    return int((pd.to_datetime(df[col], errors="coerce") > pd.Timestamp(date)).sum())


def _missing_md(df: pd.DataFrame, col: str) -> str:
    if col not in df.columns:
        return f"- `{col}`: missing"
    return f"- `{col}` missing: {int(df[col].isna().sum()):,}"


def _prefix_current_suffix_columns(columns: pd.Index) -> dict[str, str]:
    renames: dict[str, str] = {}
    for col in columns:
        if col in {"sbti_id", "overlay_is_current_metadata", "overlay_source_company_file", "overlay_snapshot_date"}:
            continue
        if col.startswith("current_"):
            continue
        if col.endswith("_current"):
            renames[col] = "current_" + col[: -len("_current")]
        elif col.endswith("_current_parsed"):
            base = col[: -len("_current_parsed")]
            renames[col] = f"current_{base}_parsed"
    return renames
