from __future__ import annotations

from pathlib import Path
import hashlib

import numpy as np
import pandas as pd

from .config import LegacyConfig
from .io import load_panel
from .model_runner import filter_model_data, fit_legacy_ols


def prepare_leverage_data(config: LegacyConfig) -> pd.DataFrame:
    df = load_panel(config)
    adopters = df[df["earliest_near_term_validation_date"].notna()].copy()
    adopters["sbti_id"] = adopters["sbti_id"].astype("category")
    adopters["fyear"] = adopters["fyear"].astype("category")
    adopters["private_dummy"] = (adopters["firm_type"] == "private").astype(int)
    for col in [
        "roa_winsorized",
        "op_margin_winsorized",
        "tobins_q_winsorized",
        "size_log_assets",
        "leverage_winsorized",
        "post_event",
    ]:
        if col in adopters and adopters[col].dtype != "float64":
            adopters[col] = pd.to_numeric(adopters[col], errors="coerce")
    return adopters


def _registry_row(dep_var: str, sample_name: str, formula: str, filt, result, mean_leverage: float):
    after_listwise = filt.initial_rows - filt.dropped_missing
    after_constant = after_listwise - filt.dropped_constant_dv
    return {
        "model_family": "centered_leverage",
        "dependent_variable": dep_var,
        "sample_name": sample_name,
        "formula": formula,
        "formula_hash": hashlib.sha256(formula.encode("utf-8")).hexdigest()[:16],
        "controls": "size_log_assets; leverage centered within model sample",
        "fixed_effects": "Firm & Year",
        "cluster_variable": "sbti_id",
        "starting_rows": filt.initial_rows,
        "rows_after_listwise_deletion": after_listwise,
        "rows_after_constant_dv_removal": after_constant,
        "rows_after_singleton_removal": int(result.nobs) if result is not None else 0,
        "final_n": int(result.nobs) if result is not None else 0,
        "firm_count": int(filt.data["sbti_id"].nunique()) if len(filt.data) else 0,
        "year_count": int(filt.data["fyear"].nunique()) if len(filt.data) else 0,
        "notes": f"Centered leverage robustness; model-sample leverage mean={mean_leverage:.6f}.",
        "legacy_compatible": False,
        "clean_spec": True,
    }


def run(config: LegacyConfig) -> dict[str, Path]:
    tables_dir = config.output_subdir("tables")
    diagnostics_dir = config.output_subdir("diagnostics")
    adopters = prepare_leverage_data(config)
    rows: list[dict] = []
    registry_rows: list[dict] = []
    centered_diag: list[dict] = []

    for dep_var in config.raw["dependent_variables"]["centered_leverage"]:
        samples = [("full", adopters)]
        samples.append(("public", adopters[adopters["private_dummy"] == 0].copy()))
        if dep_var != "tobins_q_winsorized":
            samples.append(("private", adopters[adopters["private_dummy"] == 1].copy()))
        for sample_name, sample_df in samples:
            variables = [dep_var, "post_event", "leverage_winsorized", "size_log_assets"]
            filt = filter_model_data(sample_df, variables, dep_var)
            if filt.data.empty:
                continue
            model_df = filt.data.copy()
            mean_lev = model_df["leverage_winsorized"].mean()
            model_df["leverage_centered"] = model_df["leverage_winsorized"] - mean_lev
            model_df["leverage_centered_sq"] = model_df["leverage_centered"] ** 2
            centered_diag.append(
                {
                    "dependent_variable": dep_var,
                    "sample_name": sample_name,
                    "mean_original_leverage": mean_lev,
                    "mean_centered_leverage": model_df["leverage_centered"].mean(),
                    "nobs": len(model_df),
                }
            )
            formula = (
                f"{dep_var} ~ post_event * leverage_centered + "
                "post_event * leverage_centered_sq + size_log_assets + C(sbti_id) + C(fyear)"
            )
            result = fit_legacy_ols(formula, model_df)
            if result is None:
                continue
            registry_rows.append(_registry_row(dep_var, sample_name, formula, filt, result, mean_lev))
            for term in [
                "post_event",
                "leverage_centered",
                "leverage_centered_sq",
                "post_event:leverage_centered",
                "post_event:leverage_centered_sq",
                "size_log_assets",
            ]:
                if term not in result.params.index:
                    continue
                rows.append(
                    {
                        "dependent_variable": dep_var,
                        "sample_name": sample_name,
                        "term": term,
                        "coef": result.params[term],
                        "std_error": result.bse[term],
                        "p_value": result.pvalues[term],
                        "nobs": int(result.nobs),
                        "rsquared_adj": result.rsquared_adj,
                    }
                )

    result_path = tables_dir / "centered_leverage_results.csv"
    pd.DataFrame(rows).to_csv(result_path, index=False)
    centered_path = diagnostics_dir / "centered_leverage_diagnostics.csv"
    pd.DataFrame(centered_diag).to_csv(centered_path, index=False)

    registry_path = diagnostics_dir / "model_registry.csv"
    if registry_path.exists():
        registry = pd.read_csv(registry_path)
        registry = pd.concat([registry, pd.DataFrame(registry_rows)], ignore_index=True)
    else:
        registry = pd.DataFrame(registry_rows)
    registry.to_csv(registry_path, index=False)

    interpretation = [
        "# Centered Leverage Robustness Interpretation",
        "",
        "Leverage is centered within each model estimation sample after listwise deletion, constant-DV firm removal, and singleton removal.",
        "",
        "With centering, `post_event` is the estimated post-validation effect at average leverage in the model sample. `post_event:leverage_centered` is the linear change in the post-event effect as leverage rises above the model-sample mean. `post_event:leverage_centered_sq` captures nonlinear curvature around average leverage.",
        "",
        "These models are robustness/interpretability diagnostics. This does not replace the dissertation's uncentered leverage-trap results.",
    ]
    interpretation_path = diagnostics_dir / "centered_leverage_interpretation.md"
    interpretation_path.write_text("\n".join(interpretation) + "\n", encoding="utf-8")
    return {
        "centered_leverage_results": result_path,
        "centered_leverage_diagnostics": centered_path,
        "centered_leverage_interpretation": interpretation_path,
    }
