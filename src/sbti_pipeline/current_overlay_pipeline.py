from __future__ import annotations

from .config import LegacyConfig
from .current_company_overlay import build_company_overlay
from .current_overlay_builder import (
    build_final_overlay,
    write_data_quality_report,
    write_overlay_summary,
    write_overlay_vs_legacy_diagnostics,
)
from .current_sbti_dictionary import build_dictionary_crosswalk
from .current_sbti_loader import load_current_sbti, write_load_diagnostics
from .current_sector_flags import build_sector_flags
from .current_target_overlay import aggregate_target_overlay, normalize_target_rows
from .io import ensure_output_dirs


def run_current_overlay(config: LegacyConfig) -> dict[str, str]:
    ensure_output_dirs(config)
    data = load_current_sbti(config)
    write_load_diagnostics(config, data)
    build_dictionary_crosswalk(config, data)

    company_overlay = build_company_overlay(config, data.company)
    target_rows = normalize_target_rows(config, data.target)
    target_overlay = aggregate_target_overlay(config, target_rows)
    sector_flags = build_sector_flags(config, company_overlay, target_rows, target_overlay)
    final_overlay = build_final_overlay(config, company_overlay, target_overlay, sector_flags)
    match_summary = write_overlay_vs_legacy_diagnostics(config, final_overlay)
    write_data_quality_report(
        config,
        data.company,
        len(data.target) + data.blank_target_rows_dropped,
        data.blank_target_rows_dropped,
        target_rows,
        final_overlay,
    )
    write_overlay_summary(config, final_overlay, match_summary)
    return {
        "overlay_csv": str(config.output_dir / "current_sbti_firm_overlay.csv"),
        "overlay_parquet": str(config.output_dir / "current_sbti_firm_overlay.parquet"),
        "summary": str(config.output_dir / "current_overlay_summary.md"),
    }
