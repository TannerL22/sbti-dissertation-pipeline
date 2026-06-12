from __future__ import annotations

from pathlib import Path

import pandas as pd

from .config import LegacyConfig


def _legacy_event_value(config: LegacyConfig, dv: str, term: str) -> float | None:
    path = config.root / "outputs/refactored_legacy/diagnostics/event_study_full_vs_fallback_coefficients.csv"
    if not path.exists():
        return None
    df = pd.read_csv(path)
    rows = df[
        (df["dependent_variable"] == dv)
        & (df["selected_legacy"])
        & (df["term"] == term)
    ]
    if rows.empty:
        return None
    return float(rows.iloc[0]["coef"])


def _classify(legacy: float | None, clean: float | None, legacy_p: float | None, clean_p: float | None) -> str:
    if legacy is None or clean is None:
        return "not comparable due to specification change"
    if legacy == 0 or clean == 0:
        same_direction = legacy == clean
    else:
        same_direction = (legacy > 0) == (clean > 0)
    legacy_sig = legacy_p is not None and legacy_p < 0.1
    clean_sig = clean_p is not None and clean_p < 0.1
    if same_direction and legacy_sig == clean_sig:
        return "unchanged" if abs(legacy - clean) < 0.01 else "directionally unchanged but magnitude differs"
    if same_direction:
        return "significance changed"
    return "materially changed"


def write_clean_comparison(config: LegacyConfig) -> Path:
    comparisons = config.output_subdir("comparisons")
    diagnostics = config.output_subdir("diagnostics")
    clean_event = pd.read_csv(diagnostics / "clean_event_study_coefficients.csv")
    clean_event = clean_event[clean_event["specification"] == "clean_full"]
    pretrend = pd.read_csv(diagnostics / "pretrend_tests.csv")
    leverage = pd.read_csv(config.output_dir / "tables" / "centered_leverage_results.csv")

    rows = []
    for dv in clean_event["dependent_variable"].unique():
        clean_row = clean_event[
            (clean_event["dependent_variable"] == dv) & (clean_event["term"] == "clean_event_0")
        ]
        if clean_row.empty:
            continue
        c = clean_row.iloc[0]
        legacy = _legacy_event_value(config, dv, "post_event")
        rows.append(
            {
                "dependent_variable": dv,
                "legacy_post_or_event0": legacy,
                "clean_event0": c["coef"],
                "clean_p": c["p_value"],
                "classification": _classify(legacy, c["coef"], None, c["p_value"]),
            }
        )
    comparison_df = pd.DataFrame(rows)
    comparison_df.to_csv(comparisons / "event_study_legacy_vs_clean.csv", index=False)

    lines = [
        "# Refactored-Clean vs Legacy Diagnostic Comparison",
        "",
        "This report compares robustness diagnostics against the legacy/refactored-legacy benchmark. It does not reinterpret dissertation conclusions as new causal findings.",
        "",
        "## Event-Study Comparison",
        "",
        "Clean mode uses mutually exclusive bins with `t = -1` omitted and excludes the broad `post_event` dummy. Legacy mode used overlapping event-study dummies and, for revenue growth/log revenue, a no-size fallback.",
        "",
        "| DV | Legacy post/event coefficient | Clean t=0 coefficient | Clean p-value | Classification |",
        "|---|---:|---:|---:|---|",
    ]
    for _, row in comparison_df.iterrows():
        legacy = "" if pd.isna(row["legacy_post_or_event0"]) else f"{row['legacy_post_or_event0']:.4f}"
        lines.append(
            f"| `{row['dependent_variable']}` | {legacy} | {row['clean_event0']:.4f} | {row['clean_p']:.4f} | {row['classification']} |"
        )

    lines.extend(["", "## Pretrend Summary", "", "| DV | p-value | Classification |", "|---|---:|---|"])
    for _, row in pretrend.iterrows():
        lines.append(f"| `{row['dependent_variable']}` | {row['p_value']:.4f} | {row['classification']} |")

    lines.extend(
        [
            "",
            "## Centered Leverage Robustness",
            "",
            "Centered leverage models completed as interpretability diagnostics. `post_event` is now the post-validation effect at average model-sample leverage. These models do not replace the uncentered dissertation leverage-trap estimates.",
            "",
            "| DV | Sample | Post x centered leverage | Post x centered leverage sq | Classification |",
            "|---|---|---:|---:|---|",
        ]
    )
    for dv in leverage["dependent_variable"].unique():
        for sample in leverage[leverage["dependent_variable"] == dv]["sample_name"].unique():
            sub = leverage[(leverage["dependent_variable"] == dv) & (leverage["sample_name"] == sample)]
            lin = sub[sub["term"] == "post_event:leverage_centered"]
            sq = sub[sub["term"] == "post_event:leverage_centered_sq"]
            if lin.empty or sq.empty:
                continue
            sq_coef = float(sq.iloc[0]["coef"])
            if sq.iloc[0]["p_value"] < 0.1:
                cls = "significance changed or robustness signal present"
            else:
                cls = "not materially changed"
            lines.append(
                f"| `{dv}` | {sample} | {float(lin.iloc[0]['coef']):.4f} | {sq_coef:.4f} | {cls} |"
            )

    lines.extend(
        [
            "",
            "## Finding-Level Interpretation Guardrails",
            "",
            "- Two-stage signaling vs implementation-cost narrative: clean event-study is a timing diagnostic only; it does not change the legacy pre/post main model.",
            "- Ambition shield: not re-estimated as a new headline claim in Phase 2B.",
            "- Public/private chasm: not changed in Phase 2B.",
            "- Leverage trap: centered leverage improves interpretation around average leverage but does not replace uncentered legacy estimates.",
            "- Market indifference: not changed in Phase 2B.",
            "- Temporal dynamics / implementation dip: clean bins isolate event-time periods better than legacy overlapping dummies.",
            "- Scale shock in `log_revt`: clean full-spec differs from legacy no-size fallback; classify this as full-spec vs no-size model choice plus event-study dummy correction.",
            "- Revenue growth effects: clean full-spec differs from legacy fallback; treat as robustness sensitivity, not a new causal conclusion.",
            "",
            "## Phase 3 Readiness",
            "",
            "It is safe to proceed to Phase 3 updated SBTi overlay after reviewing the event-study and pretrend diagnostics. Phase 3 should remain separate from both legacy and clean statistical modes.",
        ]
    )
    path = comparisons / "refactored_clean_vs_legacy.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path
