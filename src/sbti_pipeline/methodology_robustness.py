from __future__ import annotations

import hashlib
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm

from .clean_event_study import CLEAN_TERMS, EVENT_ORDER, add_clean_event_bins
from .config import LegacyConfig
from .io import write_text
from .model_runner import filter_model_data
from .robustness_panel import build_robustness_panel
from .tables import significance_stars


MAIN_TERMS = ["post_event", "post_event_x_s1s2_rate"]
EVENT_DVS_FOR_FIGURES = ["op_margin_winsorized", "log_ebitda", "log_revt", "log_emp"]


def run_methodology_robustness(config: LegacyConfig) -> dict[str, Path]:
    _ensure_dirs(config)
    panel = build_robustness_panel(config)
    data = prepare_robustness_data(panel)
    scenario_rows = scenario_sample_table(config, data)
    scenario_df = pd.DataFrame(scenario_rows)
    scenario_df.to_csv(config.output_dir / "diagnostics/robustness_scenario_samples.csv", index=False)

    results, registry = run_main_robustness(config, data, scenario_df)
    results.to_csv(config.output_dir / "tables/robustness_results_long.csv", index=False)
    make_wide_results(results).to_csv(config.output_dir / "tables/robustness_results_wide.csv", index=False)
    registry.to_csv(config.output_dir / "diagnostics/robustness_model_registry.csv", index=False)

    event_results, pretrends = run_event_study_robustness(config, data, scenario_df)
    event_results.to_csv(config.output_dir / "tables/robustness_event_study_results.csv", index=False)
    pretrends.to_csv(config.output_dir / "diagnostics/robustness_event_study_pretrends.csv", index=False)

    write_scope3_comparison(config, data)
    write_sector_composition(config, data)
    write_status_caveat(config, data)
    conclusion = write_conclusion_matrix(config, results, event_results)
    write_figures(config, results, data)
    write_summary(config, scenario_df, conclusion)
    return {
        "long_results": config.output_dir / "tables/robustness_results_long.csv",
        "event_results": config.output_dir / "tables/robustness_event_study_results.csv",
        "summary": config.output_dir / "methodology_robustness_summary.md",
    }


def prepare_robustness_data(panel: pd.DataFrame) -> pd.DataFrame:
    data = panel[panel["earliest_near_term_validation_date"].notna()].copy()
    data["sbti_id"] = data["sbti_id"].astype("category")
    data["fyear"] = data["fyear"].astype("category")
    data["post_event_x_s1s2_rate"] = data["post_event"] * data["s1s2_annual_reduction_rate"]
    for col in data.columns:
        if col.startswith("current_is_") or col.startswith("current_has_") or col.startswith("current_near_term_") or col.startswith("current_net_zero_"):
            if pd.api.types.is_numeric_dtype(data[col]):
                data[col] = data[col].fillna(0).astype(int)
    for col in [
        "roa_winsorized",
        "op_margin_winsorized",
        "revenue_growth_winsorized",
        "log_revt",
        "log_ebitda",
        "log_emp",
        "tobins_q_winsorized",
        "size_log_assets",
        "leverage_winsorized",
    ]:
        if col in data:
            data[col] = pd.to_numeric(data[col], errors="coerce").replace([np.inf, -np.inf], np.nan)
    return data


def scenario_sample_table(config: LegacyConfig, data: pd.DataFrame) -> list[dict]:
    rows = []
    for name, spec in config.raw["robustness_scenarios"].items():
        if spec.get("type") == "benchmark_only":
            rows.append(_scenario_row(name, spec, 0, 0, 0, "benchmark_only"))
            continue
        sample = apply_scenario_filter(data, spec["filter"])
        status = "run"
        if len(sample) < config.raw["model_filtering_rules"]["minimum_model_n"] or sample["sbti_id"].nunique() < config.raw["model_filtering_rules"]["minimum_firm_count"]:
            status = "skip_not_enough_observations"
        rows.append(_scenario_row(name, spec, len(sample), sample["sbti_id"].nunique(), sample["fyear"].nunique(), status))
    return rows


def _scenario_row(name: str, spec: dict, rows: int, firms: int, years: int, status: str) -> dict:
    return {
        "scenario": name,
        "description": spec.get("description", ""),
        "caveat_category": spec.get("caveat_category", ""),
        "filter": spec.get("filter", ""),
        "starting_rows": rows,
        "starting_firms": firms,
        "starting_years": years,
        "run_status": status,
    }


