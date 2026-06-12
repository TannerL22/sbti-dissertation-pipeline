from __future__ import annotations

import pandas as pd

from .config import LegacyConfig


COMPANY_RENAME = {
    "company_name": "company_name_current",
    "isin": "isin_current",
    "lei": "lei_current",
    "organization_type": "organization_type_current",
    "location": "location_current",
    "region": "region_current",
    "sector": "sector_current",
    "near_term_status": "near_term_status_current",
    "near_term_target_classification": "near_term_target_classification_current",
    "near_term_target_year": "near_term_target_year_current",
    "long_term_status": "long_term_status_current",
    "long_term_target_classification": "long_term_target_classification_current",
    "long_term_target_year": "long_term_target_year_current",
    "net_zero_status": "net_zero_status_current",
    "net_zero_year": "net_zero_year_current",
    "ba15_status": "ba15_status_current",
    "target_classification_long": "target_classification_long_current",
    "reason_for_extension_or_removal": "reason_for_extension_or_removal_current",
    "date_updated": "date_updated_current",
    "date_updated_parsed": "date_updated_current_parsed",
}


def build_company_overlay(config: LegacyConfig, company: pd.DataFrame) -> pd.DataFrame:
    cols = ["sbti_id"] + [col for col in COMPANY_RENAME if col in company.columns]
    overlay = company[cols].copy().rename(columns=COMPANY_RENAME)
    overlay = overlay.drop_duplicates(subset=["sbti_id"], keep="first")

    near = _lower(overlay.get("near_term_status_current", pd.Series(index=overlay.index, dtype=object)))
    long = _lower(overlay.get("long_term_status_current", pd.Series(index=overlay.index, dtype=object)))
    netzero = _lower(overlay.get("net_zero_status_current", pd.Series(index=overlay.index, dtype=object)))
    org_type = _lower(overlay.get("organization_type_current", pd.Series(index=overlay.index, dtype=object)))
    reason = _lower(overlay.get("reason_for_extension_or_removal_current", pd.Series(index=overlay.index, dtype=object)))

    overlay["current_company_in_dashboard"] = 1
    overlay["current_near_term_targets_set"] = near.eq("targets set").astype(int)
    overlay["current_near_term_committed"] = near.eq("committed").astype(int)
    overlay["current_near_term_commitment_removed"] = near.eq("commitment removed").astype(int)
    overlay["current_long_term_targets_set"] = long.eq("targets set").astype(int)
    overlay["current_net_zero_targets_set"] = netzero.eq("targets set").astype(int)
    overlay["current_net_zero_committed"] = netzero.eq("committed").astype(int)
    overlay["current_net_zero_commitment_removed"] = netzero.eq("commitment removed").astype(int)
    overlay["current_has_net_zero_year"] = overlay.get("net_zero_year_current", pd.Series(index=overlay.index)).notna().astype(int)
    overlay["current_has_reason_for_extension_or_removal"] = reason.ne("").astype(int)
    overlay["current_is_financial_institution_by_org_type"] = org_type.str.contains("financial institution", na=False).astype(int)
    overlay["current_is_sme"] = org_type.eq("sme").astype(int)
    overlay["current_is_corporate"] = org_type.eq("corporate").astype(int)
    overlay["overlay_is_current_metadata"] = 1
    overlay["overlay_source_company_file"] = str((config.root / config.raw["company_file"]).relative_to(config.root))
    overlay["overlay_snapshot_date"] = config.raw.get("overlay_snapshot_date", "2026-05")
    overlay.to_csv(config.output_dir / "tables/current_company_overlay.csv", index=False)
    return overlay


def _lower(series: pd.Series) -> pd.Series:
    return series.fillna("").astype(str).str.strip().str.lower()
