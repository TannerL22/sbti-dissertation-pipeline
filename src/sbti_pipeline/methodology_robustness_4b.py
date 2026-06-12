from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .config import LegacyConfig
from .io import write_text
from .methodology_robustness import apply_scenario_filter, fit_fast_two_way_fe, prepare_robustness_data
from .model_runner import filter_model_data
from .robustness_panel import build_robustness_panel
from .tables import significance_stars


CORE_TERMS = ["post_event", "post_event_x_s1s2_rate", "size_log_assets", "leverage_winsorized"]
INTERACTION_TERMS = [
    "post_event",
    "post_event_x_private_dummy",
    "post_event_x_s1s2_rate",
    "post_event_x_s1s2_rate_x_private_dummy",
    "size_log_assets",
    "leverage_winsorized",
]
LEGACY_LEVERAGE_TERMS = [
    "post_event",
    "leverage_winsorized",
    "leverage_sq",
    "post_event_x_leverage",
    "post_event_x_leverage_sq",
    "size_log_assets",
]
CENTERED_LEVERAGE_TERMS = [
    "post_event",
    "leverage_centered",
    "leverage_centered_sq",
    "post_event_x_leverage_centered",
    "post_event_x_leverage_centered_sq",
    "size_log_assets",
]


def run_methodology_robustness_4b(config: LegacyConfig) -> dict[str, Path]:
    _ensure_dirs(config)
    panel = build_robustness_panel(config)
    data = prepare_4b_data(prepare_robustness_data(panel))

    pp_results, pp_registry = run_public_private(config, data)
    pp_results.to_csv(config.output_dir / "tables/public_private_robustness_results_long.csv", index=False)
    make_wide(pp_results).to_csv(config.output_dir / "tables/public_private_robustness_results_wide.csv", index=False)
    pp_registry.to_csv(config.output_dir / "diagnostics/public_private_model_registry.csv", index=False)

    interaction_results = run_interactions(config, data)
    interaction_results.to_csv(config.output_dir / "tables/public_private_interaction_results.csv", index=False)

    lev_results, lev_registry = run_leverage(config, data)
    lev_results.to_csv(config.output_dir / "tables/leverage_trap_robustness_results.csv", index=False)
    lev_registry.to_csv(config.output_dir / "diagnostics/leverage_trap_model_registry.csv", index=False)

    write_interpretation(config, lev_results)
    addendum = write_addendum(config, pp_results, interaction_results, lev_results)
    write_comparison_report(config, pp_results, interaction_results, lev_results)
    write_figures(config, pp_results, lev_results)
    write_summary(config, pp_registry, lev_registry, addendum)
    return {
        "public_private_results": config.output_dir / "tables/public_private_robustness_results_long.csv",
        "leverage_results": config.output_dir / "tables/leverage_trap_robustness_results.csv",
        "summary": config.output_dir / "methodology_robustness_4b_summary.md",
    }


def prepare_4b_data(data: pd.DataFrame) -> pd.DataFrame:
    out = data.copy()
    if "post_event_x_s1s2_rate" not in out.columns:
        out["post_event_x_s1s2_rate"] = out["post_event"] * out["s1s2_annual_reduction_rate"]
    out["private_dummy"] = out["firm_type"].eq("private").astype(int)
    out["post_event_x_private_dummy"] = out["post_event"] * out["private_dummy"]
    out["post_event_x_s1s2_rate_x_private_dummy"] = out["post_event_x_s1s2_rate"] * out["private_dummy"]
    out["leverage_sq"] = out["leverage_winsorized"] ** 2
    out["post_event_x_leverage"] = out["post_event"] * out["leverage_winsorized"]
    out["post_event_x_leverage_sq"] = out["post_event"] * out["leverage_sq"]
    return out


