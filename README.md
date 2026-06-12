# The Financial Impact of Science-Based Climate Targets

This repository contains the analysis pipeline for an MSc dissertation on the financial impact of Science Based Targets initiative (SBTi) commitment and validation among public and private firms.

## Research Question

Does official validation of a science-based climate target affect firm financial performance, and do target ambition, ownership status, leverage, Scope 3 coverage, sector, and current SBTi rule-regime classifications shape that relationship?

The historical empirical panel covers 2012-2024. The current SBTi files are May 2026 metadata overlays and are not used to redefine historical treatment timing.

## Pipeline Modes

| Mode | Purpose | Command |
|---|---|---|
| Legacy reproduction | Preserve and reproduce dissertation-era outputs and quirks. | `python run_pipeline.py legacy` |
| Refactored legacy | Reproduce legacy behavior with modular code and compatibility rules. | `python run_pipeline.py refactored-legacy` |
| Refactored clean | Add clean event-study bins, pre-trends, attrition logs, and centered leverage diagnostics. | `python run_pipeline.py refactored-clean` |
| Current SBTi overlay | Build May 2026 current metadata overlay from frozen SBTi by-company/by-target files. | `python run_pipeline.py current-overlay` |
| Methodology robustness | Run overlay-aware finance/FLAG/auto/oil-gas/Scope 3/status robustness checks. | `python run_pipeline.py methodology-robustness` |
| Phase 4B robustness | Target Public-Private Chasm and Leverage Trap robustness. | `python run_pipeline.py methodology-robustness-4b` |
| Final synthesis | Use generated Phase 5 memos and conclusion matrices. | `python run_pipeline.py final-synthesis` |

## Quickstart

This clean GitHub package is intended to make the pipeline, assumptions, and statistical interpretation readable. It does not include the licensed/raw financial data needed to rerun the full empirical analysis.

Create an environment and install dependencies:

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
```

Run tests after restoring the required local data and generated benchmark artifacts:

```bash
python run_pipeline.py test
```

Validate the project:

```bash
python validate_project.py
```

## Data Requirements

Required local files:

- `data/derived/final_analytical_panel_v3.parquet`
- `data/raw/current_sbti/targets-excel.xlsx`
- `data/raw/current_sbti/companies-excel(2).xlsx`
- `data/raw/current_sbti/Alpha-Dashboard-Data-Dictionary(3).xlsx`

The repository assumes raw data are immutable. Do not overwrite raw files.

Without these files, the code and documentation can be reviewed, but the full regression pipeline and guardrail tests cannot be rerun end to end. See `DATA_AVAILABILITY.md` for what is intentionally excluded.

## SBTi Caveats

- Current SBTi metadata is May 2026 dashboard state, not historical event-time data.
- Post-2025 SBTi rules are not retroactively applied to 2012-2024 financial results.
- The legacy Scope 3 variable is narrow: standalone `scope == 3` and `type == Absolute`.
- Finance, FLAG, automotive, oil/gas, and current-status fields are robustness/caveat classifications, not baseline exclusions.

## Reproducibility Notes

Each phase writes to its own output folder. Legacy, refactored legacy, clean, overlay, robustness, 4B, and synthesis outputs are not overwritten by later modes.

The design should be described as a within-adopter firm/year fixed-effects and event-study pipeline, not a canonical untreated-control DiD.

## Key Outputs

- Legacy reproduction: `outputs/legacy_reproduction/`
- Refactored legacy: `outputs/refactored_legacy/`
- Refactored clean: `outputs/refactored_clean/`
- Current overlay: `outputs/current_sbti_overlay/`
- Methodology robustness: `outputs/methodology_robustness/`
- Phase 4B robustness: `outputs/methodology_robustness_4b/`
- Final synthesis: `outputs/final_synthesis/`
- Results index: `outputs/results_index.md`
- Output manifest: `outputs/output_manifest.csv`

## Limitations

The project has no true non-SBTi untreated control group, no post-2024 financial outcomes, no historical SBTi dashboard snapshots after the original pull, and some event-study findings are specification-sensitive. Current metadata should be used for robustness and caveats only.

## Repository Status

The project is packaged for local reproducibility and dissertation revision support. Before external release, review data licensing, large generated outputs, and any raw-data sharing restrictions.
