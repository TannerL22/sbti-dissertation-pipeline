# Final Dissertation Update Memo

## 1. Executive Summary

The original dissertation conclusions largely survive the improved pipeline and updated SBTi context, but the language should become more precise. The strongest surviving findings are the two-stage commitment-versus-validation narrative, the post-validation operational dip, the Ambition Shield, the Public-Private Chasm, the Leverage Trap, and average Market Indifference. The findings that need the strongest caveats are the Scope 3 Puzzle, the dynamic event-study timing, the sustained log-revenue scale shock, and employment dynamics.

The most important update is conceptual rather than destructive: the results remain valid as historical evidence on firms validated under the 2012-2024, pre-mid-2025 SBTi regime. They should not be presented as timeless evidence about the post-2025 SBTi architecture, which now has more differentiated finance, FLAG, automotive, Scope 3, renewal, and target-status logic.

| Dissertation finding | Final assessment | Why |
|---|---|---|
| Two-stage signaling vs implementation-cost narrative | Mostly robust | Legacy and refactored results reproduce the commitment/validation contrast; current SBTi changes reinforce the distinction but require lifecycle caveats. |
| Post-validation operational dip | Mostly robust with caveat | Main post-validation models reproduce operational weakness, especially operating margin/log EBITDA; clean event-study changes timing details. |
| Ambition Shield | Mostly robust with caveat | Positive ambition interactions persist broadly, but should be interpreted partly as strategic preparedness rather than pure target-stringency effect. |
| Public-Private Chasm | Mostly robust with caveat | Phase 4B finds stronger significant post-validation effects in public split models than private split models. |
| Leverage Trap | Mostly robust with caveat | Phase 4B preserves nonlinear leverage evidence in uncentered and centered variants; centered models clarify interpretation. |
| Market Indifference | Mostly robust | Tobin's Q/headline market response remains broadly muted on average. |
| Scope 3 Puzzle | Mostly robust with caveat | Legacy Scope 3 is historically precise but narrower than current taxonomy; broader current Scope 3 metadata changes interpretation. |
| Temporal implementation dip | Sensitive to specification | Corrected clean event-study is better for timing diagnostics; legacy dummies and fallback behavior should be documented. |
| Sustained scale shock | Sensitive to specification | Legacy log-revenue scale shock depends partly on no-size fallback/event-study design; clean full-spec weakens this claim. |
| Employment dynamics | Weakened / sensitive | Clean event-study shows material pre-trend concern for log employees. |

## 2. What Changed Across Phases

| Phase | What changed | Effect on conclusions |
|---|---|---|
| Legacy reproduction | Froze inputs, backed up outputs, reran legacy scripts, and documented quirks. | Main fixed-effects and predictive results are substantively reproducible; event-study discrepancy was isolated. |
| Refactored legacy | Built modular legacy pipeline with deterministic event-study compatibility fallback. | Preserves dissertation-facing behavior, including no-size fallback for `revenue_growth_winsorized` and `log_revt`. |
| Refactored-clean stats | Added mutually exclusive event-study bins, pre-trend tests, model registry, and centered leverage diagnostics. | Improves statistical interpretation; weakens some dynamic claims but does not replace legacy results. |
| Current SBTi overlay | Built May 2026 current metadata overlay with finance, FLAG, automotive, oil/gas, status, and Scope 3 taxonomy flags. | Adds interpretation/robustness context only; does not change historical event variables. |
| Methodology robustness | Reran main models across overlay-based exclusions and current metadata groups. | Most conclusions are mostly robust with caveats; Scope 3 taxonomy needs clearer wording. |
| Public/private and leverage robustness | Targeted the two previously non-comparable conclusions. | Upgrades Public-Private Chasm and Leverage Trap to mostly robust with caveat. |

These changes fall into three categories. Code and reproducibility improvements make the dissertation easier to defend. Statistical-specification improvements clarify timing and leverage interpretation. SBTi classification/context improvements identify where the historical sample needs caveats. These are not interchangeable: a current metadata caveat is not a failed reproduction, and a clean event-study sensitivity is not a post-2025 SBTi result.

## 3. Final Interpretation of Each Core Finding

### 1. Two-Stage Signaling Vs Implementation-Cost Narrative

Original claim: the initial commitment acts as a positive signal, while validation triggers implementation costs.

Legacy/refactored evidence: the main regression and commitment-date robustness are substantively reproducible. The refactored legacy pipeline preserves the commitment-validation distinction and the dissertation-facing benchmark.

Clean statistical evidence: clean event-study diagnostics do not directly replace the commitment/validation comparison. They mainly clarify timing around validation.

SBTi overlay evidence: current dashboard fields preserve the institutional distinction between commitment rows and target rows. Current status changes do not rewrite historical timing.

Final interpretation: retain the two-stage narrative as a strong organizing interpretation, but describe it as evidence consistent with signaling and implementation-cost mechanisms, not as definitive untreated-control causal proof.

