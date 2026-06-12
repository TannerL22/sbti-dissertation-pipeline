# Pipeline Modes

| Mode | Purpose | Command | Inputs | Outputs | Should it change results? |
|---|---|---|---|---|---|
| Legacy reproduction | Preserve dissertation-era behavior. | `python run_pipeline.py legacy` | Legacy scripts, canonical panel, stored outputs. | `outputs/legacy_reproduction/` | No. |
| Refactored legacy | Modular reproduction of legacy results. | `python run_pipeline.py refactored-legacy` | Canonical panel, legacy config. | `outputs/refactored_legacy/` | No. |
| Refactored clean | Statistical diagnostics and cleaned event-study design. | `python run_pipeline.py refactored-clean` | Canonical panel. | `outputs/refactored_clean/` | Only diagnostic results may differ. |
| Current overlay | Build current SBTi metadata overlay. | `python run_pipeline.py current-overlay` | Frozen May 2026 SBTi files. | `outputs/current_sbti_overlay/` | No historical results change. |
| Methodology robustness | Test sensitivity to current metadata flags. | `python run_pipeline.py methodology-robustness` | Canonical panel + current overlay. | `outputs/methodology_robustness/` | Robustness only. |
| Methodology robustness 4B | Target public/private and leverage conclusions. | `python run_pipeline.py methodology-robustness-4b` | Canonical panel + current overlay. | `outputs/methodology_robustness_4b/` | Robustness only. |
| Final synthesis | Decision-ready dissertation update package. | `python run_pipeline.py final-synthesis` | Prior phase outputs. | `outputs/final_synthesis/` | No. |
| Tests | Validate guardrails. | `python run_pipeline.py test` | Test files and generated outputs. | Test report in console. | No. |

## Canonical Outputs

Legacy and refactored legacy outputs are the benchmark for dissertation reproduction. Refactored-clean, overlay, robustness, and Phase 4B outputs are diagnostic or robustness layers.

## Diagnostic-Only Outputs

Current overlay preview panels and output manifests are not modeling panels. They are for inspection and reproducibility only.
