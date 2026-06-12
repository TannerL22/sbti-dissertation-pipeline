# Refactored Legacy Comparison

## Verdict

The refactored legacy pipeline preserves the key dissertation-facing behavior for the canonical panel, main fixed-effects models, predictive logit model Ns, and event-study compatibility specifications.

The main and predictive text files are not byte-for-byte copies because the refactored pipeline writes clearly labeled refactored headers and diagnostics. Golden checks compare the substantive values.

## Output Locations

- Tables: `C:/Users/tanne/Desktop/Dissertation/outputs/refactored_legacy/tables`
- Diagnostics: `C:/Users/tanne/Desktop/Dissertation/outputs/refactored_legacy/diagnostics`
- Comparisons: `C:/Users/tanne/Desktop/Dissertation/outputs/refactored_legacy/comparisons`

## Panel Checks

| Check | Expected | Refactored | Status |
|---|---:|---:|---|
| Final panel rows | 59,496 | 59,496 | match |
| Adopter firm-years | 32,484 | 32,484 | match |
| Duplicate non-null `gvkey`-`fyear` groups | 13 | 13 | match |

## Main Regression Golden Checks

| Dependent variable | Model | N | `post_event` | `post_event_x_s1s2_rate` |
|---|---|---:|---:|---:|
| `roa_winsorized` | Model 1 | 23,141 | -0.006 | 0.000 |
| `op_margin_winsorized` | Model 1 | 22,550 | -0.034 | 0.006 |
| `revenue_growth_winsorized` | Model 1 | 21,008 | -0.003 | 0.001 |
| `tobins_q_winsorized` | Model 1 | 15,626 | 0.024 | -0.006 |
| `log_revt` | Model 1 | 23,100 | -0.045 | 0.004 |
| `log_ebitda` | Model 1 | 20,690 | -0.111 | 0.010 |
| `log_emp` | Model 1 | 20,039 | 0.017 | -0.004 |

## Event-Study Compatibility

Legacy compatibility mode is applied: `revenue_growth_winsorized` and `log_revt` use the no-size fallback; the other event-study DVs use the full size-controlled specification.

| Dependent variable | Selected spec | N | `post_event` | `size_log_assets` selected? |
|---|---|---:|---:|---|
| `roa_winsorized` | `legacy_event_study_full` | 25,487 | -0.0036 | True |
| `op_margin_winsorized` | `legacy_event_study_full` | 24,831 | 0.0003 | True |
| `revenue_growth_winsorized` | `legacy_event_study_no_size_fallback` | 23,155 | 0.0020 | False |
| `log_ebitda` | `legacy_event_study_full` | 22,835 | -0.0321 | True |
| `log_revt` | `legacy_event_study_no_size_fallback` | 25,437 | -0.0502 | False |
| `log_emp` | `legacy_event_study_full` | 22,090 | 0.0045 | True |

## Predictive Logit

| Outcome | N | Pseudo R2 |
|---|---:|---:|
| `Positive_ROA_Outcome` | 1,477 | 0.011 |
| `Positive_OP_MARGIN_Outcome` | 1,447 | 0.024 |
| `Positive_REVENUE_GROWTH_Outcome` | 1,744 | 0.035 |
| `Positive_TOBINS_Q_Outcome` | 1,022 | 0.031 |

Predictive output checksum comparison:

- Stored SHA-256: `22d028c90ef83fabdce77e75202629486d7a56d7ad15fb43328d3d07019a5b15`
- Refactored SHA-256: `a98f5f86e61fb392bae279f6f106552165fd9e0dc9d872426285a92871b523bd`
- Expected: not byte-identical because the refactored file has a different header, but model Ns and values are checked in tests.

## Remaining Differences

- Formatting and file headers differ from legacy scripts.
- Event-study overlapping dummies are intentionally preserved, not corrected.
- Current SBTi metadata is not merged.
- The no-size event-study fallback is now deterministic for legacy compatibility instead of environment-dependent.

## Phase 2B Readiness

It is safe to proceed to Phase 2B after reviewing this report. Phase 2B should build clean/robustness modes without overwriting the legacy compatibility outputs.
