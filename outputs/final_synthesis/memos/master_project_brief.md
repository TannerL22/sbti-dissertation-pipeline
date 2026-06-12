# Master Project Brief

## 1. One-Page Executive Summary

This project rebuilt, audited, and extended the dissertation pipeline for *The Financial Impact of Science-Based Climate Targets: A Comparative Analysis of Public and Private Firms*. The goal was not to rewrite the dissertation or change the historical empirical design, but to determine whether the original findings survive a reproducibility audit, cleaner statistical diagnostics, and the updated SBTi standards/data environment.

The central answer is: **yes, the main dissertation story survives, but it needs sharper caveats.** The strongest surviving conclusions are the two-stage commitment-versus-validation narrative, the post-validation operational performance dip, the Ambition Shield, the Public-Private Chasm, the Leverage Trap, and average Market Indifference. The conclusions that need the most careful wording are the Scope 3 Puzzle, the exact timing of the implementation dip, the sustained log-revenue scale shock, and employment dynamics.

The original empirical results remain best understood as historical evidence for firms validated under the SBTi regime that governed the 2012-2024 financial panel. Updated SBTi changes after mid-2025 do not retroactively invalidate those results. They do, however, change how the results should be interpreted going forward: finance firms, FLAG-relevant firms, automotive firms, oil and gas firms, Scope 3 target types, target statuses, and revalidation cycles now need more explicit classification and robustness treatment.

The codebase is now much more defensible. It has frozen input snapshots, legacy reproduction guardrails, a refactored legacy pipeline, a refactored-clean statistical mode, a current SBTi metadata overlay, methodology-aware robustness checks, targeted Public-Private Chasm and Leverage Trap robustness, and final synthesis memos. Tests protect the fragile methodological choices so future changes do not silently alter legacy behavior.

The most important methodological correction is wording: the design should be described as a **within-adopter firm and year fixed-effects design with event-study diagnostics**, not as a canonical untreated-control difference-in-differences design. The design still supports useful within-firm evidence around commitment and validation, but causal claims should be phrased carefully.

Nothing in the update requires removing a core dissertation finding outright. The recommended revision is to retain the main narrative while making the limitations more precise, especially around causal language, event-study sensitivity, Scope 3 taxonomy, current SBTi metadata, and sector-specific rule changes.

## 2. Why We Did This Project

The dissertation was written using SBTi data originally pulled around June 2025 and a financial panel covering 2012-2024. Since then, the SBTi standards and public dashboard structure have evolved. The project therefore had two linked problems:

1. Reproducibility: can the original pipeline still reproduce the dissertation-style results, and can the fragile methodological logic be protected?
2. Interpretation: do updated SBTi standards and current metadata change what the historical results mean?

The project also needed to avoid a common error: using current SBTi statuses as if they were historical event-time facts. The updated SBTi files are useful, but they are current metadata overlays, not a replacement for the original event construction.

## 3. What The Original Dissertation Claimed

The dissertation argued that SBTi target-setting has a two-stage financial profile. The initial commitment to set a target was interpreted as a signaling event, while official validation was interpreted as the point where implementation/accountability costs begin to materialize.

Its core claims were:

- Commitment produces positive signaling effects.
- Validation is associated with an operational performance dip.
- More ambitious S1+S2 targets mitigate costs: the Ambition Shield.
- Costs are concentrated in public firms: the Public-Private Chasm.
- Leverage creates a nonlinear financial constraint: the Leverage Trap.
- Headline market/valuation metrics show limited average response: Market Indifference.
- Firms with absolute Scope 3 targets appear less financially harmed: the Scope 3 Puzzle.
- Dynamic results suggest implementation timing, scale shock, and employment adjustment.

The original design used firm fixed effects, year fixed effects, controls for size and leverage, firm-clustered standard errors, and event-time indicators around the first validated near-term target.

## 4. What Changed In The Codebase

The project moved from a collection of legacy scripts toward a staged, documented pipeline:

- Legacy reproduction mode freezes and reproduces original outputs while preserving known quirks.
- Refactored legacy mode reproduces legacy behavior with modular code and deterministic compatibility rules.
- Refactored-clean mode adds cleaner statistical diagnostics without replacing the legacy benchmark.
- Current SBTi overlay mode builds a May 2026 metadata overlay from frozen by-company, by-target, and data dictionary files.
- Methodology robustness mode tests sensitivity to updated SBTi-aware classifications.
- Phase 4B robustness targets the Public-Private Chasm and Leverage Trap.
- Final synthesis mode produces decision-ready dissertation update memos.
- Phase 6 added README, developer docs, dependency files, validation, output manifests, and a unified command wrapper.