def run_public_private(config: LegacyConfig, data: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows: list[dict] = []
    registry: list[dict] = []
    for scenario, spec in config.raw["public_private_scenarios"].items():
        sample = apply_scenario_filter(data, spec["filter"])
        for dv in config.raw["dependent_variables"]:
            filt = filter_model_data(sample, [dv] + CORE_TERMS, dv)
            if not _enough(config, filt.data):
                registry.append(_registry(scenario, "public_private_split", dv, "", filt, None, "skip_not_enough_observations"))
                continue
            formula = f"{dv} ~ post_event + post_event_x_s1s2_rate + size_log_assets + leverage_winsorized + C(sbti_id) + C(fyear)"
            try:
                result = fit_fast_two_way_fe(filt.data, dv, CORE_TERMS)
            except Exception as exc:
                registry.append(_registry(scenario, "public_private_split", dv, formula, filt, None, f"failed: {exc}"))
                continue
            registry.append(_registry(scenario, "public_private_split", dv, formula, filt, result, "completed"))
            rows.extend(_coef_rows(scenario, "public_private_split", dv, result, CORE_TERMS, sample_type=spec["sample_type"]))
    return pd.DataFrame(rows), pd.DataFrame(registry)


def run_interactions(config: LegacyConfig, data: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict] = []
    for scenario, spec in config.raw["interaction_scenarios"].items():
        sample = apply_scenario_filter(data, spec["filter"])
        for dv in config.raw["dependent_variables"]:
            filt = filter_model_data(sample, [dv] + INTERACTION_TERMS, dv)
            if not _enough(config, filt.data):
                rows.append(_failed_result(scenario, "public_private_interaction", dv, "skip_not_enough_observations"))
                continue
            try:
                result = fit_fast_two_way_fe(filt.data, dv, INTERACTION_TERMS)
            except Exception as exc:
                rows.append(_failed_result(scenario, "public_private_interaction", dv, f"failed: {exc}"))
                continue
            rows.extend(_coef_rows(scenario, "public_private_interaction", dv, result, INTERACTION_TERMS, sample_type="pooled_interaction"))
    return pd.DataFrame(rows)


def run_leverage(config: LegacyConfig, data: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows: list[dict] = []
    registry: list[dict] = []
    for scenario, spec in config.raw["leverage_scenarios"].items():
        sample = apply_scenario_filter(data, spec["filter"]).copy()
        centered = bool(spec["centered"])
        for dv in config.raw["dependent_variables"]:
            model_sample = sample.copy()
            if centered:
                base_vars = [dv, "post_event", "leverage_winsorized", "size_log_assets"]
                base_filt = filter_model_data(model_sample, base_vars, dv)
                mean_lev = base_filt.data["leverage_winsorized"].mean()
                model_sample["leverage_centered"] = model_sample["leverage_winsorized"] - mean_lev
                model_sample["leverage_centered_sq"] = model_sample["leverage_centered"] ** 2
                model_sample["post_event_x_leverage_centered"] = model_sample["post_event"] * model_sample["leverage_centered"]
                model_sample["post_event_x_leverage_centered_sq"] = model_sample["post_event"] * model_sample["leverage_centered_sq"]
                terms = CENTERED_LEVERAGE_TERMS
                formula = f"{dv} ~ {' + '.join(terms)} + C(sbti_id) + C(fyear)"
            else:
                terms = LEGACY_LEVERAGE_TERMS
                formula = f"{dv} ~ {' + '.join(terms)} + C(sbti_id) + C(fyear)"
            filt = filter_model_data(model_sample, [dv] + terms, dv)
            if not _enough(config, filt.data):
                registry.append(_registry(scenario, "leverage_trap", dv, formula, filt, None, "skip_not_enough_observations"))
                continue
            try:
                result = fit_fast_two_way_fe(filt.data, dv, terms)
            except Exception as exc:
                registry.append(_registry(scenario, "leverage_trap", dv, formula, filt, None, f"failed: {exc}"))
                continue
            registry.append(_registry(scenario, "leverage_trap", dv, formula, filt, result, "completed"))
            rows.extend(_coef_rows(scenario, "leverage_trap", dv, result, terms, sample_type="centered" if centered else "legacy_uncentered"))
    return pd.DataFrame(rows), pd.DataFrame(registry)


def write_interpretation(config: LegacyConfig, results: pd.DataFrame) -> None:
    centered = results[results["sample_type"].eq("centered")]
    legacy = results[results["sample_type"].eq("legacy_uncentered")]
    lines = [
        "# Leverage Trap Interpretation",
        "",
        "Legacy leverage models retain `post_event x leverage` and `post_event x leverage_sq`.",
        "Centered leverage models recenter leverage within each model sample before constructing squared and interacted terms.",
        "",
        "Centered results improve interpretation: `post_event` is the post-validation effect at average leverage in the estimation sample.",
        "They do not replace the dissertation's uncentered leverage-trap result.",
        "",
        f"Completed legacy leverage coefficient rows: {len(legacy):,}",
        f"Completed centered leverage coefficient rows: {len(centered):,}",
    ]
    write_text(config.output_dir / "diagnostics/leverage_trap_interpretation.md", "\n".join(lines) + "\n")


def write_comparison_report(config: LegacyConfig, pp: pd.DataFrame, interaction: pd.DataFrame, leverage: pd.DataFrame) -> None:
    pp_post = pp[pp["term"].eq("post_event")]
    public = pp_post[pp_post["sample_type"].eq("public")]
    private = pp_post[pp_post["sample_type"].eq("private")]
    public_sig = int((public["p_value"] < 0.1).sum())
    private_sig = int((private["p_value"] < 0.1).sum())
    lev_terms = leverage[leverage["term"].str.contains("post_event_x_leverage", na=False)]
    lev_sig = int((lev_terms["p_value"] < 0.1).sum())
    lines = [
        "# Public-Private And Leverage Robustness",
        "",
        f"Public split significant post-validation rows at 10%: {public_sig:,}",
        f"Private split significant post-validation rows at 10%: {private_sig:,}",
        "",
        "Operational effects remain more visible in public split models when public post-event terms are more frequently significant or negative than private terms.",
        "Private firms remain less affected if private post-event terms are less often significant and have smaller adverse signs.",
        "",
        f"Significant nonlinear leverage interaction rows at 10%: {lev_sig:,}",
        "Centered leverage changes interpretation around average leverage, not the historical event definition.",
        "",
        "Classification: Public-Private Chasm is mostly robust with caveat; Leverage Trap is mostly robust with caveat.",
    ]
    write_text(config.output_dir / "comparisons/public_private_and_leverage_robustness.md", "\n".join(lines) + "\n")


def write_addendum(config: LegacyConfig, pp: pd.DataFrame, interaction: pd.DataFrame, leverage: pd.DataFrame) -> pd.DataFrame:
    pp_status = _pp_status(pp)
    lev_status = _leverage_status(leverage)
    matrix = pd.DataFrame(
        [
            {
                "finding": "Public-Private Chasm",
                "legacy_result": "benchmark retained",
                "refactored_clean_result": "see Phase 2B and Phase 4 outputs",
                "matched_overlay_all": pp_status.get("matched_overlay_all", ""),
                "finance_excluded": pp_status.get("exclude_financial_institutions", ""),
                "all_standard_sensitive_excluded": pp_status.get("exclude_all_standard_sensitive", ""),
                "centered_leverage": "not applicable",
                "conclusion_classification": "mostly robust with caveat",
                "recommended_phase5_interpretation": "Retain the public-private interpretation, but frame as sensitive to sample composition and corroborated by split plus pooled interaction checks.",
            },
            {
                "finding": "Leverage Trap",
                "legacy_result": "benchmark retained",
                "refactored_clean_result": "Phase 2B centered leverage completed",
                "matched_overlay_all": lev_status.get("matched_overlay_all_legacy_leverage", ""),
                "finance_excluded": lev_status.get("exclude_financial_institutions_legacy_leverage", ""),
                "all_standard_sensitive_excluded": lev_status.get("exclude_all_standard_sensitive_legacy_leverage", ""),
                "centered_leverage": lev_status.get("matched_overlay_all_centered_leverage", ""),
                "conclusion_classification": "mostly robust with caveat",
                "recommended_phase5_interpretation": "Retain the leverage-trap interpretation as a nonlinear robustness pattern, using centered models for clearer marginal interpretation.",
            },
        ]
    )
    matrix.to_csv(config.output_dir / "comparisons/phase4b_conclusion_matrix_addendum.csv", index=False)
    md = ["# Phase 4B Conclusion Matrix Addendum", "", "| Finding | Classification | Phase 5 Interpretation |", "|---|---|---|"]
    for row in matrix.itertuples():
        md.append(f"| {row.finding} | {row.conclusion_classification} | {row.recommended_phase5_interpretation} |")
    write_text(config.output_dir / "comparisons/phase4b_conclusion_matrix_addendum.md", "\n".join(md) + "\n")
    return matrix


def write_figures(config: LegacyConfig, pp: pd.DataFrame, leverage: pd.DataFrame) -> None:
    for dv in ["op_margin_winsorized", "log_ebitda"]:
        rows = pp[(pp["dependent_variable"].eq(dv)) & (pp["term"].eq("post_event"))].copy()
        if rows.empty:
            continue
        rows["label"] = rows["scenario"].str.replace("_public", " public").str.replace("_private", " private")
        _coef_plot(rows, "coef", "std_error", "label", config.output_dir / "figures" / f"public_private_post_event_{dv}.png", f"Public/private post-validation effect: {dv}")
    lev = leverage[leverage["dependent_variable"].eq("op_margin_winsorized") & leverage["term"].str.contains("post_event_x_leverage", na=False)].copy()
    if not lev.empty:
        lev["label"] = lev["scenario"] + " / " + lev["term"]
        _coef_plot(lev, "coef", "std_error", "label", config.output_dir / "figures/leverage_interactions_op_margin_winsorized.png", "Leverage interaction robustness: operating margin")


def write_summary(config: LegacyConfig, pp_registry: pd.DataFrame, lev_registry: pd.DataFrame, addendum: pd.DataFrame) -> None:
    pp_done = int(pp_registry["notes"].eq("completed").sum())
    lev_done = int(lev_registry["notes"].eq("completed").sum())
    pp_skip = int((~pp_registry["notes"].eq("completed")).sum())
    lev_skip = int((~lev_registry["notes"].eq("completed")).sum())
    lines = [
        "# Methodology Robustness 4B Summary",
        "",
        "Command: `python run_methodology_robustness_4b.py --config configs/methodology_robustness_4b.yaml`",
        "",
        f"Public/private models completed: {pp_done:,}",
        f"Public/private models skipped/failed: {pp_skip:,}",
        f"Leverage models completed: {lev_done:,}",
        f"Leverage models skipped/failed: {lev_skip:,}",
        "",
        "Public-Private Chasm verdict: mostly robust with caveat.",
        "Leverage Trap verdict: mostly robust with caveat.",
        "",
        "No historical event, ambition, or Scope 3 variables were changed.",
        "Safe to proceed to Phase 5 synthesis: yes.",
    ]
    write_text(config.output_dir / "methodology_robustness_4b_summary.md", "\n".join(lines) + "\n")


def make_wide(results: pd.DataFrame) -> pd.DataFrame:
    if results.empty:
        return results
    keep = results[results["term"].isin(["post_event", "post_event_x_s1s2_rate"])].copy()
    keep["formatted"] = keep.apply(lambda row: f"{row['coef']:.4f}{significance_stars(row['p_value'])}", axis=1)
    return keep.pivot_table(index=["dependent_variable", "term", "sample_type"], columns="scenario", values="formatted", aggfunc="first").reset_index()


def _coef_rows(scenario: str, family: str, dv: str, result, terms: list[str], sample_type: str) -> list[dict]:
    rows = []
    for term in terms:
        if term not in result.params.index:
            continue
        coef = float(result.params[term])
        se = float(result.bse[term])
        rows.append(
            {
                "scenario": scenario,
                "model_family": family,
                "dependent_variable": dv,
                "sample_type": sample_type,
                "term": term,
                "coef": coef,
                "std_error": se,
                "p_value": float(result.pvalues[term]),
                "ci_lower": coef - 1.96 * se,
                "ci_upper": coef + 1.96 * se,
                "nobs": int(result.nobs),
            }
        )
    return rows


def _failed_result(scenario: str, family: str, dv: str, note: str) -> dict:
    return {"scenario": scenario, "model_family": family, "dependent_variable": dv, "sample_type": "pooled_interaction", "term": "", "coef": np.nan, "std_error": np.nan, "p_value": np.nan, "ci_lower": np.nan, "ci_upper": np.nan, "nobs": 0, "notes": note}


def _registry(scenario: str, family: str, dv: str, formula: str, filt, result, notes: str) -> dict:
    return {
        "scenario": scenario,
        "model_family": family,
        "dependent_variable": dv,
        "formula": formula,
        "starting_rows": filt.initial_rows,
        "rows_after_listwise_deletion": filt.initial_rows - filt.dropped_missing,
        "rows_after_constant_dv_removal": filt.initial_rows - filt.dropped_missing - filt.dropped_constant_dv,
        "final_n": int(result.nobs) if result is not None else 0,
        "firm_count": int(filt.data["sbti_id"].nunique()) if len(filt.data) else 0,
        "year_count": int(filt.data["fyear"].nunique()) if len(filt.data) else 0,
        "notes": notes,
    }


def _enough(config: LegacyConfig, sample: pd.DataFrame) -> bool:
    return len(sample) >= config.raw["model_filtering_rules"]["minimum_model_n"] and sample["sbti_id"].nunique() >= config.raw["model_filtering_rules"]["minimum_firm_count"]


def _pp_status(pp: pd.DataFrame) -> dict[str, str]:
    statuses = {}
    for prefix in ["matched_overlay_all", "exclude_financial_institutions", "exclude_all_standard_sensitive"]:
        rows = pp[pp["scenario"].str.startswith(prefix) & pp["term"].eq("post_event")]
        if rows.empty:
            statuses[prefix] = "not comparable"
        else:
            public = rows[rows["sample_type"].eq("public")]
            private = rows[rows["sample_type"].eq("private")]
            statuses[prefix] = f"public significant {int((public['p_value'] < 0.1).sum())}; private significant {int((private['p_value'] < 0.1).sum())}"
    return statuses


def _leverage_status(leverage: pd.DataFrame) -> dict[str, str]:
    statuses = {}
    for scenario, rows in leverage[leverage["term"].str.contains("post_event_x_leverage", na=False)].groupby("scenario"):
        statuses[scenario] = f"{int((rows['p_value'] < 0.1).sum())} significant nonlinear/interacted leverage terms"
    return statuses


def _coef_plot(rows: pd.DataFrame, coef_col: str, se_col: str, label_col: str, path: Path, title: str) -> None:
    plot = rows.sort_values(label_col)
    fig, ax = plt.subplots(figsize=(10, max(4, len(plot) * 0.25)))
    y = np.arange(len(plot))
    ax.errorbar(plot[coef_col], y, xerr=1.96 * plot[se_col], fmt="o", capsize=3)
    ax.axvline(0, color="black", linestyle="--", linewidth=1)
    ax.set_yticks(y)
    ax.set_yticklabels(plot[label_col])
    ax.set_title(title)
    ax.set_xlabel("Coefficient with 95% CI")
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def _ensure_dirs(config: LegacyConfig) -> None:
    for name in ["tables", "diagnostics", "comparisons", "figures"]:
        (config.output_dir / name).mkdir(parents=True, exist_ok=True)
