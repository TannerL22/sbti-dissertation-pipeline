# Refactored-Clean vs Legacy Diagnostic Comparison

This report compares robustness diagnostics against the legacy/refactored-legacy benchmark. It does not reinterpret dissertation conclusions as new causal findings.

## Event-Study Comparison

Clean mode uses mutually exclusive bins with `t = -1` omitted and excludes the broad `post_event` dummy. Legacy mode used overlapping event-study dummies and, for revenue growth/log revenue, a no-size fallback.

| DV | Legacy post/event coefficient | Clean t=0 coefficient | Clean p-value | Classification |
|---|---:|---:|---:|---|
| `roa_winsorized` | -0.0036 | -0.0030 | 0.1354 | unchanged |
| `op_margin_winsorized` | 0.0003 | 0.0005 | 0.8835 | unchanged |
| `revenue_growth_winsorized` | 0.0020 | 0.0020 | 0.8791 | unchanged |
| `log_revt` | -0.0502 | -0.0070 | 0.4892 | directionally unchanged but magnitude differs |
| `log_ebitda` | -0.0321 | -0.0348 | 0.0669 | significance changed |
| `log_emp` | 0.0045 | 0.0009 | 0.9345 | unchanged |

## Pretrend Summary

| DV | p-value | Classification |
|---|---:|---|
| `roa_winsorized` | 0.5235 | no strong pre-trend evidence |
| `op_margin_winsorized` | 0.2406 | no strong pre-trend evidence |
| `revenue_growth_winsorized` | 0.8298 | no strong pre-trend evidence |
| `log_revt` | 0.4470 | no strong pre-trend evidence |
| `log_ebitda` | 0.7583 | no strong pre-trend evidence |
| `log_emp` | 0.0013 | material pre-trend concern |

## Centered Leverage Robustness

Centered leverage models completed as interpretability diagnostics. `post_event` is now the post-validation effect at average model-sample leverage. These models do not replace the uncentered dissertation leverage-trap estimates.

| DV | Sample | Post x centered leverage | Post x centered leverage sq | Classification |
|---|---|---:|---:|---|
| `roa_winsorized` | full | -0.0201 | 0.0775 | significance changed or robustness signal present |
| `roa_winsorized` | public | -0.0196 | 0.0769 | significance changed or robustness signal present |
| `roa_winsorized` | private | 0.0338 | 0.0911 | not materially changed |
| `op_margin_winsorized` | full | -0.0142 | 0.2447 | significance changed or robustness signal present |
| `op_margin_winsorized` | public | -0.0458 | 0.1583 | significance changed or robustness signal present |
| `op_margin_winsorized` | private | 0.1320 | 0.2786 | significance changed or robustness signal present |
| `tobins_q_winsorized` | full | -0.0642 | 0.3922 | not materially changed |
| `tobins_q_winsorized` | public | -0.0642 | 0.3922 | not materially changed |

## Finding-Level Interpretation Guardrails

- Two-stage signaling vs implementation-cost narrative: clean event-study is a timing diagnostic only; it does not change the legacy pre/post main model.
- Ambition shield: not re-estimated as a new headline claim in Phase 2B.
- Public/private chasm: not changed in Phase 2B.
- Leverage trap: centered leverage improves interpretation around average leverage but does not replace uncentered legacy estimates.
- Market indifference: not changed in Phase 2B.
- Temporal dynamics / implementation dip: clean bins isolate event-time periods better than legacy overlapping dummies.
- Scale shock in `log_revt`: clean full-spec differs from legacy no-size fallback; classify this as full-spec vs no-size model choice plus event-study dummy correction.
- Revenue growth effects: clean full-spec differs from legacy fallback; treat as robustness sensitivity, not a new causal conclusion.

## Phase 3 Readiness

It is safe to proceed to Phase 3 updated SBTi overlay after reviewing the event-study and pretrend diagnostics. Phase 3 should remain separate from both legacy and clean statistical modes.
