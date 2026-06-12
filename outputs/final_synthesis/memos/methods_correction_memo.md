# Methods Correction Memo

## Core Correction

The dissertation design is best described as a within-adopter firm and year fixed-effects design with event-study diagnostics. It should not be described as a canonical difference-in-differences design unless a true untreated or not-yet-treated comparison group is explicitly constructed.

## Why This Matters

A canonical DiD design compares treated firms with comparable untreated firms and relies on a parallel-trends assumption between those groups. The dissertation's main empirical strategy instead compares firms to themselves before and after SBTi commitment or validation, while absorbing time-invariant firm traits and common year shocks. This is still useful and defensible for the research question, but it supports narrower causal language.

## Recommended Causal Phrasing

Use:

- "is associated with";
- "is consistent with";
- "within-firm changes following validation";
- "conditional on firm and year fixed effects";
- "event-time evidence."

Avoid:

- "proves";
- "causes" without qualification;
- "canonical DiD";
- "relative to untreated firms" unless a control group is added.

## Future True DiD Design

A future true DiD or matched-control design would require:

- a sample of comparable non-SBTi firms;
- pre-treatment financial data for both groups;
- matching or weighting on sector, geography, size, leverage, growth, and pre-trends;
- explicit treatment timing for SBTi adopters;
- tests for parallel pre-trends;
- robustness to staggered-adoption estimator choices.

## Event-Study Fallback Issue

The legacy dissertation-facing event-study table used a no-`size_log_assets` fallback for `revenue_growth_winsorized` and `log_revt`. The fresh rerun in the current environment estimated the full specification, causing differences. The refactored legacy pipeline now encodes the fallback explicitly for reproduction.

The dissertation should document this as a legacy compatibility feature. It should not silently present the full-spec estimates as the original dissertation result.

## Refactored-Clean Event Study

The refactored-clean event-study uses mutually exclusive bins with `t = -1` omitted and excludes the broad `post_event` dummy. This design is cleaner for timing interpretation. It weakens some dynamic claims, especially the log-revenue scale shock, and flags a material pre-trend concern for `log_emp`.

Recommendation: keep the legacy event-study as reproduction evidence, but use the clean event-study as the preferred robustness diagnostic for dynamic timing.