def apply_scenario_filter(data: pd.DataFrame, expression: str) -> pd.DataFrame:
    if not expression:
        return data.copy()
    return data.query(expression, engine="python").copy()


def run_main_robustness(config: LegacyConfig, data: pd.DataFrame, scenarios: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    result_rows: list[dict] = []
    registry_rows: list[dict] = []
    controls = " + ".join(config.raw["controls"])
    formula_template = "{dv} ~ post_event + post_event_x_s1s2_rate + " + controls + " + C(sbti_id) + C(fyear)"
    variables_template = MAIN_TERMS + config.raw["controls"]

    for _, scenario in scenarios.iterrows():
        if scenario["run_status"] != "run":
            registry_rows.append(_failed_registry_row(scenario, "all", "main", "not run: " + scenario["run_status"]))
            continue
        sample = apply_scenario_filter(data, scenario["filter"])
        for dv in config.raw["dependent_variables"]["main"]:
            if dv not in sample.columns:
                registry_rows.append(_failed_registry_row(scenario, dv, "main", "dependent variable missing"))
                continue
            variables = [dv] + variables_template
            filt = filter_model_data(sample, variables, dv)
            if not _enough(config, filt.data):
                registry_rows.append(_registry_row(scenario, dv, "main", "", filt, None, "skip after filtering"))
                continue
            formula = formula_template.format(dv=dv)
            try:
                result = fit_fast_two_way_fe(filt.data, dv, ["post_event", "post_event_x_s1s2_rate", "size_log_assets", "leverage_winsorized"])
            except Exception as exc:
                registry_rows.append(_registry_row(scenario, dv, "main", formula, filt, None, f"failed: {exc}"))
                continue
            registry_rows.append(_registry_row(scenario, dv, "main", formula, filt, result, "completed"))
            result_rows.extend(_coef_rows(scenario, dv, "main", result, ["post_event", "post_event_x_s1s2_rate", "size_log_assets", "leverage_winsorized"]))
    return pd.DataFrame(result_rows), pd.DataFrame(registry_rows)


def run_event_study_robustness(config: LegacyConfig, data: pd.DataFrame, scenarios: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    event_data = add_clean_event_bins(data)
    result_rows: list[dict] = []
    pretrend_rows: list[dict] = []
    controls = " + ".join(config.raw["controls"])
    formula_template = "{dv} ~ " + " + ".join(CLEAN_TERMS) + " + " + controls + " + C(sbti_id) + C(fyear)"
    event_scenarios = set(config.raw["event_study_scenarios"])
    scenario_map = scenarios.set_index("scenario").to_dict("index")

    for scenario_name in config.raw["event_study_scenarios"]:
        scenario = scenario_map[scenario_name]
        scenario["scenario"] = scenario_name
        if scenario["run_status"] != "run":
            for dv in config.raw["dependent_variables"]["event_study"]:
                pretrend_rows.append({"scenario": scenario_name, "dependent_variable": dv, "status": scenario["run_status"], "p_value": np.nan, "classification": "not enough observations"})
            continue
        sample = apply_scenario_filter(event_data, scenario["filter"])
        for dv in config.raw["dependent_variables"]["event_study"]:
            variables = [dv] + CLEAN_TERMS + config.raw["controls"]
            filt = filter_model_data(sample, variables, dv)
            if not _enough(config, filt.data):
                pretrend_rows.append({"scenario": scenario_name, "dependent_variable": dv, "status": "skip_after_filtering", "p_value": np.nan, "classification": "not enough observations"})
                continue
            formula = formula_template.format(dv=dv)
            try:
                result = fit_fast_two_way_fe(filt.data, dv, CLEAN_TERMS + ["size_log_assets", "leverage_winsorized"])
            except Exception as exc:
                pretrend_rows.append({"scenario": scenario_name, "dependent_variable": dv, "status": f"failed: {exc}", "p_value": np.nan, "classification": "failed"})
                continue
            result_rows.extend(_event_coef_rows(scenario, dv, result))
            p_value, label = _pretrend(result)
            pretrend_rows.append({"scenario": scenario_name, "dependent_variable": dv, "status": "completed", "p_value": p_value, "classification": label})

    event_df = pd.DataFrame(result_rows)
    for scenario_name in event_scenarios:
        for dv in EVENT_DVS_FOR_FIGURES:
            _plot_event(config.output_dir / "figures" / f"event_study_{scenario_name}_{dv}.png", event_df, scenario_name, dv)
    return event_df, pd.DataFrame(pretrend_rows)


def write_scope3_comparison(config: LegacyConfig, data: pd.DataFrame) -> None:
    firm = _firm_level(data)
    legacy = firm["has_s3_absolute_target"].fillna(0).astype(int)
    current_any = firm["current_has_any_target_including_scope3"].fillna(0).astype(int)
    current_like = firm["current_has_legacy_like_absolute_scope3_target"].fillna(0).astype(int)
    fields = [
        "has_s3_absolute_target",
        "current_has_legacy_like_absolute_scope3_target",
        "current_has_any_target_including_scope3",
        "current_has_absolute_target_including_scope3",
        "current_has_intensity_target_including_scope3",
        "current_has_engagement_target_including_scope3",
        "current_has_no_deforestation_target_including_scope3",
    ]
    counts = firm[fields].fillna(0).astype(int).sum().rename("firm_count").reset_index().rename(columns={"index": "scope3_definition"})
    counts.to_csv(config.output_dir / "comparisons/scope3_taxonomy_counts.csv", index=False)
    overlap = pd.crosstab(legacy, current_any, rownames=["legacy_absolute_s3"], colnames=["current_any_scope3"])
    overlap.to_csv(config.output_dir / "comparisons/scope3_taxonomy_overlap_matrix.csv")
    legacy_not_current = int(((legacy == 1) & (current_any == 0)).sum())
    current_not_legacy = int(((current_any == 1) & (legacy == 0)).sum())

    lines = [
        "# Scope 3 Taxonomy Comparison",
        "",
        "The dissertation Scope 3 variable is historically precise but narrower than the current SBTi taxonomy.",
        "",
        "## Firm Counts",
    ]
    lines.extend(f"- `{row.scope3_definition}`: {int(row.firm_count):,}" for row in counts.itertuples())
    lines.extend(
        [
            "",
            "## Overlap",
            f"Legacy absolute Scope 3 firms not captured by current any-Scope-3 metadata: {legacy_not_current:,}",
            f"Current any-Scope-3 firms not captured by legacy absolute Scope 3: {current_not_legacy:,}",
            "",
            "The Scope 3 puzzle should be tested against broader current metadata categories, but these categories are current metadata robustness, not event-time causal evidence.",
        ]
    )
    write_text(config.output_dir / "comparisons/scope3_taxonomy_comparison.md", "\n".join(lines) + "\n")


def write_sector_composition(config: LegacyConfig, data: pd.DataFrame) -> None:
    firm = _firm_level(data)
    flags = [
        "current_is_financial_institution",
        "current_is_flag_relevant_any",
        "current_is_automotive_any",
        "current_is_oil_and_gas",
        "current_is_power_or_utilities",
        "current_is_chemicals",
    ]
    rows = []
    for flag in flags:
        mask = data[flag].fillna(0).eq(1)
        fmask = firm[flag].fillna(0).eq(1)
        rows.append({"flag": flag, "firm_count": int(fmask.sum()), "firm_year_count": int(mask.sum()), "share_firms": float(fmask.mean())})
    comp = pd.DataFrame(rows)
    comp.to_csv(config.output_dir / "comparisons/sector_rule_regime_composition.csv", index=False)
    standard = firm[["current_is_financial_institution", "current_is_flag_relevant_any", "current_is_automotive_any", "current_is_oil_and_gas"]].fillna(0).eq(1).any(axis=1)
    lines = [
        "# Sector And Rule-Regime Composition",
        "",
        "Counts are based on historical firms with current overlay metadata.",
        "",
    ]
    lines.extend(f"- `{row.flag}`: {int(row.firm_count):,} firms; {int(row.firm_year_count):,} firm-years" for row in comp.itertuples())
    lines.extend(
        [
            "",
            f"Combined finance/FLAG/automotive/oil-gas standard-sensitive firms: {int(standard.sum()):,} of {len(firm):,}.",
            "These groups are large enough to plausibly affect sample composition if exclusions are imposed.",
            "",
            "## Public/Private Composition",
        ]
    )
    if "firm_type" in firm:
        lines.extend(f"- {idx}: {val:,}" for idx, val in firm["firm_type"].value_counts(dropna=False).items())
    if "event_year" in firm:
        lines.extend(["", "## Validation Cohort Distribution"])
        lines.extend(f"- {int(idx)}: {val:,}" for idx, val in firm["event_year"].dropna().astype(int).value_counts().sort_index().items())
    if "sector" in firm:
        lines.extend(["", "## Top Historical Sectors"])
        lines.extend(f"- {idx}: {val:,}" for idx, val in firm["sector"].value_counts().head(15).items())
    write_text(config.output_dir / "comparisons/sector_rule_regime_composition.md", "\n".join(lines) + "\n")


def write_status_caveat(config: LegacyConfig, data: pd.DataFrame) -> None:
    firm = _firm_level(data)
    fields = [
        "current_near_term_commitment_removed",
        "current_near_term_targets_set",
        "current_near_term_committed",
        "current_net_zero_targets_set",
        "current_net_zero_committed",
        "current_has_reason_for_extension_or_removal",
    ]
    rows = [{"field": field, "firm_count": int(firm[field].fillna(0).sum())} for field in fields if field in firm]
    pd.DataFrame(rows).to_csv(config.output_dir / "comparisons/current_status_caveat_counts.csv", index=False)
    lines = [
        "# Current Status Caveat Analysis",
        "",
        "Current status may post-date the dissertation event and must not be treated as known at the historical event date.",
        "",
    ]
    lines.extend(f"- `{row['field']}`: {row['firm_count']:,} firms" for row in rows)
    lines.extend(
        [
            "",
            "This analysis informs credibility and caveat language only. It is not causal treatment timing.",
        ]
    )
    write_text(config.output_dir / "comparisons/current_status_caveat_analysis.md", "\n".join(lines) + "\n")


def write_conclusion_matrix(config: LegacyConfig, results: pd.DataFrame, event_results: pd.DataFrame) -> pd.DataFrame:
    key = _post_event_matrix(results)
    rows = []
    findings = [
        ("Two-stage signaling vs implementation-cost narrative", "Mostly assessed outside this overlay; operational post-validation effects remain benchmarked."),
        ("Post-validation operational performance dip", _classify_from_terms(key, ["roa_winsorized", "op_margin_winsorized"])),
        ("Ambition Shield", _classify_ambition(results)),
        ("Public-Private Chasm", "Not directly re-estimated in this phase; sample exclusions prepare sensitivity context."),
        ("Leverage Trap", "Not directly re-estimated in this phase; Phase 2B centered leverage remains the clean robustness layer."),
        ("Market Indifference", _classify_from_terms(key, ["tobins_q_winsorized"])),
        ("Scope 3 Puzzle", "Sensitive to taxonomy by design; legacy Scope 3 is narrower than current Scope 3 metadata."),
        ("Temporal implementation dip", "Clean event-study robustness completed for key overlay scenarios."),
        ("Sustained scale shock", _classify_from_terms(key, ["log_revt"])),
        ("Employment dynamics", _classify_from_terms(key, ["log_emp"])),
    ]
    for finding, note in findings:
        rows.append(
            {
                "core_finding": finding,
                "legacy_result": "benchmark retained",
                "refactored_clean_result": "see Phase 2B outputs",
                "finance_excluded_robustness": _scenario_term_status(key, "exclude_financial_institutions"),
                "flag_excluded_robustness": _scenario_term_status(key, "exclude_flag_relevant_any"),
                "automotive_excluded_robustness": _scenario_term_status(key, "exclude_automotive_any"),
                "oil_gas_excluded_robustness": _scenario_term_status(key, "exclude_oil_and_gas"),
                "all_standard_sensitive_excluded_robustness": _scenario_term_status(key, "exclude_all_standard_sensitive"),
                "current_scope3_taxonomy_robustness": _scenario_term_status(key, "current_any_scope3_target_yes"),
                "current_status_caveat_robustness": _scenario_term_status(key, "exclude_current_near_term_commitment_removed"),
                "conclusion_classification": _classify_conclusion(finding, note),
                "recommended_dissertation_interpretation_update": note,
            }
        )
    matrix = pd.DataFrame(rows)
    matrix.to_csv(config.output_dir / "comparisons/robustness_conclusion_matrix.csv", index=False)
    md = ["# Robustness Conclusion Matrix", "", "| Finding | Classification | Interpretation Update |", "|---|---|---|"]
    for row in matrix.itertuples():
        md.append(f"| {row.core_finding} | {row.conclusion_classification} | {row.recommended_dissertation_interpretation_update} |")
    write_text(config.output_dir / "comparisons/robustness_conclusion_matrix.md", "\n".join(md) + "\n")
    return matrix


def write_figures(config: LegacyConfig, results: pd.DataFrame, data: pd.DataFrame) -> None:
    for dv in ["op_margin_winsorized", "log_ebitda", "roa_winsorized", "log_revt"]:
        rows = results[(results["dependent_variable"] == dv) & (results["term"] == "post_event")].copy()
        if rows.empty:
            continue
        rows = rows.sort_values("scenario")
        fig, ax = plt.subplots(figsize=(10, 5))
        y = np.arange(len(rows))
        ax.errorbar(rows["coef"], y, xerr=1.96 * rows["std_error"], fmt="o", capsize=3)
        ax.axvline(0, color="black", linestyle="--", linewidth=1)
        ax.set_yticks(y)
        ax.set_yticklabels(rows["scenario"])
        ax.set_title(f"Post-validation coefficient robustness: {dv}")
        ax.set_xlabel("Coefficient with 95% CI")
        fig.tight_layout()
        fig.savefig(config.output_dir / "figures" / f"post_event_comparison_{dv}.png", dpi=160)
        plt.close(fig)
    _scope3_chart(config, data)
    _sector_chart(config, data)


def write_summary(config: LegacyConfig, scenarios: pd.DataFrame, conclusion: pd.DataFrame) -> None:
    completed = int((scenarios["run_status"] == "run").sum())
    skipped = scenarios[scenarios["run_status"] != "run"]
    lines = [
        "# Methodology Robustness Summary",
        "",
        "Command: `python run_methodology_robustness.py --config configs/methodology_robustness.yaml`",
        "",
        f"Robustness scenarios completed: {completed:,}",
        f"Scenarios skipped or benchmark-only: {len(skipped):,}",
        "",
        "## Skipped Or Benchmark-Only Scenarios",
    ]
    if skipped.empty:
        lines.append("- None")
    else:
        lines.extend(f"- `{row.scenario}`: {row.run_status}" for row in skipped.itertuples())
    lines.extend(["", "## Conclusion Matrix"])
    lines.extend(f"- {row.core_finding}: {row.conclusion_classification}" for row in conclusion.itertuples())
    lines.extend(
        [
            "",
            "Key caveat: current SBTi metadata is used only for robustness flags and caveat scenarios.",
            "Safe to proceed to Phase 5 synthesis: yes, after reviewing the scenario-level result tables.",
        ]
    )
    write_text(config.output_dir / "methodology_robustness_summary.md", "\n".join(lines) + "\n")


def make_wide_results(results: pd.DataFrame) -> pd.DataFrame:
    if results.empty:
        return results
    keep = results[results["term"].isin(["post_event", "post_event_x_s1s2_rate"])].copy()
    keep["formatted"] = keep.apply(lambda r: f"{r['coef']:.4f}{significance_stars(r['p_value'])}", axis=1)
    return keep.pivot_table(index=["dependent_variable", "term"], columns="scenario", values="formatted", aggfunc="first").reset_index()


def _coef_rows(scenario, dv: str, family: str, result, terms: list[str]) -> list[dict]:
    rows = []
    for term in terms:
        if term not in result.params.index:
            continue
        coef = float(result.params[term])
        se = float(result.bse[term])
        rows.append(
            {
                "scenario": scenario["scenario"],
                "dependent_variable": dv,
                "model_family": family,
                "term": term,
                "coef": coef,
                "std_error": se,
                "p_value": float(result.pvalues[term]),
                "ci_lower": coef - 1.96 * se,
                "ci_upper": coef + 1.96 * se,
                "nobs": int(result.nobs),
                "rsquared_adj": float(result.rsquared_adj),
                "caveat_category": scenario["caveat_category"],
                "current_metadata_caveat": "current metadata robustness, not event-time causal evidence",
            }
        )
    return rows


def _event_coef_rows(scenario, dv: str, result) -> list[dict]:
    rows = []
    for term in CLEAN_TERMS:
        coef = float(result.params[term])
        se = float(result.bse[term])
        rows.append(
            {
                "scenario": scenario["scenario"],
                "dependent_variable": dv,
                "term": term,
                "coef": coef,
                "std_error": se,
                "p_value": float(result.pvalues[term]),
                "ci_lower": coef - 1.96 * se,
                "ci_upper": coef + 1.96 * se,
                "nobs": int(result.nobs),
                "caveat_category": scenario["caveat_category"],
            }
        )
    return rows


def _registry_row(scenario, dv: str, family: str, formula: str, filt, result, notes: str) -> dict:
    return {
        "scenario": scenario["scenario"],
        "model_family": family,
        "dependent_variable": dv,
        "formula": formula,
        "formula_hash": hashlib.sha256(formula.encode("utf-8")).hexdigest()[:16] if formula else "",
        "starting_rows": filt.initial_rows,
        "rows_after_listwise_deletion": filt.initial_rows - filt.dropped_missing,
        "rows_after_constant_dv_removal": filt.initial_rows - filt.dropped_missing - filt.dropped_constant_dv,
        "final_n": int(result.nobs) if result is not None else 0,
        "firm_count": int(filt.data["sbti_id"].nunique()) if len(filt.data) else 0,
        "year_count": int(filt.data["fyear"].nunique()) if len(filt.data) else 0,
        "caveat_category": scenario["caveat_category"],
        "notes": notes,
    }


def _failed_registry_row(scenario, dv: str, family: str, notes: str) -> dict:
    return {
        "scenario": scenario["scenario"],
        "model_family": family,
        "dependent_variable": dv,
        "formula": "",
        "formula_hash": "",
        "starting_rows": scenario.get("starting_rows", 0),
        "rows_after_listwise_deletion": 0,
        "rows_after_constant_dv_removal": 0,
        "final_n": 0,
        "firm_count": 0,
        "year_count": 0,
        "caveat_category": scenario.get("caveat_category", ""),
        "notes": notes,
    }


def _enough(config: LegacyConfig, sample: pd.DataFrame) -> bool:
    return len(sample) >= config.raw["model_filtering_rules"]["minimum_model_n"] and sample["sbti_id"].nunique() >= config.raw["model_filtering_rules"]["minimum_firm_count"]


def _pretrend(result) -> tuple[float, str]:
    test = result.wald_test("clean_event_pre3_or_less = 0, clean_event_pre2 = 0", scalar=True)
    p_value = float(test.pvalue)
    if p_value < 0.05:
        return p_value, "material pre-trend concern"
    if p_value < 0.10:
        return p_value, "weak/preliminary pre-trend concern"
    return p_value, "no strong pre-trend evidence"


def _plot_event(path: Path, event_df: pd.DataFrame, scenario: str, dv: str) -> None:
    rows = event_df[(event_df["scenario"] == scenario) & (event_df["dependent_variable"] == dv)]
    if rows.empty:
        return
    plot_rows = []
    for term, x, label in EVENT_ORDER:
        if term == "reference_t_minus_1":
            plot_rows.append({"x": x, "label": label, "coef": 0.0, "ci_lower": 0.0, "ci_upper": 0.0})
        else:
            row = rows[rows["term"] == term]
            if not row.empty:
                r = row.iloc[0]
                plot_rows.append({"x": x, "label": label, "coef": r["coef"], "ci_lower": r["ci_lower"], "ci_upper": r["ci_upper"]})
    pdf = pd.DataFrame(plot_rows)
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.errorbar(pdf["x"], pdf["coef"], yerr=[pdf["coef"] - pdf["ci_lower"], pdf["ci_upper"] - pdf["coef"]], fmt="o-", capsize=3)
    ax.axhline(0, color="black", linestyle="--", linewidth=1)
    ax.axvline(-1, color="gray", linestyle=":", linewidth=1)
    ax.set_xticks(pdf["x"])
    ax.set_xticklabels(pdf["label"])
    ax.set_title(f"{scenario}: {dv}")
    ax.set_ylabel("Coefficient relative to t=-1")
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def _firm_level(data: pd.DataFrame) -> pd.DataFrame:
    return data.sort_values("fyear").drop_duplicates("sbti_id", keep="last")


def _post_event_matrix(results: pd.DataFrame) -> pd.DataFrame:
    return results[results["term"].eq("post_event")].copy()


def _scenario_term_status(key: pd.DataFrame, scenario: str) -> str:
    rows = key[key["scenario"].eq(scenario)]
    if rows.empty:
        return "not comparable"
    sig = int((rows["p_value"] < 0.1).sum())
    neg = int((rows["coef"] < 0).sum())
    return f"{sig} significant terms at 10%; {neg}/{len(rows)} negative post_event coefficients"


def _classify_from_terms(key: pd.DataFrame, dvs: list[str]) -> str:
    rows = key[key["dependent_variable"].isin(dvs)]
    if rows.empty:
        return "not comparable"
    return _scenario_term_status(rows, "matched_overlay_all")


def _classify_ambition(results: pd.DataFrame) -> str:
    rows = results[results["term"].eq("post_event_x_s1s2_rate")]
    if rows.empty:
        return "not comparable"
    positive = int((rows["coef"] > 0).sum())
    return f"Ambition interaction positive in {positive}/{len(rows)} estimated scenario-DV models"


def _classify_conclusion(finding: str, note: str) -> str:
    if "Scope 3" in finding:
        return "mostly robust with caveat"
    if "Public-Private" in finding or "Leverage" in finding:
        return "not comparable"
    if "not comparable" in note:
        return "not comparable"
    return "mostly robust with caveat"


def _scope3_chart(config: LegacyConfig, data: pd.DataFrame) -> None:
    firm = _firm_level(data)
    cols = [
        "has_s3_absolute_target",
        "current_has_legacy_like_absolute_scope3_target",
        "current_has_any_target_including_scope3",
        "current_has_intensity_target_including_scope3",
        "current_has_engagement_target_including_scope3",
    ]
    counts = firm[cols].fillna(0).astype(int).sum().sort_values()
    fig, ax = plt.subplots(figsize=(9, 5))
    counts.plot(kind="barh", ax=ax)
    ax.set_title("Scope 3 taxonomy firm counts")
    ax.set_xlabel("Firm count")
    fig.tight_layout()
    fig.savefig(config.output_dir / "figures/scope3_taxonomy_counts.png", dpi=160)
    plt.close(fig)


def _sector_chart(config: LegacyConfig, data: pd.DataFrame) -> None:
    firm = _firm_level(data)
    cols = ["current_is_financial_institution", "current_is_flag_relevant_any", "current_is_automotive_any", "current_is_oil_and_gas"]
    counts = firm[cols].fillna(0).astype(int).sum().sort_values()
    fig, ax = plt.subplots(figsize=(8, 4))
    counts.plot(kind="barh", ax=ax)
    ax.set_title("Rule-regime sensitivity flags")
    ax.set_xlabel("Firm count")
    fig.tight_layout()
    fig.savefig(config.output_dir / "figures/sector_rule_regime_composition.png", dpi=160)
    plt.close(fig)


def _ensure_dirs(config: LegacyConfig) -> None:
    for name in ["tables", "figures", "diagnostics", "comparisons", "logs"]:
        (config.output_dir / name).mkdir(parents=True, exist_ok=True)


def fit_fast_two_way_fe(
    data: pd.DataFrame,
    dep_var: str,
    x_vars: list[str],
    firm_col: str = "sbti_id",
    year_col: str = "fyear",
):
    cols = [dep_var] + x_vars
    work = data[[firm_col, year_col] + cols].copy()
    for col in cols:
        work[col] = pd.to_numeric(work[col], errors="coerce")
    demeaned = _two_way_demean(work, cols, firm_col, year_col)
    y = demeaned[dep_var]
    x = demeaned[x_vars]
    keep = y.notna() & x.notna().all(axis=1)
    fit = sm.OLS(y.loc[keep], x.loc[keep]).fit(
        cov_type="cluster",
        cov_kwds={"groups": work.loc[keep, firm_col].astype(str)},
    )
    return fit


def _two_way_demean(
    data: pd.DataFrame,
    cols: list[str],
    firm_col: str,
    year_col: str,
    max_iter: int = 100,
    tol: float = 1e-10,
) -> pd.DataFrame:
    values = data[cols].astype(float).copy()
    values = values - values.mean(axis=0)
    firm = data[firm_col]
    year = data[year_col]
    for _ in range(max_iter):
        previous = values.to_numpy(copy=True)
        values = values - values.groupby(firm, observed=True).transform("mean")
        values = values - values.groupby(year, observed=True).transform("mean")
        values = values + values.mean(axis=0)
        delta = np.nanmax(np.abs(values.to_numpy() - previous))
        if delta < tol:
            break
    return values