Caveat language: "The design identifies within-adopter changes around commitment and validation dates, conditional on firm and year fixed effects, rather than a canonical untreated-control difference-in-differences estimate."

### 2. Post-Validation Operational Performance Dip

Original claim: validation is followed by weaker operational performance.

Legacy/refactored evidence: key Model 1 results reproduce. Operating margin remains negative and significant; log EBITDA remains negative in the legacy benchmark.

Clean statistical evidence: clean event-study timing is more conservative, but it does not erase the average post-validation operational-cost result.

SBTi overlay evidence: finance/FLAG/auto/oil-gas and status sensitivity checks do not overturn the broad operational-cost story.

Final interpretation: retain, but distinguish average post-period FE models from dynamic event-study timing.

Caveat language: "The operational dip is strongest in average post-validation models; dynamic timing estimates are more sensitive to event-study specification."

### 3. Ambition Shield

Original claim: higher target ambition mitigates validation costs.

Legacy/refactored evidence: the S1+S2 ambition interaction is preserved and remains positive in the central operating-margin model.

Clean statistical evidence: clean mode did not redefine ambition. It protects the legacy definition while adding diagnostics elsewhere.

SBTi overlay evidence: Phase 4 finds the ambition interaction positive in most scenario-DV models, but post-2025 ACA changes mean future ambition comparability requires method-aware measures.

Final interpretation: retain the Ambition Shield, but interpret it as a mix of target ambition and firm readiness under the older SBTi rule regime.

Caveat language: "Higher ambition may proxy for stronger transition preparedness, cleaner starting assets, or better operational governance, not only for a more demanding target."

### 4. Public-Private Chasm

Original claim: validation costs are concentrated in public firms.

Legacy/refactored evidence: legacy public/private splits and interactions are preserved.

Clean statistical evidence: Phase 2B did not change public/private logic.

SBTi overlay evidence: Phase 4B finds public split models have more significant post-validation effects than private split models; public/private evidence remains visible after finance and standard-sensitive exclusions.

Final interpretation: retain, but add a sample-composition caveat and describe sub-sample models as more flexible than pooled interactions.

Caveat language: "The public-private contrast is robust in targeted checks, though its magnitude should be interpreted as sample- and disclosure-regime dependent."

### 5. Leverage Trap

Original claim: leverage has a nonlinear effect on post-validation outcomes.

Legacy/refactored evidence: the uncentered legacy leverage specification is preserved.

Clean statistical evidence: centered leverage robustness makes the post-event term interpretable at average leverage and preserves meaningful nonlinear signals.

SBTi overlay evidence: Phase 4B finds active nonlinear/interacted leverage terms in both uncentered and centered models.

Final interpretation: retain, but present centered leverage as the clearer robustness interpretation.

Caveat language: "The leverage trap is best read as a nonlinear robustness pattern in firms' capacity to absorb validation-linked implementation demands."

### 6. Market Indifference

Original claim: headline market valuation metrics show limited response.

Legacy/refactored evidence: Tobin's Q and other headline metrics remain broadly null.

Clean statistical evidence: no clean diagnostic overturns the average market-indifference finding.

SBTi overlay evidence: Phase 4 does not reveal an overlay-driven reversal.

Final interpretation: retain as an average finding, with room for sector-specific exceptions.

Caveat language: "Market indifference is an average result; it does not rule out valuation effects in specific sectors, cohorts, or highly salient firms."

### 7. Scope 3 Puzzle

Original claim: firms with absolute Scope 3 targets appear less financially harmed than firms without.

Legacy/refactored evidence: the strict legacy variable is preserved: standalone `scope == 3` and `type == Absolute`.

Clean statistical evidence: no clean-mode change redefines Scope 3.

SBTi overlay evidence: current metadata shows the legacy variable is narrower than current taxonomy. In the historical overlay comparison, current any-Scope-3 captures many firms not captured by the legacy absolute indicator.

Final interpretation: retain as a historical narrow-construct result, but soften any implication that Scope 3 decarbonization is intrinsically easier.

Caveat language: "The Scope 3 result likely reflects selection into more mature value-chain governance under the earlier SBTi regime."

### 8. Temporal Implementation Dip

Original claim: dynamic effects reveal an implementation dip after validation.

Legacy/refactored evidence: legacy event-study behavior is preserved, including overlapping dummies and no-size fallback for two DVs.

Clean statistical evidence: clean mutually exclusive bins improve event-time interpretation and should be treated as the preferred diagnostic for timing.

SBTi overlay evidence: Phase 4 selected clean event-study checks support robustness with caveats.

Final interpretation: retain the idea of implementation timing, but avoid overreliance on the exact legacy event-study coefficients.

Caveat language: "Event-study timing is sensitive to dummy construction and model specification."

### 9. Sustained Scale Shock

Original claim: log revenue shows a sustained scale shock.

Legacy/refactored evidence: the legacy dissertation-facing log-revenue event-study used no-size fallback.

Clean statistical evidence: the clean full specification substantially weakens the t0 log-revenue effect.

