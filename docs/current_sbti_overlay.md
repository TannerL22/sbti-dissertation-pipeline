# Current SBTi Overlay

Phase 3 builds a current metadata overlay from the frozen May 2026 SBTi files in `data/raw/current_sbti/`.

This overlay is not a new treatment construction. It does not change historical commitment dates, validation dates, post-event indicators, ambition variables, winsorization, filtering, or the legacy Scope 3 definition.

## Source Grain

The by-company workbook is current company-level dashboard state: one row per current dashboard company. It is used for current organization type, sector, geography, target-status fields, net-zero fields, and dashboard coverage.

The by-target workbook is target/commitment-level current tracker data. `action == Target` identifies target rows. `action == Commitment` identifies commitment rows. The `status` field is mainly meaningful for commitment rows, so `status == Target set` is not used to identify target rows.

The data dictionary is used as documentation and a crosswalk. Ambiguous fields are documented instead of guessed into historical methodology.

## Safe Uses

Safe Phase 4 uses include robustness flags and stratification based on current metadata:

- financial institution flag;
- FLAG-relevant sector and observed target proxies;
- automotive sector and observed pathway proxies;
- oil and gas, power/utilities, chemicals, buildings/real estate, and high-Scope-3 sector proxies;
- current near-term, long-term, and net-zero dashboard status;
- richer current Scope 3 target taxonomy.

These fields must be described as current metadata overlays.

## Caution

Current target statuses are not historical event-time statuses. A target that is currently removed, expired, extended, or updated may not have had that status when the dissertation event occurred.

Post-2025 SBTi policy changes are not retroactively applied to old targets. Current `date_published` fields are retained for context but do not overwrite dissertation validation dates.

## Scope 3 Taxonomy

The legacy variable remains strict: standalone `scope == 3` and `type == Absolute`.

The overlay adds broader current metadata fields:

- any target including Scope 3;
- absolute target including Scope 3;
- intensity target including Scope 3;
- engagement target including Scope 3;
- no-deforestation target including Scope 3;
- observed Scope 3 target types and target-type count.

Combined `1+2+3` targets count as including Scope 3 but do not count as legacy-like standalone absolute Scope 3 unless a standalone `scope == 3`, `type == Absolute` row also exists.

## Outputs

Run:

```bash
python run_current_sbti_overlay.py --config configs/current_sbti_overlay.yaml
```

Main outputs:

- `outputs/current_sbti_overlay/current_sbti_firm_overlay.csv`
- `outputs/current_sbti_overlay/current_sbti_firm_overlay.parquet`
- `outputs/current_sbti_overlay/tables/current_company_overlay.csv`
- `outputs/current_sbti_overlay/tables/current_target_rows_normalized.csv`
- `outputs/current_sbti_overlay/tables/current_target_firm_overlay.csv`
- `outputs/current_sbti_overlay/tables/current_sector_flags.csv`
- `outputs/current_sbti_overlay/comparisons/current_overlay_vs_legacy_panel.md`
- `outputs/current_sbti_overlay/diagnostics/current_overlay_data_quality_report.md`

## Future Phase 4

Phase 4 can use this overlay to run robustness checks excluding or flagging financial institutions, FLAG-relevant firms, automotive firms, oil and gas firms, and richer Scope 3 categories.

Those checks should remain separate from legacy reproduction and should not be presented as automatic replacements for the dissertation results.
