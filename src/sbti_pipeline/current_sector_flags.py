from __future__ import annotations

import pandas as pd

from .config import LegacyConfig
from .io import write_text


FLAG_RELEVANT_SECTORS = {
    "Agricultural Production",
    "Agricultural Products",
    "Food and Beverage Processing",
    "Food Production - Agricultural Production",
    "Food Production - Animal Source Food Production",
    "Forest and Paper Products - Forestry, Timber, Pulp and Paper, Rubber",
    "Restaurants and Food Service",
    "Retailing",
    "Textiles, Apparel, Footwear and Luxury Goods",
}

AUTOMOTIVE_SECTORS = {"Automobiles and Components"}

OIL_GAS_PATTERNS = ["oil", "gas", "coal", "fossil"]
POWER_PATTERNS = ["electric utilities", "power producers", "energy traders", "utilities"]
CHEMICAL_PATTERNS = ["chemicals"]
BUILDING_PATTERNS = ["real estate", "building", "construction"]
HIGH_SCOPE3_SECTORS = {
    "Automobiles and Components",
    "Banks, Diverse Financials, Insurance",
    "Construction and Engineering",
    "Consumer Durables, Household and Personal Products",
    "Food and Beverage Processing",
    "Oil and Gas",
    "Retailing",
    "Textiles, Apparel, Footwear and Luxury Goods",
    "Trading Companies and Distributors, and Commercial Services and Supplies",
}


def build_sector_flags(
    config: LegacyConfig,
    company_overlay: pd.DataFrame,
    target_rows: pd.DataFrame,
    target_firm_overlay: pd.DataFrame,
) -> pd.DataFrame:
    base_cols = ["sbti_id"]
    if "sector_current" in company_overlay.columns:
        base_cols.append("sector_current")
    if "organization_type_current" in company_overlay.columns:
        base_cols.append("organization_type_current")
    flags = company_overlay[base_cols].copy()

    sector = _lower(flags.get("sector_current", pd.Series(index=flags.index, dtype=object)))
    org_type = _lower(flags.get("organization_type_current", pd.Series(index=flags.index, dtype=object)))

    flags["current_is_financial_institution"] = (
        org_type.str.contains("financial institution", na=False)
        | sector.str.contains("banks|financials|insurance", regex=True, na=False)
    ).astype(int)
    flags["current_is_flag_relevant_sector_proxy"] = flags.get("sector_current", "").isin(FLAG_RELEVANT_SECTORS).astype(int)
    flags["current_is_automotive_sector_proxy"] = flags.get("sector_current", "").isin(AUTOMOTIVE_SECTORS).astype(int)
    flags["current_is_oil_and_gas"] = _contains_any(sector, OIL_GAS_PATTERNS).astype(int)
    flags["current_is_power_or_utilities"] = _contains_any(sector, POWER_PATTERNS).astype(int)
    flags["current_is_chemicals"] = _contains_any(sector, CHEMICAL_PATTERNS).astype(int)
    flags["current_is_buildings_or_real_estate"] = _contains_any(sector, BUILDING_PATTERNS).astype(int)
    flags["current_is_high_scope3_sector_proxy"] = flags.get("sector_current", "").isin(HIGH_SCOPE3_SECTORS).astype(int)

    reason_by_firm = (
        target_rows.assign(_reason=_lower(target_rows.get("reason_for_commitment_extension_or_removal_current", pd.Series(index=target_rows.index))))
        .groupby("sbti_id")["_reason"]
        .agg(lambda values: " ; ".join(sorted({value for value in values if value})))
    )
    flags = flags.merge(reason_by_firm.rename("current_reason_fields_observed"), on="sbti_id", how="left")
    reason = _lower(flags["current_reason_fields_observed"])
    flags["current_has_automakers_pathway_reason"] = reason.str.contains("automakers pathway", na=False).astype(int)
    flags["current_has_observed_flag_target_proxy"] = (
        flags["sbti_id"].isin(
            target_rows.loc[
                target_rows.get("is_no_deforestation_target_current", pd.Series(index=target_rows.index, dtype=int)).eq(1),
                "sbti_id",
            ]
        )
        | reason.str.contains("timber|wood fiber|deforestation", regex=True, na=False)
    ).astype(int)
    flags["current_is_flag_relevant_any"] = (
        flags["current_is_flag_relevant_sector_proxy"].eq(1) | flags["current_has_observed_flag_target_proxy"].eq(1)
    ).astype(int)
    flags["current_is_automotive_any"] = (
        flags["current_is_automotive_sector_proxy"].eq(1) | flags["current_has_automakers_pathway_reason"].eq(1)
    ).astype(int)

    out_cols = ["sbti_id"] + [col for col in flags.columns if col.startswith("current_")]
    flags[out_cols].to_csv(config.output_dir / "tables/current_sector_flags.csv", index=False)
    _write_methodology(config)
    return flags[out_cols]


def _write_methodology(config: LegacyConfig) -> None:
    lines = [
        "# Current Sector Flag Methodology",
        "",
        "These flags are current metadata overlays for later robustness checks. They do not alter the legacy baseline.",
        "",
        "## FLAG-Relevant Sector Proxy",
        "The manually curated proxy includes:",
        *[f"- {sector}" for sector in sorted(FLAG_RELEVANT_SECTORS)],
        "",
        "The sector proxy may be over-inclusive because not every firm in these sectors has FLAG-covered emissions.",
        "The observed target proxy may be under-inclusive because it only captures visible current target/reason fields.",
        "",
        "## Automotive Proxy",
        "Automotive firms are flagged from `Automobiles and Components` and separately from observed `Automakers pathway` reason fields.",
        "",
        "## Other Caution Flags",
        "Oil and gas, power/utilities, chemicals, buildings/real estate, and high-Scope-3 sector proxies are string/sector based and should be used as sensitivity flags, not silent exclusions.",
    ]
    write_text(config.output_dir / "diagnostics/current_sector_flag_methodology.md", "\n".join(lines) + "\n")


def _lower(series: pd.Series) -> pd.Series:
    return series.fillna("").astype(str).str.strip().str.lower()


def _contains_any(series: pd.Series, patterns: list[str]) -> pd.Series:
    mask = pd.Series(False, index=series.index)
    for pattern in patterns:
        mask = mask | series.str.contains(pattern, case=False, na=False)
    return mask
