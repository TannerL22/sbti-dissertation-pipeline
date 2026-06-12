# Developer Guide

## Project Structure

- `configs/`: YAML configs for pipeline modes.
- `src/sbti_pipeline/`: active refactored Python modules.
- `scripts/`: original legacy scripts, preserved for provenance.
- `run_*.py`: mode-specific runners.
- `run_pipeline.py`: convenience command registry.
- `tests/`: guardrail tests.
- `outputs/`: generated outputs by mode.

## Configs

Configs are loaded through `src/sbti_pipeline/config.py`. Paths are relative to the repository root. Do not hard-code output paths inside model code when a config field exists.

## Runners

Mode-specific runners call the relevant module:

- `run_refactored_legacy.py`
- `run_refactored_clean.py`
- `run_current_sbti_overlay.py`
- `run_methodology_robustness.py`
- `run_methodology_robustness_4b.py`

Use `run_pipeline.py` for a single entry point.

## Outputs

Every mode must write to its own output folder. Do not write new robustness outputs into legacy folders.

## Adding A Robustness Scenario

1. Add the scenario to the relevant YAML config.
2. Use current overlay fields only as current metadata flags.
3. Do not redefine `post_event`, `event_year`, ambition, Scope 3, winsorization, or filtering.
4. Add a test that confirms sample size decreases or remains bounded relative to the parent scenario.

## Adding A Dependent Variable

1. Confirm the variable exists in `data/derived/final_analytical_panel_v3.parquet`.
2. Add it to the relevant config.
3. Check missingness and model attrition.
4. Update tests if the output shape is expected to change.

## Adding A Current SBTi Overlay Flag

1. Add row-level logic in `current_target_overlay.py` or firm-level logic in `current_sector_flags.py`.
2. Prefix the new field with `current_`.
3. Document whether it is sector proxy, observed target proxy, or current status.
4. Add no-lookahead tests if the field could be confused with historical treatment.

## Tests

Tests protect legacy behavior, clean event-study rules, overlay guardrails, robustness outputs, and final packaging. Run:

```bash
python -m pytest tests
```

## Do Not Break Legacy Outputs

Never edit legacy methodology silently. If a new method is needed, add it as a new mode or optional scenario and label it clearly.
