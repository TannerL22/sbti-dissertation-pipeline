from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from .config import LegacyConfig
from .io import write_text


@dataclass(frozen=True)
class CurrentSBTIData:
    company: pd.DataFrame
    target: pd.DataFrame
    dictionary: pd.DataFrame
    blank_target_rows_dropped: int
    company_path: Path
    target_path: Path
    dictionary_path: Path


def normalize_column_name(value: object) -> str:
    text = str(value).strip().lower()
    for old, new in [("/", "_"), ("-", "_"), (" ", "_"), ("(", ""), (")", ""), ["%", "pct"]]:
        text = text.replace(old, new)
    while "__" in text:
        text = text.replace("__", "_")
    return text.strip("_")


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out.columns = [normalize_column_name(col) for col in out.columns]
    return out


def parse_date_series(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series, errors="coerce")


def load_current_sbti(config: LegacyConfig) -> CurrentSBTIData:
    raw = config.raw
    company_path = config.root / raw["company_file"]
    target_path = config.root / raw["target_file"]
    dictionary_path = config.root / raw["data_dictionary_file"]

    company = normalize_columns(pd.read_excel(company_path, sheet_name=raw.get("company_sheet", 0)))
    target_raw = normalize_columns(pd.read_excel(target_path, sheet_name=raw.get("target_sheet", 0)))
    dictionary = normalize_columns(pd.read_excel(dictionary_path, sheet_name=raw.get("data_dictionary_sheet", 0)))

    blank_mask = target_raw.isna().all(axis=1)
    target = target_raw.loc[~blank_mask].copy()
    blank_target_rows_dropped = int(blank_mask.sum())

    required_company = {"sbti_id", "company_name", "organization_type", "sector"}
    required_target = {"row_entry_id", "sbti_id", "action", "target", "scope", "type", "status"}
    missing_company = sorted(required_company - set(company.columns))
    missing_target = sorted(required_target - set(target.columns))
    if missing_company or missing_target:
        raise ValueError(
            f"Missing required SBTi fields. company={missing_company}; target={missing_target}"
        )

    for frame in [company, target]:
        for col in frame.columns:
            if col.startswith("date_") or col.endswith("_date") or col in {
                "commitment_deadline",
                "date_published",
                "date_updated",
                "ba15_date",
            }:
                frame[f"{col}_parsed"] = parse_date_series(frame[col])

    return CurrentSBTIData(
        company=company,
        target=target,
        dictionary=dictionary,
        blank_target_rows_dropped=blank_target_rows_dropped,
        company_path=company_path,
        target_path=target_path,
        dictionary_path=dictionary_path,
    )


def write_load_diagnostics(config: LegacyConfig, data: CurrentSBTIData) -> None:
    out = config.output_dir
    rows: list[dict[str, Any]] = []
    for source_name, path, frame in [
        ("by_company", data.company_path, data.company),
        ("by_target", data.target_path, data.target),
        ("data_dictionary", data.dictionary_path, data.dictionary),
    ]:
        for col in frame.columns:
            rows.append(
                {
                    "source_file": source_name,
                    "path": str(path.relative_to(config.root)),
                    "column": col,
                    "inferred_dtype": str(frame[col].dtype),
                    "non_null_rows": int(frame[col].notna().sum()),
                    "missing_rows": int(frame[col].isna().sum()),
                }
            )
    pd.DataFrame(rows).to_csv(out / "diagnostics/current_sbti_columns_by_file.csv", index=False)

    lines = [
        "# Current SBTi Load Summary",
        "",
        f"Company file: `{data.company_path.relative_to(config.root)}`",
        f"Target file: `{data.target_path.relative_to(config.root)}`",
        f"Data dictionary file: `{data.dictionary_path.relative_to(config.root)}`",
        "",
        f"By-company rows: {len(data.company):,}",
        f"By-company columns: {len(data.company.columns):,}",
        f"By-company unique sbti_id: {data.company['sbti_id'].nunique(dropna=True):,}",
        f"By-target usable rows: {len(data.target):,}",
        f"Fully blank by-target rows dropped: {data.blank_target_rows_dropped:,}",
        f"By-target columns: {len(data.target.columns):,}",
        f"By-target unique sbti_id: {data.target['sbti_id'].nunique(dropna=True):,}",
        f"Data dictionary rows: {len(data.dictionary):,}",
        "",
        "These files are treated as current May 2026 metadata and are not historical event-time facts.",
    ]
    write_text(out / "diagnostics/current_sbti_load_summary.md", "\n".join(lines) + "\n")
