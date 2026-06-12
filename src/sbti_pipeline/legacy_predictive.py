from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

from .config import LegacyConfig
from .io import load_panel
from .tables import registry_to_csv


METRICS = [
    "roa_winsorized",
    "op_margin_winsorized",
    "revenue_growth_winsorized",
    "tobins_q_winsorized",
]


def build_predictive_dataset(config: LegacyConfig) -> pd.DataFrame:
    df = load_panel(config)
    adopters = df[df["event_year"].notna()].copy()
    pre_event = adopters[adopters["fyear"] < adopters["event_year"]]
    post_event = adopters[adopters["fyear"] >= adopters["event_year"]]

    predictors_to_average = ["leverage_winsorized", "size_log_assets"]
    pre_summary = pre_event.groupby("sbti_id")[METRICS + predictors_to_average].mean().rename(
        columns=lambda c: f"{c}_pre_avg"
    )
    post_summary = post_event.groupby("sbti_id")[METRICS].mean().rename(
        columns=lambda c: f"{c}_post_avg"
    )

    static = adopters.sort_values("fyear").groupby("sbti_id").first()
    static = static[["s1s2_annual_reduction_rate", "firm_type", "sector"]].copy()
    static["private_dummy"] = (static["firm_type"] == "private").astype(int)

    logit_df = static.join(pre_summary).join(post_summary)
    for metric in METRICS:
        outcome = f"Positive_{metric.replace('_winsorized', '').upper()}_Outcome"
        pre_col = f"{metric}_pre_avg"
        post_col = f"{metric}_post_avg"
        logit_df[outcome] = np.nan
        valid = logit_df[pre_col].notna() & logit_df[post_col].notna()
        logit_df.loc[valid, outcome] = np.where(
            logit_df.loc[valid, post_col] > logit_df.loc[valid, pre_col], 1, 0
        )

    logit_df.rename(
        columns={
            "s1s2_annual_reduction_rate": "ambition_pre",
            "leverage_winsorized_pre_avg": "leverage_pre",
            "size_log_assets_pre_avg": "size_pre",
        },
        inplace=True,
    )
    logit_df["leverage_sq_pre"] = logit_df["leverage_pre"] ** 2
    strategic = [
        "Chemicals",
        "Construction and Engineering",
        "Food and Beverage Processing",
        "Textiles, Apparel, Footwear and Luxury Goods",
        "Automobiles and Components",
        "Professional Services",
        "Software and Services",
        "Banks, Diverse Financials, Insurance",
    ]
    logit_df["sector_strategic"] = logit_df["sector"].apply(
        lambda x: x if x in strategic else "Other_Sector"
    )
    return logit_df


def run(config: LegacyConfig) -> dict[str, Path]:
    tables_dir = config.output_subdir("tables")
    diagnostics_dir = config.output_subdir("diagnostics")
    logit_df = build_predictive_dataset(config)

    outcomes = [f"Positive_{m.replace('_winsorized', '').upper()}_Outcome" for m in METRICS]
    summaries: list[str] = []
    registry: list[dict] = []

    for outcome in outcomes:
        if "TOBINS_Q" in outcome:
            formula = (
                f"{outcome} ~ ambition_pre + leverage_pre + leverage_sq_pre + "
                "size_pre + C(sector_strategic)"
            )
            required = [
                outcome,
                "ambition_pre",
                "leverage_pre",
                "leverage_sq_pre",
                "size_pre",
                "sector_strategic",
            ]
        else:
            formula = (
                f"{outcome} ~ ambition_pre + private_dummy + leverage_pre + "
                "leverage_sq_pre + size_pre + C(sector_strategic)"
            )
            required = [
                outcome,
                "ambition_pre",
                "private_dummy",
                "leverage_pre",
                "leverage_sq_pre",
                "size_pre",
                "sector_strategic",
            ]

        model_df = logit_df.dropna(subset=required)
        if model_df.empty or model_df[outcome].nunique() < 2:
            continue

        model = smf.logit(formula, data=model_df)
        result = model.fit(cov_type="HC3", disp=0, maxiter=200)
        params = result.params
        pvalues = result.pvalues
        conf_int = result.conf_int()
        summary_df = pd.DataFrame(
            {
                "Odds Ratio": np.exp(params),
                "p-value": pvalues,
                "[0.025": np.exp(conf_int[0]),
                "0.975]": np.exp(conf_int[1]),
            }
        )
        clean_index = summary_df.index.str.replace(
            "C(sector_strategic)[T.", "Sector: ", regex=False
        ).str.replace("]", "", regex=False)
        clean_index = clean_index.str.replace("ambition_pre", "Ambition (Pre-Event)", regex=False)
        clean_index = clean_index.str.replace("private_dummy", "Firm Type: Private (Dummy)", regex=False)
        clean_index = clean_index.str.replace("leverage_pre", "Leverage (Pre-Event)", regex=False)
        clean_index = clean_index.str.replace(
            "leverage_sq_pre", "Leverage Squared (Pre-Event)", regex=False
        )
        clean_index = clean_index.str.replace(
            "size_pre", "Firm Size (Log Assets, Pre-Event)", regex=False
        )
        summary_df.index = clean_index
        stars = summary_df["p-value"].apply(
            lambda p: "***" if p < 0.01 else ("**" if p < 0.05 else ("*" if p < 0.1 else ""))
        )
        summary_df["Odds Ratio"] = summary_df["Odds Ratio"].round(3).astype(str) + stars
        title = f"--- Logistic Regression Results for Outcome: {outcome} ---\n"
        model_info = f"N: {int(result.nobs)}\nPseudo R-sq: {result.prsquared:.3f}\n\n"
        summaries.append(
            title
            + model_info
            + summary_df[["Odds Ratio", "p-value", "[0.025", "0.975]"]].to_string(
                float_format="%.3f"
            )
        )
        registry.append(
            {
                "outcome": outcome,
                "nobs": int(result.nobs),
                "pseudo_r2": result.prsquared,
                "formula": formula,
                "success_definition": config.raw["predictive_success_definition"],
                "legacy_leakage_note": "Outcomes use post-event averages by design; predictors are pre-event averages plus static first-observed sector/firm type/ambition.",
            }
        )

    output = (
        "--- REFACTORED LEGACY PREDICTIVE LOGIT ANALYSIS (FINAL) ---\n\n"
        "This analysis preserves the legacy success definition: post-event average greater than pre-event average.\n"
        "Odds Ratios are presented. Sector aggregation follows the dissertation script.\n\n"
    )
    for summary in summaries:
        output += summary + "\n\n======================================================================\n\n"
    path = tables_dir / "predictive_logit_results_final_refactored.txt"
    path.write_text(output, encoding="utf-8")
    registry_to_csv(registry, diagnostics_dir / "predictive_model_registry.csv")
    return {"predictive_results": path, "predictive_registry": diagnostics_dir / "predictive_model_registry.csv"}
