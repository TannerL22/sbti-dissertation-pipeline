from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from statsmodels.iolib.summary2 import summary_col

from .config import LegacyConfig
from .io import load_panel
from .model_runner import coefficient_rows, filter_model_data, fit_legacy_ols, registry_row
from .model_spec import event_study_formula
from .tables import registry_to_csv


EVENT_TERMS = ["pre3", "pre2", "post_event", "post1", "post2", "post3plus"]


def prepare_event_data(config: LegacyConfig) -> pd.DataFrame:
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
    return adopters


def _fit_event(adopters: pd.DataFrame, dep_var: str, controls: str):
    control_vars = [v.strip() for v in controls.split("+")]
    variables = [dep_var] + EVENT_TERMS + control_vars
    filt = filter_model_data(adopters, variables, dep_var)
    formula = event_study_formula(dep_var, controls)
    return filt, formula, fit_legacy_ols(formula, filt.data)


def run(config: LegacyConfig) -> dict[str, Path]:
    tables_dir = config.output_subdir("tables")
    diagnostics_dir = config.output_subdir("diagnostics")
    adopters = prepare_event_data(config)
    force_no_size = set(
        config.raw["legacy_event_study_compatibility_mode"]["force_no_size_fallback"]
    )

    models = []
    model_names = []
    registry: list[dict] = []
    coef_rows: list[dict] = []
    comparison_rows: list[dict] = []

    for dep_var in config.raw["dependent_variables"]["event_study"]:
        if dep_var not in adopters:
            continue

        full_filt, full_formula, full_result = _fit_event(
            adopters, dep_var, "size_log_assets + leverage_winsorized"
        )
        nosize_filt, nosize_formula, nosize_result = _fit_event(
            adopters, dep_var, "leverage_winsorized"
        )

        selected = "no_size_fallback" if dep_var in force_no_size else "full"
        filt = nosize_filt if selected == "no_size_fallback" else full_filt
        formula = nosize_formula if selected == "no_size_fallback" else full_formula
        result = nosize_result if selected == "no_size_fallback" else full_result

        if result is None:
            continue

        models.append(result)
        model_names.append(dep_var)
        registry.append(
            registry_row(
                dep_var=dep_var,
                model_name=f"legacy_event_study_{selected}",
                formula=formula,
                filter_result=filt,
                result=result,
                controls=(
                    "leverage_winsorized"
                    if selected == "no_size_fallback"
                    else "size_log_assets + leverage_winsorized"
                ),
            )
        )
        coef_rows.extend(coefficient_rows(dep_var, f"legacy_event_study_{selected}", result))

        for spec_name, spec_result in [("full", full_result), ("no_size_fallback", nosize_result)]:
            if spec_result is None:
                continue
            for term in ["Intercept"] + EVENT_TERMS + ["size_log_assets", "leverage_winsorized"]:
                comparison_rows.append(
                    {
                        "dependent_variable": dep_var,
                        "specification": spec_name,
                        "selected_legacy": spec_name == selected,
                        "term": term,
                        "coef": spec_result.params.get(term, np.nan),
                        "std_error": spec_result.bse.get(term, np.nan),
                        "p_value": spec_result.pvalues.get(term, np.nan),
                        "nobs": int(spec_result.nobs),
                        "rsquared_adj": spec_result.rsquared_adj,
                    }
                )

    summary_table = summary_col(
        results=models,
        model_names=model_names,
        stars=True,
        float_format="%.4f",
        regressor_order=[
            "Intercept",
            "pre3",
            "pre2",
            "post_event",
            "post1",
            "post2",
            "post3plus",
            "size_log_assets",
            "leverage_winsorized",
        ],
        info_dict={
            "N": lambda x: f"{int(x.nobs):,}",
            "R-squared Adj.": lambda x: f"{x.rsquared_adj:.3f}",
            "Fixed-Effects": lambda x: "Firm & Year",
            "Std. Errors": lambda x: "Clustered (Firm)",
        },
        drop_omitted=True,
    )

    note = config.raw["legacy_event_study_compatibility_mode"]["note"]
    text = (
        "--- REFACTORED LEGACY DYNAMIC EVENT STUDY REGRESSION RESULTS ---\n\n"
        "This table reproduces the dissertation-facing event-study compatibility specification.\n"
        f"{note}\n"
        "The overlapping legacy event-time dummy structure is preserved.\n"
        + "=" * 80
        + "\n\n"
        + str(summary_table)
        + "\n\n"
        + "=" * 80
        + "\n"
    )
    table_path = tables_dir / "dynamic_event_study_regression_tables_refactored.txt"
    table_path.write_text(text, encoding="utf-8")

    registry_to_csv(registry, diagnostics_dir / "event_study_model_registry.csv")
    registry_to_csv(coef_rows, diagnostics_dir / "event_study_coefficients.csv")
    registry_to_csv(comparison_rows, diagnostics_dir / "event_study_full_vs_fallback_coefficients.csv")
    return {
        "event_table": table_path,
        "event_registry": diagnostics_dir / "event_study_model_registry.csv",
        "event_coefficients": diagnostics_dir / "event_study_coefficients.csv",
        "event_comparison": diagnostics_dir / "event_study_full_vs_fallback_coefficients.csv",
    }
