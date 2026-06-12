from __future__ import annotations

from pathlib import Path
import hashlib

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from statsmodels.iolib.summary2 import summary_col

from .config import LegacyConfig
from .io import load_panel
from .model_runner import filter_model_data, fit_legacy_ols
from .tables import registry_to_csv


CLEAN_TERMS = [
    "clean_event_pre3_or_less",
    "clean_event_pre2",
    "clean_event_0",
    "clean_event_1",
    "clean_event_2",
    "clean_event_3plus",
]
EVENT_ORDER = [
    ("clean_event_pre3_or_less", -3, "t<=-3"),
    ("clean_event_pre2", -2, "t=-2"),
    ("reference_t_minus_1", -1, "t=-1"),
    ("clean_event_0", 0, "t=0"),
    ("clean_event_1", 1, "t=1"),
    ("clean_event_2", 2, "t=2"),
    ("clean_event_3plus", 3, "t>=3"),
]


def add_clean_event_bins(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    validation_year = pd.to_numeric(out["event_year"], errors="coerce")
    if validation_year.isna().all() and "earliest_near_term_validation_date" in out:
        validation_year = pd.to_datetime(
            out["earliest_near_term_validation_date"], errors="coerce"
        ).dt.year
    out["rel_year"] = pd.to_numeric(out["fyear"], errors="coerce") - validation_year
    out["clean_event_pre3_or_less"] = (out["rel_year"] <= -3).astype(int)
    out["clean_event_pre2"] = (out["rel_year"] == -2).astype(int)
    out["reference_t_minus_1"] = (out["rel_year"] == -1).astype(int)
    out["clean_event_0"] = (out["rel_year"] == 0).astype(int)
    out["clean_event_1"] = (out["rel_year"] == 1).astype(int)
    out["clean_event_2"] = (out["rel_year"] == 2).astype(int)
    out["clean_event_3plus"] = (out["rel_year"] >= 3).astype(int)
    return out


def prepare_data(config: LegacyConfig) -> pd.DataFrame:
    df = load_panel(config)
    adopters = df[df["earliest_near_term_validation_date"].notna()].copy()
    for col in ["log_revt", "log_emp", "log_ebitda", "revenue_growth_winsorized"]:
        if col in adopters:
            adopters[col] = adopters[col].replace([np.inf, -np.inf], np.nan)
    for col in config.raw["dependent_variables"]["event_study"] + [
        "size_log_assets",
        "leverage_winsorized",
    ]:
        if col in adopters and adopters[col].dtype != "float64":
            adopters[col] = adopters[col].astype("float64")
    adopters["sbti_id"] = adopters["sbti_id"].astype("category")
    adopters["fyear"] = adopters["fyear"].astype("category")
    return add_clean_event_bins(adopters)


def clean_event_formula(dep_var: str, controls: str) -> str:
    return f"{dep_var} ~ {' + '.join(CLEAN_TERMS)} + {controls} + C(sbti_id) + C(fyear)"


def _fit_clean_model(adopters: pd.DataFrame, dep_var: str, controls: str):
    control_vars = [c.strip() for c in controls.split("+")]
    variables = [dep_var] + CLEAN_TERMS + control_vars
    filt = filter_model_data(adopters, variables, dep_var)
    formula = clean_event_formula(dep_var, controls)
    result = fit_legacy_ols(formula, filt.data)
    return filt, formula, result


def _registry_row(family: str, dep_var: str, sample: str, formula: str, filt, result, controls: str, notes: str, clean_spec: bool):
    after_listwise = filt.initial_rows - filt.dropped_missing
    after_constant = after_listwise - filt.dropped_constant_dv
    final_n = int(result.nobs) if result is not None else 0
    return {
        "model_family": family,
        "dependent_variable": dep_var,
        "sample_name": sample,
        "formula": formula,
        "formula_hash": hashlib.sha256(formula.encode("utf-8")).hexdigest()[:16],
        "controls": controls,
        "fixed_effects": "Firm & Year",
        "cluster_variable": "sbti_id",
        "starting_rows": filt.initial_rows,
        "rows_after_listwise_deletion": after_listwise,
        "rows_after_constant_dv_removal": after_constant,
        "rows_after_singleton_removal": final_n,
        "final_n": final_n,
        "firm_count": int(filt.data["sbti_id"].nunique()) if len(filt.data) else 0,
        "year_count": int(filt.data["fyear"].nunique()) if len(filt.data) else 0,
        "notes": notes,
        "legacy_compatible": False,
        "clean_spec": clean_spec,
    }


def _coef_rows(dep_var: str, specification: str, result) -> list[dict]:
    rows = []
    if result is None:
        return rows
    for term in ["Intercept"] + CLEAN_TERMS + ["size_log_assets", "leverage_winsorized"]:
        if term not in result.params.index:
            continue
        coef = result.params[term]
        se = result.bse[term]
        rows.append(
            {
                "dependent_variable": dep_var,
                "specification": specification,
                "term": term,
                "coef": coef,
                "std_error": se,
                "p_value": result.pvalues[term],
                "ci_lower": coef - 1.96 * se,
                "ci_upper": coef + 1.96 * se,
                "nobs": int(result.nobs),
                "rsquared_adj": result.rsquared_adj,
            }
        )
    return rows


def _pretrend(result) -> tuple[float, str]:
    test = result.wald_test("clean_event_pre3_or_less = 0, clean_event_pre2 = 0", scalar=True)
    p_value = float(test.pvalue)
    if p_value < 0.05:
        label = "material pre-trend concern"
    elif p_value < 0.10:
        label = "weak/preliminary pre-trend concern"
    else:
        label = "no strong pre-trend evidence"
    return p_value, label


def _plot_event_study(coefs: pd.DataFrame, dep_var: str, path: Path) -> None:
    plot_rows = []
    for term, x, label in EVENT_ORDER:
        if term == "reference_t_minus_1":
            plot_rows.append({"x": x, "label": label, "coef": 0.0, "ci_lower": 0.0, "ci_upper": 0.0})
            continue
        row = coefs[(coefs["dependent_variable"] == dep_var) & (coefs["specification"] == "clean_full") & (coefs["term"] == term)]
        if row.empty:
            continue
        r = row.iloc[0]
        plot_rows.append({"x": x, "label": label, "coef": r["coef"], "ci_lower": r["ci_lower"], "ci_upper": r["ci_upper"]})
    pdf = pd.DataFrame(plot_rows)
    fig, ax = plt.subplots(figsize=(8, 5))
    yerr = [pdf["coef"] - pdf["ci_lower"], pdf["ci_upper"] - pdf["coef"]]
    ax.errorbar(pdf["x"], pdf["coef"], yerr=yerr, fmt="o-", capsize=4)
    ax.axhline(0, color="black", linewidth=1, linestyle="--")
    ax.axvline(-1, color="gray", linewidth=1, linestyle=":", label="Reference t=-1")
    ax.set_xticks(pdf["x"])
    ax.set_xticklabels(pdf["label"])
    ax.set_title(f"Refactored-clean event study: {dep_var}")
    ax.set_xlabel("Relative year bin")
    ax.set_ylabel("Coefficient relative to t=-1")
    ax.legend()
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=160)
    plt.close(fig)


