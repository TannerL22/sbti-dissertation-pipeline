# Methodology Robustness

Phase 4 uses the May 2026 current SBTi metadata overlay as a robustness layer on the existing 2012-2024 financial panel.

It does not change the legacy treatment timing, event definitions, ambition definitions, Scope 3 definitions, winsorization, filters, or raw data. Current metadata is used only for sample flags, sensitivity filters, and caveat analysis.

## Robustness Groups

The sector and rule-regime checks use current overlay flags for:

- financial institutions;
- FLAG-relevant firms;
- automotive firms;
- oil and gas firms;
- the combined standard-sensitive group.

These are robustness exclusions or sub-samples. They are not silent baseline changes.

## Scope 3

The dissertation Scope 3 variable remains the strict historical definition: standalone `scope == 3` and `type == Absolute`.

Phase 4 compares that variable with current metadata categories such as any target including Scope 3, current legacy-like absolute Scope 3, intensity Scope 3, engagement Scope 3, and no-deforestation Scope 3.

Current Scope 3 taxonomy results should be described as current metadata robustness, not event-time causal evidence.

## Current Status Caveats

Current near-term and net-zero statuses can post-date the dissertation event. They are used only for caveat and sensitivity scenarios, not as treatment-timing inputs.

## Interpretation

If coefficients change, Phase 4 classifies the likely reason as sample composition, sector-standard sensitivity, current-status caveat, Scope 3 taxonomy, statistical specification, or unresolved difference.

Phase 5 can synthesize these results into dissertation interpretation updates.
