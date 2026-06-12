# Publishing Notes

This is the clean GitHub publication package for the dissertation pipeline.

The package is intentionally not identical to the full local working repository. It excludes raw data, bulky generated outputs, local backups, and legacy figure artifacts. It preserves the parts needed for a reader to understand the pipeline and evaluate the statistical design:

- active source code in `src/sbti_pipeline/`;
- configs in `configs/`;
- runners;
- methodology documentation;
- final synthesis and conclusion summaries;
- tests as guardrails, subject to local data availability.

Recommended repository visibility: private unless you are certain all included summaries and dissertation text excerpts are safe to share.

Before making public, review:

- whether final synthesis memos include any dissertation text you do not want public;
- whether the results summaries should be public;
- whether your institution or data providers restrict derived outputs.