SBTi overlay evidence: overlay robustness does not transform this into a stronger claim.

Final interpretation: downgrade to a suggestive legacy pattern.

Caveat language: "The scale-shock finding is specification-sensitive and should be discussed as exploratory."

### 10. Employment Dynamics

Original claim: employment dynamics evolve after validation.

Legacy/refactored evidence: legacy outputs preserve the employment dynamic pattern.

Clean statistical evidence: log employees has a material pre-trend concern in clean diagnostics.

SBTi overlay evidence: selected robustness event-studies continue to flag employment pre-trends.

Final interpretation: weaken.

Caveat language: "Employment dynamics should be treated as exploratory because pre-validation trends complicate event-time interpretation."

## 4. Methodological Implications of Updated SBTi Context

Corporate Net-Zero Standard V2 matters for forward-looking interpretation, not historical reclassification. It should be described as draft/transition context rather than retroactively imposed on targets validated in 2012-2024.

The 2026 Absolute Contraction Approach update affects comparability of future ambition measures. It does not invalidate the dissertation's annualized S1+S2 absolute reduction metric as a legacy-regime construct.

The Financial Institutions Net-Zero Standard means finance firms should be flagged and tested separately. The historical pooled baseline remains usable, but refreshed analysis should not ignore finance-specific architecture.

FLAG Guidance changes mean land-intensive firms need robustness flags. The Phase 3/4 pipeline now includes sector and observed target proxies, with explicit over-/under-inclusion caveats.

Automotive/land transport changes mean automotive and auto-parts firms should be flagged. The current robustness layer does this without changing the historical baseline.

Scope 3 now requires richer taxonomy. The old absolute Scope 3 variable was historically precise but too narrow for future-ready analysis.

Current target status is useful for caveat language and sensitivity checks. It is not historical status and must not define event-time treatment.

Carbon credits, EACs, BVCM, and neutralization should affect framing of substantiveness and future target quality only where the policy report supports it. They should not be used to reinterpret 2012-2024 financial outcomes without new data.

## 5. What Should Change in the Dissertation

| Dissertation section | Recommended change | Severity |
|---|---|---|
| Abstract | Add one caveat sentence that results apply to the pre-mid-2025 SBTi regime and a within-adopter FE design. | Moderate |
| Introduction | Keep research motivation but distinguish historical validation from the newer review/renewal/status lifecycle. | Minor |
| Literature review | Add updated SBTi governance, sector-specific standards, and finance/FLAG/Scope 3 differentiation as context. | Moderate |
| Data/methodology | Rephrase design as within-adopter firm/year FE with event-study diagnostics, not canonical untreated-control DiD. | Major |
| Results | Preserve main results; label scale-shock and employment dynamics as specification-sensitive. | Moderate |
| Discussion | Add robustness findings from finance/FLAG/auto/oil-gas and Scope 3 taxonomy. | Moderate |
| Limitations | Add current metadata not event-time metadata, no untreated controls, no post-2024 financial outcomes, and event-study sensitivity. | Major |
| Future research | Emphasize new financial data, historical SBTi snapshots, method-aware ambition, and emissions data. | Moderate |
| Implications | Keep managerial/investor implications but caution against treating all validated targets as institutionally identical. | Moderate |

## 6. What Should Not Change

- First validated near-term target remains a defensible historical event.
- Commitment versus validation remains a core and useful distinction.
- Annualized S1+S2 ambition remains defensible as a legacy-regime metric.
- The legacy Scope 3 absolute-target variable remains valid as a narrow historical construct.
- Public/private comparison remains defensible with caveats.
- The design can remain a within-adopter FE/event-study design.
- Market indifference remains defensible as an average result.

## 7. Remaining Weaknesses

- There is no true non-SBTi untreated control group.
- Current SBTi metadata is not event-time metadata.
- Post-2024 financial data are unavailable.
- Some event-study findings are sensitive to dummy design and fallback specifications.
- `log_emp` has a material clean pre-trend concern.
- Legacy event-study fallback behavior must be documented.
- Multiple testing across sectors, geographies, DVs, and sub-samples remains a concern.
- Sector-specific SBTi standards continue to evolve.

## 8. Recommended Next Empirical Work

Possible now with existing data:

- Add a short appendix comparing legacy, clean, overlay, and Phase 4B verdicts.
- Add multiple-testing caveats for sector/geography chapters.
- Produce publication-ready tables from the refactored outputs.

Possible only with new financial data:

- Extend outcomes beyond 2024.
- Build a matched non-SBTi control group for a true DiD design.
- Re-estimate market valuation effects as climate-risk disclosure systems mature.

Possible only with historical SBTi tracker snapshots:

- Reconstruct event-time target status, renewal status, removed/expired status, and target update cycles.
- Distinguish initial validation from revalidation/renewal in event time.

Possible only with emissions data:

- Separate financial effects of target validation from actual emissions abatement.
- Test whether the Ambition Shield reflects actual decarbonization progress or ex-ante transition readiness.
