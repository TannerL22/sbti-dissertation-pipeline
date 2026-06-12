# Refactored-Clean Statistical Mode

Phase 2B adds a statistical robustness layer separate from legacy reproduction.

## What It Does

Run command:

```bash
python run_refactored_clean.py --config configs/refactored_clean_2012_2024.yaml
```

Outputs are written only to `outputs/refactored_clean/`.

The clean mode adds:

- Mutually exclusive event-study bins.
- Omitted reference period `t = -1`.
- Joint Wald pre-trend tests.
- Event-study plots with confidence intervals.
- Model registry and attrition diagnostics.
- Full-spec event-study as clean default.
- No-size diagnostic comparisons for `revenue_growth_winsorized` and `log_revt`.
- Centered leverage robustness for nonlinear leverage interpretation.

## What It Does Not Do

- It does not replace the dissertation results.
- It does not modify legacy compatibility mode.
- It does not correct or overwrite legacy outputs.
- It does not merge current SBTi metadata.
- It does not use post-2025 target statuses or policy changes.
- It does not change event definitions, ambition definitions, Scope 3 definitions, winsorization, filtering, or public/private classification.

## Clean Event-Study Design

Legacy event-study output used overlapping event dummies, including broad `post_event` together with `post1`, `post2`, and `post3plus`.

Clean mode instead creates `rel_year = fyear - event_year` and uses mutually exclusive bins:

- `rel_year <= -3`
- `rel_year == -2`
- omitted `rel_year == -1`
- `rel_year == 0`
- `rel_year == 1`
- `rel_year == 2`
- `rel_year >= 3`

The omitted reference period is `t = -1`. The clean model does not include broad `post_event`.

## Revenue Growth And Log Revenue

The legacy dissertation-facing event-study table used no-`size_log_assets` fallback models for:

- `revenue_growth_winsorized`
- `log_revt`

Clean mode runs the full specification where it estimates successfully and separately records no-size diagnostics for those two variables. Differences in these DVs should be classified as a mix of event-study dummy correction and full-spec vs no-size model choice, not as automatic changes in dissertation conclusions.

## Pre-Trend Tests

Clean mode tests the included pre-period bins jointly:

- `rel_year <= -3`
- `rel_year == -2`

Classification:

- `p >= 0.10`: no strong pre-trend evidence
- `0.05 <= p < 0.10`: weak/preliminary pre-trend concern
- `p < 0.05`: material pre-trend concern

These tests are diagnostics. They should guide robustness interpretation, not silently reclassify historical results.

## Centered Leverage Robustness

Centered leverage is defined within each model estimation sample after model-specific filtering:

```text
leverage_centered = leverage_winsorized - mean(leverage_winsorized)
leverage_centered_sq = leverage_centered ** 2
```

This makes `post_event` interpretable as the post-validation effect at average leverage in that model sample. The interaction terms describe how the post-event effect changes above or below average leverage.

These centered models do not replace the dissertation's uncentered leverage-trap results.

## Remaining Future Phases

- Updated SBTi metadata overlay.
- Finance-sector robustness.
- FLAG, automotive, and oil/gas flags.
- Richer Scope 3 taxonomy.
- Global post-merge winsorization robustness if desired.
- True non-SBTi control group if new financial data becomes available.
