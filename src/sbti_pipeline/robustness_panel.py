from __future__ import annotations

import pandas as pd

from .config import LegacyConfig
from .io import write_text

PROTECTED_HISTORICAL_COLUMNS = {
    "earliest_near_term_validation_date",
    "earliest_commitment_date",
    "event_year",
    "event_year_commit",
    "post_event",
    "post_event_commit",
    "s1s2_annual_reduction_rate",
    "has_s3_absolute_target",
    "s3_annual_reduction_rate",
}


def build_robustness_panel(config: LegacyConfig) -> pd.DataFrame:
    panel = pd.read_parquet(config.root / config.raw["historical_panel_path"])
    overlay = pd.read_parquet(config.root / config.raw["current_overlay_path"])

    panel["_historical_row_id"] = range(len(panel))
    panel["sbti_id"] = panel["sbti_id"].astype("string")
    overlay["sbti_id"] = overlay["sbti_id"].astype("string")

    collisions = sorted((set(panel.columns) & set(overlay.columns)) - {"sbti_id"})
    protected_collisions = sorted(set(collisions) & PROTECTED_HISTORICAL_COLUMNS)
    if protected_collisions:
        raise ValueError(f"Overlay would overwrite protected historical variables: {protected_collisions}")

    merged = panel.merge(overlay, on="sbti_id", how="left", validate="many_to_one", indicator="_overlay_merge")
    if len(merged) != len(panel):
        raise ValueError("Overlay merge changed historical panel row count.")
    merged["matched_overlay"] = merged["_overlay_merge"].eq("both").astype(int)
    merged = merged.sort_values("_historical_row_id").drop(columns=["_overlay_merge"])

    out_path = config.output_dir / "diagnostics/historical_panel_with_current_overlay_for_robustness.parquet"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    merged.to_parquet(out_path, index=False)
    write_merge_diagnostics(config, panel, overlay, merged, collisions)
    return merged


def write_merge_diagnostics(
    config: LegacyConfig,
    panel: pd.DataFrame,
    overlay: pd.DataFrame,
    merged: pd.DataFrame,
    collisions: list[str],
) -> None:
    hist_firms = set(panel["sbti_id"].dropna().astype(str))
    overlay_firms = set(overlay["sbti_id"].dropna().astype(str))
    unmatched = sorted(hist_firms - overlay_firms)
    matched_firms = hist_firms & overlay_firms
    matched_rows = int(merged["matched_overlay"].sum())
    unmatched_rows = len(merged) - matched_rows
    overlay_flag_cols = [c for c in merged.columns if c.startswith("current_")]

    lines = [
        "# Overlay Merge Diagnostics",
        "",
        "This is a robustness panel only. It is not a new canonical final panel.",
        "",
        f"Historical rows: {len(panel):,}",
        f"Historical unique firms with `sbti_id`: {len(hist_firms):,}",
        f"Matched firms: {len(matched_firms):,}",
        f"Unmatched firms: {len(unmatched):,}",
        f"Matched firm-years/rows: {matched_rows:,}",
        f"Unmatched firm-years/rows: {unmatched_rows:,}",
        f"Row match share: {matched_rows / len(merged):.1%}",
        f"Overlay flag/current columns attached: {len(overlay_flag_cols):,}",
        "",
        "No historical event, treatment, ambition, or legacy Scope 3 columns were overwritten.",
    ]
    if collisions:
        lines.extend(["", "Non-protected column name collisions avoided by merge rules:"])
        lines.extend(f"- `{col}`" for col in collisions[:100])
    if unmatched:
        lines.extend(["", "## Unmatched Historical `sbti_id` Values"])
        lines.extend(f"- `{value}`" for value in unmatched)
    write_text(config.output_dir / "diagnostics/overlay_merge_diagnostics.md", "\n".join(lines) + "\n")
