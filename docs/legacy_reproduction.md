# Legacy Reproduction Mode

This document defines the safe Phase 1 reproduction baseline. It preserves the dissertation-era methodology and legacy quirks before any refactor or methodological correction.

## Canonical Legacy Inputs

- Canonical final panel: `data/derived/final_analytical_panel_v3.parquet`
- Canonical main regression script: `scripts/02_analysis/02_main_fixed_effects_with_placebo.py`
- Canonical stored legacy output folder: `data/analysis/`
- Safe reproduction output folder: `outputs/legacy_reproduction/`
- Current SBTi metadata snapshot: `data/raw/current_sbti/`

## Commands

Non-destructive stored-output snapshot:

```bash
python run_legacy_reproduction.py
```

Fresh legacy-script execution for the core reproduction scripts:

```bash
python run_legacy_reproduction.py --execute --scripts core
```

Fresh legacy-script execution for the broader analysis scripts:

```bash
python run_legacy_reproduction.py --execute --scripts all --continue-on-error
```

The default command does not execute legacy scripts. It copies currently stored outputs into `outputs/legacy_reproduction/` so Phase 1 can establish a safe baseline without overwriting `data/analysis`.

## Expected Outputs

- Logs: `outputs/legacy_reproduction/logs/`
- Copied tables/text outputs: `outputs/legacy_reproduction/tables/`
- Copied figures: `outputs/legacy_reproduction/figures/`
- Diagnostics: `outputs/legacy_reproduction/diagnostics/`
- Run summary: `outputs/legacy_reproduction/legacy_reproduction_summary.md`

## Preserved Legacy Quirks

These are intentionally preserved in `legacy_exact` mode:

- Duplicated non-null `gvkey`-`fyear` rows remain in the canonical panel.
- Unmatched public rows with missing `sbti_id` metadata are removed from adopter regressions through the legacy model sample construction.
- The event-study dummy design is overlapping: `post_event` coexists with `post1`, `post2`, and `post3plus`.
- Winsorization remains source-specific at 1/99 where legacy scripts perform public/private cleaning separately.
- Legacy Scope 3 is exactly standalone `scope == 3` and `type == Absolute`.
- The empirical design is a within-adopter fixed-effects design; it does not include a non-SBTi untreated control group.
- Commitment-date robustness remains the original simple post-commitment specification.
- The predictive success definition remains post-average greater than pre-average.

## Mode Boundaries

`legacy_exact` reproduces the dissertation-style outputs as closely as possible. It preserves duplicate rows, overlapping event-study dummies, legacy filtering, legacy winsorization, and legacy Scope 3 treatment.

`refactored_clean` will later improve code structure and diagnostics while keeping the historical design visible. It may correct duplicates and event-study bins only after legacy reproduction is benchmarked.

`updated_sbti_overlay` will later enrich the same financial panel with current SBTi metadata. It must not treat current statuses as historical event-time facts unless timing is reconstructed.

`robustness` will later add finance-sector, FLAG, automotive, oil and gas, global winsorization, richer Scope 3, and corrected event-study checks without replacing the legacy baseline.