def run(config: LegacyConfig) -> dict[str, Path]:
    tables_dir = config.output_subdir("tables")
    diagnostics_dir = config.output_subdir("diagnostics")
    figures_dir = config.output_subdir("figures")
    adopters = prepare_data(config)
    diagnostic_no_size = set(config.raw["event_study"]["run_no_size_diagnostic_for"])

    models = []
    names = []
    coef_rows: list[dict] = []
    registry: list[dict] = []
    pretrend_rows: list[dict] = []

    for dep_var in config.raw["dependent_variables"]["event_study"]:
        filt, formula, result = _fit_clean_model(adopters, dep_var, "size_log_assets + leverage_winsorized")
        if result is None:
            continue
        models.append(result)
        names.append(dep_var)
        coef_rows.extend(_coef_rows(dep_var, "clean_full", result))
        registry.append(
            _registry_row(
                "clean_event_study",
                dep_var,
                "adopters_full_spec",
                formula,
                filt,
                result,
                "size_log_assets + leverage_winsorized",
                "Clean default: mutually exclusive event-time bins, t=-1 omitted, broad post_event excluded.",
                True,
            )
        )
        p_value, label = _pretrend(result)
        pretrend_rows.append(
            {
                "dependent_variable": dep_var,
                "specification": "clean_full",
                "terms_tested": "clean_event_pre3_or_less, clean_event_pre2",
                "p_value": p_value,
                "classification": label,
            }
        )
        if dep_var in diagnostic_no_size:
            nfilt, nformula, nresult = _fit_clean_model(adopters, dep_var, "leverage_winsorized")
            if nresult is not None:
                coef_rows.extend(_coef_rows(dep_var, "clean_no_size_diagnostic", nresult))
                registry.append(
                    _registry_row(
                        "clean_event_study_diagnostic",
                        dep_var,
                        "adopters_no_size_diagnostic",
                        nformula,
                        nfilt,
                        nresult,
                        "leverage_winsorized",
                        "Diagnostic only: no-size comparison because legacy dissertation-facing event-study used fallback.",
                        True,
                    )
                )

    coef_df = pd.DataFrame(coef_rows)
    registry_df = registry_to_csv(registry, diagnostics_dir / "model_registry.csv")
    coef_df.to_csv(diagnostics_dir / "clean_event_study_coefficients.csv", index=False)
    pretrend_df = pd.DataFrame(pretrend_rows)
    pretrend_df.to_csv(diagnostics_dir / "pretrend_tests.csv", index=False)
    pretrend_md = ["# Refactored-Clean Pretrend Tests", "", "| DV | p-value | Classification |", "|---|---:|---|"]
    for _, row in pretrend_df.iterrows():
        pretrend_md.append(f"| `{row['dependent_variable']}` | {row['p_value']:.4f} | {row['classification']} |")
    (diagnostics_dir / "pretrend_tests.md").write_text("\n".join(pretrend_md) + "\n", encoding="utf-8")

    summary = summary_col(
        models,
        model_names=names,
        stars=True,
        float_format="%.4f",
        regressor_order=["Intercept"] + CLEAN_TERMS + ["size_log_assets", "leverage_winsorized"],
        info_dict={
            "N": lambda x: f"{int(x.nobs):,}",
            "R-squared Adj.": lambda x: f"{x.rsquared_adj:.3f}",
            "Fixed-Effects": lambda x: "Firm & Year",
            "Std. Errors": lambda x: "Clustered (Firm)",
        },
        drop_omitted=True,
    )
    table_text = (
        "--- REFACTORED-CLEAN EVENT STUDY RESULTS ---\n\n"
        "Mutually exclusive event-time bins; omitted reference period is t=-1; broad post_event is excluded.\n"
        + "=" * 80
        + "\n\n"
        + str(summary)
        + "\n\n"
        + "=" * 80
        + "\n"
    )
    table_path = tables_dir / "clean_event_study_results.md"
    table_path.write_text(table_text, encoding="utf-8")
    coef_df[coef_df["specification"] == "clean_full"].to_csv(tables_dir / "clean_event_study_results.csv", index=False)

    for dep_var in config.raw["dependent_variables"]["event_study"]:
        _plot_event_study(coef_df, dep_var, figures_dir / f"event_study_{dep_var}.png")

    attrition_lines = [
        "# Refactored-Clean Model Attrition",
        "",
        "| Family | DV | Sample | Starting | After listwise | After constant-DV | Final N | Firms | Notes |",
        "|---|---|---|---:|---:|---:|---:|---:|---|",
    ]
    for _, row in registry_df.iterrows():
        attrition_lines.append(
            f"| {row['model_family']} | `{row['dependent_variable']}` | {row['sample_name']} | "
            f"{int(row['starting_rows']):,} | {int(row['rows_after_listwise_deletion']):,} | "
            f"{int(row['rows_after_constant_dv_removal']):,} | {int(row['final_n']):,} | "
            f"{int(row['firm_count']):,} | {row['notes']} |"
        )
    (diagnostics_dir / "model_attrition.md").write_text("\n".join(attrition_lines) + "\n", encoding="utf-8")

    return {
        "clean_event_table": table_path,
        "clean_event_coefficients": diagnostics_dir / "clean_event_study_coefficients.csv",
        "pretrend_tests": diagnostics_dir / "pretrend_tests.csv",
        "model_registry": diagnostics_dir / "model_registry.csv",
    }