The biggest engineering improvement is that legacy behavior is now protected rather than accidentally overwritten. The codebase distinguishes reproduction, diagnostics, metadata overlays, robustness checks, and synthesis.

## 5. What Changed Statistically

The legacy results were preserved first. The project did not silently replace event definitions, ambition definitions, Scope 3 definitions, winsorization, filtering, or public/private classification.

The statistical improvements were added separately:

- The clean event-study uses mutually exclusive event-time bins.
- The reference period is clearly `t = -1`.
- The broad `post_event` dummy is removed from clean event-study models.
- Joint pre-trend tests are reported.
- Model-level attrition and registry outputs are produced.
- Centered leverage robustness makes nonlinear leverage interpretation clearer.

These diagnostics do not erase the dissertation results. They clarify where the legacy results are strong and where timing claims are more fragile.

The clean event-study especially matters for:

- `log_revt`: the sustained scale-shock evidence is weaker under the clean full specification.
- `log_emp`: employment dynamics show a material pre-trend concern.
- dynamic timing generally: legacy event-study output should be treated as a reproduction benchmark, while clean event-study output should be treated as the preferred timing diagnostic.

## 6. What Changed Because Of Updated SBTi Context

The updated SBTi context changes interpretation more than it changes historical results.

Key changes:

- Corporate Net-Zero Standard V2 is forward-looking and should not be retroactively applied.
- The 2026 Absolute Contraction Approach update affects future ambition comparability, not the validity of historical targets.
- Financial institutions now have a structurally distinct net-zero framework.
- FLAG-relevant firms now require more careful treatment because land-intensive target logic is more differentiated.
- Automotive/land transport guidance is changing and automotive firms should be flagged.
- Scope 3 target-setting is no longer well summarized by a single absolute Scope 3 binary.
- Current target statuses, removals, commitments, renewals, and review cycles are useful caveats but not historical event-time statuses.

The dissertation should therefore say: the results describe firms validated under the earlier SBTi regime and should not be generalized mechanically to the post-2025 SBTi architecture.

## 7. What The Updated SBTi Files Added

The May 2026 SBTi files added a current metadata overlay with:

- current company status fields;
- current near-term, long-term, and net-zero status fields;
- finance-sector flags;
- FLAG-relevant sector and observed target proxies;
- automotive flags;
- oil and gas, power/utilities, chemicals, buildings/real estate, and high-Scope-3 sector proxies;
- richer current Scope 3 target taxonomy;
- current target-row and commitment-row distinctions.

The overlay matched 4,103 of 4,114 historical SBTi firms, a 99.7% match rate. This means the current metadata overlay is highly useful for robustness and caveat language, but it still does not rewrite historical treatment timing.

The overlay also showed that the legacy Scope 3 variable is narrow. In the Scope 3 comparison, the legacy absolute Scope 3 variable captured 1,446 firms, while current any-target-including-Scope-3 captured 2,224 firms. That gap is important for interpretation: the old variable was not wrong, but it was not a complete current Scope 3 taxonomy.

## 8. What The Robustness Checks Showed

The methodology-aware robustness checks tested whether conclusions were sensitive to updated SBTi-aware classifications.

Main findings:

- Excluding or isolating financial institutions did not overturn the main story.
- Excluding FLAG-relevant, automotive, oil and gas, or all standard-sensitive firms did not collapse the core operational narrative.
- Current Scope 3 taxonomy changes how the Scope 3 Puzzle should be interpreted, but does not imply the original variable was invalid.
- Current target-status scenarios are useful caveats, not causal treatment variables.
- Public/private robustness in Phase 4B upgraded the Public-Private Chasm from "not directly comparable" to "mostly robust with caveat."
- Leverage robustness in Phase 4B upgraded the Leverage Trap from "not directly comparable" to "mostly robust with caveat."

The robustness layer did not identify a reason to remove any core dissertation finding. It did identify several places where wording should be softer and more precise.

## 9. Which Conclusions Survived

The following conclusions survived the full update:

- The two-stage commitment-versus-validation narrative.
- The post-validation operational dip.
- The Ambition Shield.
- The Public-Private Chasm.
- The Leverage Trap.
- Average Market Indifference.

These should remain central to the dissertation, with caveats about design, SBTi regime, and robustness.

## 10. Which Conclusions Need Caveats

Several conclusions remain useful but need more careful wording:

- The Ambition Shield may reflect strategic preparedness, not only target stringency.
- Public-Private Chasm results are robust but sample-composition and disclosure-regime dependent.
- Leverage Trap results are clearer when centered leverage models are used for interpretation.
- Market Indifference is an average result and does not rule out sector-specific valuation responses.
- Scope 3 Puzzle is a narrow historical result, not a complete statement about modern Scope 3 target-setting.
- Current SBTi target statuses must be described as current metadata, not event-time facts.

## 11. Which Conclusions Became Weaker Or More Nuanced

The conclusions most weakened or nuanced are:

- **Sustained scale shock:** the legacy log-revenue event-study depended partly on no-size fallback behavior; the clean full-spec event-study weakens this claim.
- **Employment dynamics:** clean diagnostics show a material pre-trend concern for `log_emp`, so employment findings should be exploratory.
- **Temporal implementation dip:** the basic idea remains plausible, but exact dynamic timing should rely on clean event-study diagnostics rather than the legacy overlapping dummy design.
- **Scope 3 Puzzle:** the result survives as a historical narrow-construct finding, but updated taxonomy makes any broad Scope 3 interpretation too strong.

## 12. What Should Be Changed In The Dissertation Wording

The most important wording changes are:

1. Rephrase the empirical design as within-adopter firm/year fixed effects with event-study diagnostics, not canonical untreated-control DiD.
2. Add a caveat that results apply to the 2012-2024, pre-mid-2025 SBTi rule regime.
3. Describe validation as the start of an accountability/review cycle, not the endpoint of credibility.
4. Treat the Ambition Shield as evidence consistent with ambition and transition preparedness.
5. Define the Scope 3 variable as a narrow historical absolute-target construct.
6. Add finance, FLAG, automotive, and oil/gas robustness caveats.
7. Downgrade log-revenue scale shock and employment dynamics to specification-sensitive/exploratory findings.
8. Avoid saying current SBTi statuses were known at the time of validation.
9. Keep causal language careful: "associated with," "consistent with," and "within-firm changes" are safer than "causes."

## 13. What Should Not Be Changed

The dissertation should not change:

- first validated near-term target as the historical validation event;
- the commitment-versus-validation distinction;
- the annualized S1+S2 ambition variable as a legacy-regime metric;
- the strict legacy Scope 3 variable for reproduction;
- source-specific winsorization and filtering in legacy/refactored legacy modes;
- the public/private classification rule;
- the baseline historical sample;
- the main conclusion that validation is associated with operational costs and limited average market response.

The right update is not to rewrite the project from scratch. It is to preserve the historical benchmark and add careful methodological/contextual caveats.

## 14. What Remains Unresolved

Several limitations remain:

- There is no true non-SBTi untreated control group.
- Current SBTi metadata is not historical metadata.
- Post-2024 financial data are unavailable.
- Historical SBTi dashboard snapshots are not available, so event-time target status cannot be reconstructed.
- Some event-study claims are specification-sensitive.
- `log_emp` has a material pre-trend concern.
- Multiple testing across outcomes, sectors, regions, and subgroups remains a concern.
- Current SBTi standards are still evolving, especially around CNZS V2, automotive, finance, and target-status infrastructure.
- Financial effects cannot yet be linked directly to actual emissions reductions without emissions data.

## 15. Recommended Next Steps If New Financial Data Become Available

If new financial data become available, the next empirical stage should be a true extension rather than a silent replacement of the dissertation.

Recommended steps:

1. Extend the financial panel beyond 2024 in a separate output mode.
2. Build a matched non-SBTi control group to support a true DiD design.
3. Preserve the original 2012-2024 results as the legacy benchmark.
4. Add method-aware ambition measures for post-2025 targets.
5. Separate finance, FLAG, automotive, oil/gas, utilities, and chemicals in baseline or preferred sensitivity specifications.
6. Rebuild Scope 3 using richer target-type categories rather than a single absolute-target binary.
7. Incorporate historical SBTi snapshots if obtainable to reconstruct target status at event time.
8. Link financial outcomes to emissions outcomes if emissions data are available.
9. Treat post-2025 standards changes as a new institutional regime, not a retroactive correction to the old one.

## Bottom Line

The dissertation is fundamentally salvageable and substantially strengthened by the update. Its core narrative remains intact: SBTi commitment and validation are financially different events; validation is associated with operational costs; ambition, ownership, and leverage shape those costs; and markets do not appear to price the average effect strongly. The revised version should be more careful about causal language, SBTi rule-regime boundaries, Scope 3 taxonomy, and event-study timing, but it does not need to abandon its main findings.
