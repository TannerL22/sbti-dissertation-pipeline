from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from statsmodels.iolib.summary2 import summary_col

from .config import LegacyConfig, load_config
from .io import ensure_output_dirs, load_panel
from .model_runner import (
    coefficient_rows,
    filter_model_data,
    fit_legacy_ols,
    registry_row,
)
from .model_spec import fixed_effect_controls
from .tables import registry_to_csv


def prepare_adopters(df: pd.DataFrame) -> pd.DataFrame:
    adopters = df[df["earliest_near_term_validation_date"].notna()].copy()
    adopters["sbti_id"] = adopters["sbti_id"].astype("category")
    adopters["fyear"] = adopters["fyear"].astype("category")
    adopters["post_event_x_s1s2_rate"] = (
        adopters["post_event"] * adopters["s1s2_annual_reduction_rate"]
    )
    adopters["post_event_x_s3_dummy"] = (
        adopters["post_event"] * adopters["has_s3_absolute_target"]
    )
    adopters["private_dummy"] = (adopters["firm_type"] == "private").astype(int)
    adopters["post_event_x_private"] = adopters["post_event"] * adopters["private_dummy"]
    adopters["post_event_x_s1s2_rate_x_private"] = (
        adopters["post_event_x_s1s2_rate"] * adopters["private_dummy"]
    )
    validation_year = adopters["earliest_near_term_validation_date"].dt.year
    adopters["placebo_event_year"] = validation_year - 2
    adopters["post_placebo_event"] = (
        adopters["fyear"].astype(int) >= adopters["placebo_event_year"]
    ).astype(int)
    adopters["post_placebo_event_x_s1s2_rate"] = (
        adopters["post_placebo_event"] * adopters["s1s2_annual_reduction_rate"]
    )

    if "revt" in adopters:
        adopters["log_revt"] = np.log(adopters["revt"].replace(0, np.nan))
    if "emp" in adopters:
        adopters["log_emp"] = np.log(adopters["emp"].replace(0, np.nan))
    if "ebitda" in adopters:
        positive_ebitda = adopters["ebitda"][adopters["ebitda"] > 0]
        adopters["log_ebitda"] = np.log(positive_ebitda)

    for col in ["log_revt", "log_emp", "log_ebitda", "revenue_growth_winsorized"]:
        if col in adopters:
            adopters[col] = adopters[col].replace([np.inf, -np.inf], np.nan)
    for col in [
        "roa_winsorized",
        "op_margin_winsorized",
        "revenue_growth_winsorized",
        "tobins_q_winsorized",
        "leverage_winsorized",
        "capex_intensity_winsorized",
        "rd_intensity_winsorized",
        "log_revt",
        "log_emp",
        "log_ebitda",
    ]:
        if col in adopters and adopters[col].dtype != "float64":
            adopters[col] = adopters[col].astype("float64")
    return adopters


def _fit_model(dep_var: str, model_name: str, formula: str, data: pd.DataFrame, variables: list[str]):
    filt = filter_model_data(data, variables, dep_var)
    result = fit_legacy_ols(formula, filt.data)
    return filt, result


