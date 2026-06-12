# Data Availability And Limits

This repository does not include the raw financial data used in the dissertation pipeline.

## Not Included

- Compustat financial extracts.
- Orbis financial extracts.
- The canonical analytical panel `data/derived/final_analytical_panel_v3.parquet`.
- Raw/interim/processed data files.
- Full generated regression output directories.
- Root-level SBTi Excel downloads.

These files are omitted because they may be licensed, large, or not appropriate for public redistribution.

## Included

The repository includes:

- Pipeline source code.
- Configuration files.
- Documentation.
- Methodology guardrails.
- Final synthesis memos.
- Lightweight comparison/conclusion summaries.

## What The Results Measure

The historical analysis measures within-firm financial changes among SBTi adopters around first near-term target validation, conditional on firm fixed effects, year fixed effects, controls, and firm-clustered standard errors.

It is not a canonical untreated-control difference-in-differences design.

## SBTi Metadata Caveat

The current SBTi overlay is May 2026 dashboard metadata. It is used for robustness flags and interpretation only. It does not redefine historical validation dates, commitment dates, ambition variables, or the legacy Scope 3 definition.

## Reproducing The Full Results

To reproduce the full empirical outputs, a user needs access to the omitted financial data and the frozen SBTi inputs described in the configs and documentation.
