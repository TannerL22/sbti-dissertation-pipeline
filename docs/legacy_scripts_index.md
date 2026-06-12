# Legacy Scripts Index

The `scripts/` folder is preserved for provenance. Do not delete these files without a separate archival decision.

## Data Preparation

Scripts under `scripts/01_data_preparation/` are legacy data-building scripts. They are superseded for most current work by the canonical panel `data/derived/final_analytical_panel_v3.parquet`, but remain important for tracing original transformations.

## Analysis

| Script group | Status |
|---|---|
| `02_main_fixed_effects_with_placebo.py` | Canonical legacy main regression script. |
| `03_commitment_date_robustness.py` | Preserved legacy commitment-date robustness. |
| `08_dynamic_event_study_tables.py` | Preserved legacy event-study script; refactored legacy encodes compatibility fallback. |
| `11_predictive_logit_final.py` | Preserved legacy predictive model script. |
| Other `scripts/02_analysis/` files | Preserved legacy robustness/appendix scripts; many are superseded by refactored modes for new work. |

## Figures

Scripts under `scripts/03_figures/` are preserved for reproducing or inspecting dissertation-era visuals. New synthesis figures are under `outputs/final_synthesis/figures/`.

## Diagnostics

Scripts under `scripts/04_diagnostics/` are legacy exploratory diagnostics. Active validation now lives in `validate_project.py` and tests.

## Recommendation

Keep all legacy scripts. Add new work under `src/sbti_pipeline/` and new runner/config pairs.
