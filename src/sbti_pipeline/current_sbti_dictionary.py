from __future__ import annotations

import pandas as pd

from .config import LegacyConfig
from .current_sbti_loader import CurrentSBTIData
from .io import write_text


def build_dictionary_crosswalk(config: LegacyConfig, data: CurrentSBTIData) -> pd.DataFrame:
    dictionary = data.dictionary.copy()
    field_col = "field" if "field" in dictionary.columns else dictionary.columns[0]
    explanation_col = "explanation" if "explanation" in dictionary.columns else None

    source_columns = {
        "by_company": set(data.company.columns),
        "by_target": set(data.target.columns),
    }
    rows = []
    for _, row in dictionary.iterrows():
        field = row.get(field_col)
        field_norm = str(field).strip().lower() if pd.notna(field) else ""
        sources = [name for name, cols in source_columns.items() if field_norm in cols]
        used = _is_used_field(field_norm)
        rows.append(
            {
                "field_name": field_norm,
                "source_file_sheet": "; ".join(sources) if sources else "data_dictionary_only_or_renamed",
                "definition": row.get(explanation_col) if explanation_col else "",
                "inferred_type": row.get("data_type", ""),
                "used_in_overlay": bool(used),
                "overlay_variables_derived": "; ".join(_derived_variables(field_norm)),
                "notes_cautions": _field_caution(field_norm),
            }
        )
    out = pd.DataFrame(rows)
    out.to_csv(config.output_dir / "tables/current_sbti_data_dictionary_crosswalk.csv", index=False)

    ambiguous = out.loc[out["source_file_sheet"].eq("data_dictionary_only_or_renamed"), "field_name"].dropna()
    lines = [
        "# Data Dictionary Notes",
        "",
        "The data dictionary is used as field documentation for the current metadata overlay.",
        "Ambiguous or dictionary-only fields are documented rather than guessed into legacy variables.",
        "",
        f"Dictionary rows: {len(out):,}",
        f"Fields used in overlay: {int(out['used_in_overlay'].sum()):,}",
        f"Dictionary fields not directly matched to normalized workbook columns: {len(ambiguous):,}",
        "",
        "Current status and target metadata are current dashboard facts. They do not redefine historical treatment timing.",
    ]
    if len(ambiguous):
        lines.extend(["", "## Unmatched Or Renamed Fields"])
        lines.extend(f"- `{value}`" for value in ambiguous.head(50))
    write_text(config.output_dir / "diagnostics/data_dictionary_notes.md", "\n".join(lines) + "\n")
    return out


def _is_used_field(field: str) -> bool:
    keys = [
        "sbti_id",
        "company_name",
        "organization_type",
        "sector",
        "near_term",
        "long_term",
        "net_zero",
        "status",
        "reason",
        "validation_route",
        "action",
        "commitment",
        "target",
        "scope",
        "type",
        "sub_type",
        "base_year",
        "target_year",
        "date_published",
        "date_updated",
    ]
    return any(key in field for key in keys)


def _derived_variables(field: str) -> list[str]:
    variables: list[str] = []
    if field == "organization_type":
        variables += ["current_is_financial_institution", "current_is_sme", "current_is_corporate"]
    if field == "sector":
        variables += ["current_is_flag_relevant_sector_proxy", "current_is_automotive_sector_proxy"]
    if "scope" in field:
        variables += ["current_has_any_target_including_scope3", "current_has_legacy_like_absolute_scope3_target"]
    if "type" in field:
        variables += ["current_has_absolute_target", "current_has_engagement_target"]
    if "status" in field:
        variables += ["current_*_targets_set", "current_*_commitment_removed"]
    return variables


def _field_caution(field: str) -> str:
    if "status" in field:
        return "Current dashboard status only; not historical event-time status."
    if field in {"date_published", "date_updated"}:
        return "Date is from current export and should be interpreted cautiously for historical timing."
    if field in {"scope", "type", "sub_type"}:
        return "Used for current taxonomy flags only; legacy Scope 3 remains unchanged."
    return ""