def run(config: LegacyConfig) -> dict[str, Path]:
    ensure_output_dirs(config)
    tables_dir = config.output_subdir("tables")
    diagnostics_dir = config.output_subdir("diagnostics")

    df = load_panel(config)
    adopters = prepare_adopters(df)
    initial_count = len(adopters)

    desc_cols = [
        "roa_winsorized",
        "op_margin_winsorized",
        "revenue_growth_winsorized",
        "tobins_q_winsorized",
        "log_revt",
        "log_ebitda",
        "log_emp",
        "s1s2_annual_reduction_rate",
        "has_s3_absolute_target",
        "s3_annual_reduction_rate",
        "size_log_assets",
        "leverage_winsorized",
    ]
    existing_desc_cols = [c for c in desc_cols if c in adopters.columns]
    with pd.ExcelWriter(tables_dir / "descriptive_statistics.xlsx") as writer:
        adopters[existing_desc_cols].describe(percentiles=[0.01, 0.25, 0.5, 0.75, 0.99]).transpose().to_excel(
            writer, sheet_name="Summary_Statistics"
        )
        adopters[existing_desc_cols].corr().to_excel(writer, sheet_name="Correlation_Matrix")

    dependent_vars = [
        v for v in config.raw["dependent_variables"]["main"] if v in adopters.columns
    ]
    controls = fixed_effect_controls("size_log_assets + leverage_winsorized")
    all_tables: list[str] = []
    registry: list[dict] = []
    coefs: list[dict] = []
    attrition: dict[str, dict[str, str]] = {}

    for dep_var in dependent_vars:
        models = []
        names = []
        base_vars = [
            dep_var,
            "post_event",
            "post_event_x_s1s2_rate",
            "size_log_assets",
            "leverage_winsorized",
        ]

        specs: list[tuple[str, str, pd.DataFrame, list[str], str]] = [
            (
                "Model 1: Full Sample",
                f"{dep_var} ~ post_event + post_event_x_s1s2_rate + {controls}",
                adopters,
                base_vars,
                "size_log_assets + leverage_winsorized",
            ),
            (
                "Model 1P: Placebo",
                f"{dep_var} ~ post_placebo_event + post_placebo_event_x_s1s2_rate + {controls}",
                adopters,
                [
                    dep_var,
                    "post_placebo_event",
                    "post_placebo_event_x_s1s2_rate",
                    "size_log_assets",
                    "leverage_winsorized",
                ],
                "size_log_assets + leverage_winsorized",
            ),
            (
                "Model 2a: No S3 Target",
                f"{dep_var} ~ post_event + post_event_x_s1s2_rate + {controls}",
                adopters[adopters["has_s3_absolute_target"] == 0].copy(),
                base_vars,
                "size_log_assets + leverage_winsorized",
            ),
            (
                "Model 2b: Has S3 Target",
                f"{dep_var} ~ post_event + post_event_x_s1s2_rate + {controls}",
                adopters[adopters["has_s3_absolute_target"] == 1].copy(),
                base_vars,
                "size_log_assets + leverage_winsorized",
            ),
        ]

        s3_adopters = adopters[adopters["has_s3_absolute_target"] == 1].copy()
        s3_adopters["post_event_x_s3_rate"] = (
            s3_adopters["post_event"] * s3_adopters["s3_annual_reduction_rate"]
        )
        specs.append(
            (
                "Model 3: S3 Ambition",
                f"{dep_var} ~ post_event + post_event_x_s3_rate + {controls}",
                s3_adopters,
                [
                    dep_var,
                    "post_event",
                    "post_event_x_s3_rate",
                    "size_log_assets",
                    "leverage_winsorized",
                ],
                "size_log_assets + leverage_winsorized",
            )
        )

        if dep_var != "tobins_q_winsorized":
            specs.append(
                (
                    "Model 4: Interaction",
                    f"{dep_var} ~ post_event + post_event_x_s1s2_rate + post_event_x_private + post_event_x_s1s2_rate_x_private + {controls}",
                    adopters,
                    [
                        dep_var,
                        "post_event",
                        "post_event_x_s1s2_rate",
                        "private_dummy",
                        "post_event_x_private",
                        "post_event_x_s1s2_rate_x_private",
                        "size_log_assets",
                        "leverage_winsorized",
                    ],
                    "size_log_assets + leverage_winsorized",
                )
            )

        specs.extend(
            [
                (
                    "Model 5a: Public Sample",
                    f"{dep_var} ~ post_event + post_event_x_s1s2_rate + {controls}",
                    adopters[adopters["private_dummy"] == 0].copy(),
                    base_vars,
                    "size_log_assets + leverage_winsorized",
                ),
                (
                    "Model 5b: Private Sample",
                    f"{dep_var} ~ post_event + post_event_x_s1s2_rate + {controls}",
                    adopters[adopters["private_dummy"] == 1].copy(),
                    base_vars,
                    "size_log_assets + leverage_winsorized",
                ),
            ]
        )

        for model_name, formula, model_data, variables, controls_label in specs:
            filt, result = _fit_model(dep_var, model_name, formula, model_data, variables)
            if result is None:
                continue
            models.append(result)
            names.append(model_name)
            registry.append(
                registry_row(
                    dep_var=dep_var,
                    model_name=model_name,
                    formula=formula,
                    filter_result=filt,
                    result=result,
                    controls=controls_label,
                )
            )
            coefs.extend(coefficient_rows(dep_var, model_name, result))
            if dep_var in {"roa_winsorized", "log_revt"} and model_name == "Model 1: Full Sample":
                attrition[dep_var] = {
                    "Initial Adopter Sample (Firm-Years)": f"{initial_count:,}",
                    "Less: Missing DV or Control Variables": f"({filt.dropped_missing:,})",
                    "Subtotal": f"{initial_count - filt.dropped_missing:,}",
                    "Less: Firms with Constant DV": f"({filt.dropped_constant_dv:,})",
                    "Less: Single-observation firms (singletons)": f"({filt.dropped_singletons:,})",
                    "**Final Estimation Sample (N)**": f"**{int(result.nobs):,}**",
                }

        if models:
            summary_table = summary_col(
                results=models,
                model_names=names,
                stars=True,
                float_format="%.3f",
                regressor_order=[
                    "Intercept",
                    "post_event",
                    "post_placebo_event",
                    "post_event_x_s1s2_rate",
                    "post_placebo_event_x_s1s2_rate",
                    "post_event_x_s3_rate",
                    "post_event_x_private",
                    "post_event_x_s1s2_rate_x_private",
                    "size_log_assets",
                    "leverage_winsorized",
                ],
                info_dict={
                    "N": lambda x: f"{int(x.nobs):,}",
                    "R2 Adj.": lambda x: f"{x.rsquared_adj:.2f}",
                    "Fixed-Effects": lambda x: "Firm & Year",
                    "Std. Errors": lambda x: "Clustered (Firm)",
                },
                drop_omitted=True,
            )
            all_tables.append(f"Regression Results for Dependent Variable: {dep_var}\n{summary_table}")

    output = "--- REFACTORED LEGACY MAIN FIXED EFFECTS RESULTS ---\n\n"
    output += "\n\n==============================================================================\n\n".join(all_tables)
    (tables_dir / "regression_results_refactored.txt").write_text(output + "\n", encoding="utf-8")
    registry_to_csv(registry, diagnostics_dir / "main_model_registry.csv")
    registry_to_csv(coefs, diagnostics_dir / "main_coefficients.csv")
    pd.DataFrame(attrition).to_csv(diagnostics_dir / "main_attrition_representative.csv")
    return {
        "main_results": tables_dir / "regression_results_refactored.txt",
        "main_registry": diagnostics_dir / "main_model_registry.csv",
        "main_coefficients": diagnostics_dir / "main_coefficients.csv",
    }


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/legacy_2012_2024.yaml")
    args = parser.parse_args(argv)
    run(load_config(args.config))


if __name__ == "__main__":
    main()
