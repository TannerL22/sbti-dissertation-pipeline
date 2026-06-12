# Refactored Legacy Pipeline

Phase 2A adds a modular legacy pipeline while preserving dissertation-facing behavior.

## Run Command

```bash
python run_refactored_legacy.py --config configs/legacy_2012_2024.yaml
```

Outputs are written to `outputs/refactored_legacy/`.

## Structure

- `configs/legacy_2012_2024.yaml`: canonical panel path, output path, dependent variables, controls, fixed effects, clustering, and legacy compatibility notes.
- `src/sbti_pipeline/model_runner.py`: shared listwise deletion, constant-DV removal, singleton removal, clustered OLS fitting, and model registry helpers.
- `src/sbti_pipeline/legacy_main.py`: refactored main fixed-effects models.
- `src/sbti_pipeline/legacy_event_study.py`: refactored dissertation-facing event-study compatibility mode.
- `src/sbti_pipeline/legacy_predictive.py`: refactored predictive logit model preserving the legacy success definition.
- `src/sbti_pipeline/comparison.py`: writes the refactored-vs-legacy comparison report.

## Intentionally Preserved

- Canonical panel: `data/derived/final_analytical_panel_v3.parquet`.
- Main event definition: first validated near-term target.
- Commitment and validation timing as already embedded in the canonical panel.
- Legacy Scope 3 definition: standalone `scope == 3` and `type == Absolute`.
- Source-specific winsorization already embedded in the canonical panel.
- Public/private classification from the legacy final panel.
- Legacy filtering: model-specific listwise deletion, constant-DV firm removal, singleton removal.
- Firm and year fixed effects.
- Firm-clustered standard errors.
- Overlapping event-study dummy structure.

## Event-Study Compatibility Mode

The original event-study script had environment-dependent fallback behavior. The stored dissertation-facing table used no-`size_log_assets` fallback models for:

- `revenue_growth_winsorized`
- `log_revt`

Phase 2A makes this deterministic through `legacy_event_study_compatibility_mode`.

The legacy compatibility event-study uses:

- Full size-controlled models for `roa_winsorized`, `op_margin_winsorized`, `log_ebitda`, and `log_emp`.
- No-size fallback models for `revenue_growth_winsorized` and `log_revt`.

This preserves the dissertation-facing result. It does not endorse the fallback as the preferred clean specification.

## Not Fixed Yet

- Event-study bins are not corrected to mutually exclusive event-time bins.
- Current SBTi files are not merged into the historical panel.
- Finance, FLAG, automotive, and oil/gas flags are not implemented.
- Global post-merge winsorization is not implemented.
- Sector-adjusted predictive success is not used.
- Duplicate `gvkey`-`fyear` rows are preserved.

## Mode Distinctions

`legacy_exact` means the old scripts and stored outputs.

`refactored_legacy` means modular code that reproduces the same dissertation-facing behavior, including documented quirks and compatibility choices.

`refactored_clean` is a future mode that can correct event-study bins, make fallback specifications explicit robustness choices, improve duplicate handling, and add broader diagnostics without replacing the legacy benchmark.
