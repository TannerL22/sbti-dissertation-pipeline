# Pipeline Improvement Summary

## What Was Improved

The project now has a staged, non-destructive analysis architecture:

- legacy reproduction with frozen inputs and documented quirks;
- refactored legacy reproduction preserving dissertation behavior;
- refactored-clean statistical diagnostics;
- current SBTi metadata overlay;
- methodology-aware robustness checks;
- targeted Public-Private Chasm and Leverage Trap robustness;
- final synthesis outputs.

The pipeline no longer relies only on ad hoc scripts. It now has configs, runners, diagnostics, output separation, and tests.

## Tests Added

Tests now cover:

- legacy event construction;
- legacy ambition;
- legacy Scope 3;
- filtering and winsorization behavior;
- no-lookahead overlay guardrails;
- refactored legacy reproduction checks;
- clean event-study bins and pre-trend outputs;
- centered leverage;
- current SBTi loader and Scope 3 taxonomy;
- current sector flags;
- methodology robustness panel/specs/outputs;
- Phase 4B public/private and leverage robustness.

Latest test command:

```bash
python -m pytest tests
```

Latest result during Phase 4B: `69 passed`.

## Pipeline Modes

| Mode | Purpose |
|---|---|
| Legacy reproduction | Reproduce the original dissertation outputs and preserve quirks. |
| Refactored legacy | Modular version of legacy behavior with deterministic compatibility rules. |
| Refactored clean | Statistical diagnostics with clean event-study bins, pre-trends, and centered leverage. |
| Current SBTi overlay | Current May 2026 metadata overlay for flags and caveats. |
| Methodology robustness | Robustness checks using current metadata as sample flags only. |
| Phase 4B robustness | Targeted checks for Public-Private Chasm and Leverage Trap. |

## Before External Use

Before using the project externally:

- add a top-level README explaining the modes and data restrictions;
- decide which generated outputs should remain committed versus archived;
- add dependency metadata in `pyproject.toml`;
- document data provenance and access constraints;
- review any large output files for repository policy;
- clearly label all current SBTi overlay outputs as current metadata.
